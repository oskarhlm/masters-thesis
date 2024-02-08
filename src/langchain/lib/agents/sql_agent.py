from langchain_core.messages import AIMessage, SystemMessage
from langchain_community.agent_toolkits.sql.prompt import SQL_FUNCTIONS_SUFFIX
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import BaseSQLDatabaseTool, ListSQLDatabaseTool, InfoSQLDatabaseTool, QuerySQLCheckerTool
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
from typing import Type

from .sessions import MEMORY_KEY, get_session

import json
import os


collection_query_template = """
SELECT jsonb_build_object(
    'type',     'FeatureCollection',
    'features', jsonb_agg(features.feature)
)
FROM (
  SELECT jsonb_build_object(
    'type',       'Feature',
    'id',         id,
    'geometry',   ST_AsGeoJSON(ST_Transform(geom, 4326))::jsonb,
    'properties', to_jsonb(inputs) - 'id' - 'geom'
  ) AS feature
  FROM ({dynamic_query}) inputs) features;
"""


class CustomQuerySQLDataBaseInput(BaseModel):
    query: str
    return_geojson: bool = Field(
        ..., description='`True` if the query uses the geometry column (`geom`)')


class CustomQuerySQLDataBaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for querying a SQL database."""

    name: str = "sql_db_query"
    args_schema: Type[BaseModel] = CustomQuerySQLDataBaseInput
    description: str = """
    Input to this tool is a detailed and correct SQL query, output is a path to a file storing the results.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    The result will be a GeoJSON FeatureCollection that will be displayed in a map automatically. 
    """

    def _run(
        self,
        query: str,
        return_geojson: bool
    ) -> str:
        """Execute the query, return the results or an error message."""
        if not return_geojson:
            return self.db.run_no_throw(query)

        collection_query = collection_query_template.format(
            dynamic_query=query.strip(';'))
        result = self.db.run_no_throw(collection_query, include_columns=True)
        result = result.replace("'", '"').replace('None', 'null')

        try:
            json_result = json.loads(result)[0]['jsonb_build_object']
            path = 'output.json'
            output_directory = os.getcwd()
            path = os.path.join(output_directory, 'output.geojson')
            with open(path, 'w') as file:
                json.dump(json_result, file)

            return {
                'path': path,
                'num_features': len(json_result['features'])
                # 'geojson': json_result  # TODO: Compress this to avoid context window issues
            }

        except:
            return result


AI_SUFFIX = """I should look at the tables in the database to see what I can query.  
Then I should query the schema of the most relevant tables, before doing an SQL query to answer the user's request."""


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
    tools = [*toolkit.get_tools()]
    tools = list(filter(lambda x: x.name != 'sql_db_query', tools))
    tools.append(CustomQuerySQLDataBaseTool(db=db))
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
