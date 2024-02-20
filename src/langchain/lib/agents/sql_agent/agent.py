import json

from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate, AIMessagePromptTemplate
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLCheckerTool

from ..sessions import MEMORY_KEY, get_session
from .query_tool import CustomQuerySQLDataBaseTool
from .db_list_tool import CustomListSQLDatabaseTool
from .db_info_tool import CustomInfoSQLDatabaseTool
from .query import INFO_QUERY
# from ...tools.map_interaction.set_layer_paint import SetMapLayerPaintTool
from ...tools.map_interaction.get_map_state import GetMapStateTool


# AI_SUFFIX = """I should look at the tables in the database to see what I can query.
# Then I should query the schema of the most relevant tables, before doing an SQL query to answer the user's request.
# If no relevant data is found in the database, I should use my background knowledge to give an approximate answer."""

QUERY_CHECKER = """
{query}
Double check the {dialect} query above for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins
- Using double quotes for table names
- Using correct units for the given coordinate reference system (CRS) - i.e., degrees for WGS84 and meters for UTM 

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

Output the final SQL query only.

SQL Query: """


def create_sql_agent(session_id: str = None):
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=(
                'You are a helpful GIS agent/consultant.\n'
                'Table names should be surrounded in double quotes.\n'
                # 'DO NOT waste time presenting schemas and example rows to the user.\n'
            )),
            MessagesPlaceholder(variable_name=MEMORY_KEY),
            HumanMessagePromptTemplate.from_template("{input}"),
            # AIMessage(content=AI_SUFFIX),
            AIMessagePromptTemplate.from_template('{ai_suffix}'),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    db = SQLDatabase.from_uri(
        database_uri='postgresql://postgres:postgres@localhost:5433/geogpt_db',
        sample_rows_in_table_info=1,
    )

    res = db._execute(INFO_QUERY)
    # print(res)
    result_dict = {}
    for r in res:
        table_name = r['table_name']
        result_dict[table_name] = json.dumps(r, indent=4)
        # print(json.dumps(r, indent=4))

    db._custom_table_info = result_dict

    toolkit = SQLDatabaseToolkit(db=db, llm=ChatOpenAI(temperature=0))
    context = toolkit.get_context()  # Context not currently included in prompt
    tools = [*toolkit.get_tools()]

    tools = list(filter(lambda x: x.name not in [
                 'sql_db_query',
                 'sql_db_list_tables',
                 'sql_db_schema'
                 'sql_db_query_checker'
                 ], tools))

    tools += [
        CustomQuerySQLDataBaseTool(db=db),
        CustomListSQLDatabaseTool(db=db),
        CustomInfoSQLDatabaseTool(db=db),
        QuerySQLCheckerTool(
            db=db,
            llm=ChatOpenAI(temperature=0),
            template=QUERY_CHECKER
        ),
        GetMapStateTool()
        # SetMapLayerPaintTool()
    ]

    prompt = prompt.partial(**context)

    session_id, memory = get_session(session_id)

    # llm = ChatOpenAI(model="gpt-4-1106-preview", temperature=0, streaming=True)
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, streaming=True)

    agent = create_openai_tools_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory
    )

    return session_id, agent_executor
