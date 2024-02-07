from langchain_core.messages import AIMessage, SystemMessage
from langchain_community.agent_toolkits.sql.prompt import SQL_FUNCTIONS_SUFFIX
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import BaseSQLDatabaseTool, ListSQLDatabaseTool, InfoSQLDatabaseTool, QuerySQLCheckerTool
from langchain_core.tools import BaseTool

from ..tools.map_interaction.geojson_url import GeoJSONURLTool
from .sessions import MEMORY_KEY, get_session

import json


collection_query_template = """
SELECT jsonb_build_object(
    'type',     'FeatureCollection',
    'features', jsonb_agg(features.feature)
)
FROM (
  SELECT jsonb_build_object(
    'type',       'Feature',
    'id',         id,
    'geometry',   ST_AsGeoJSON(geom)::jsonb,
    'properties', to_jsonb(inputs) - 'id' - 'geom'
  ) AS feature
  FROM ({dynamic_query}) inputs) features;
"""


class CustomQuerySQLDataBaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for querying a SQL database."""

    name: str = "sql_database_query"
    description: str = """
    Input to this tool is a detailed and correct SQL query, output is a result from the database.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    The tool will return the rows  as a GeoJSON FeatureCollection. 
    """

    def _run(
        self,
        query: str,
    ) -> str:
        """Execute the query, return the results or an error message."""
        collection_query = collection_query_template.format(
            dynamic_query=query.strip(';'))
        result = self.db.run_no_throw(collection_query, include_columns=True)
        return json.loads(result.replace("'", '"').replace('None', 'null'))[0]['jsonb_build_object']


AI_SUFFIX = """I should look at the tables in the database to see what I can query.  
Then I should query the schema of the most relevant tables."""


def create_sql_agent(session_id: str = None):
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=(
                'You are a helpful GIS agent/consultant.\n'
            )),
            MessagesPlaceholder(variable_name=MEMORY_KEY),
            HumanMessagePromptTemplate.from_template("{input}"),
            # AIMessage(content=SQL_FUNCTIONS_SUFFIX),
            AIMessage(content=AI_SUFFIX),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    db = SQLDatabase.from_uri(
        'postgresql://postgres:postgres@localhost:5433/geogpt_db')

    toolkit = SQLDatabaseToolkit(db=db, llm=ChatOpenAI(temperature=0))
    context = toolkit.get_context()  # Context not currently included in prompt
    tools = [*toolkit.get_tools(), GeoJSONURLTool(),
             CustomQuerySQLDataBaseTool(db=db)]
    tools = list(filter(lambda x: x.name != 'sql_db_query', tools))
    print([tool.name for tool in tools])

    prompt = prompt.partial(**context)

    session_id, memory = get_session(session_id)

    # llm = ChatOpenAI(model="gpt-4-1106-preview", temperature=0,
    #                  streaming=True)
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0, streaming=True)

    agent = create_openai_tools_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory
    )

    return session_id, agent_executor
