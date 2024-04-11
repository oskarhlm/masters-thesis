import functools
import os

from langchain_openai import ChatOpenAI
from langchain.sql_database import SQLDatabase

from .common import agent_node, create_agent
from ...tools.sql.toolkit import CustomSQLDatabaseToolkit
from ...tools.documentation.query_docs import QueryDocsTool

SYSTEM_PROMPT = (
    "You are an SQL agent that has access to a PostGIS database.\n"
    "Do not make any assumptions about table/column names."
)

AI_SUFFIX = (
    "First, I should look at the tables in the database to see what I can query.\n"
    "Then I should query the schema of the most relevant tables (checking multiple to reduce the risk of missing the correct table, maximum 3),"
    " before doing an SQL query to answer the user's request.\n"
    "Before querying, I should check the documentation (using the `query_docs` tool) to verify that I am using the data correctly.\n"
    # "`query_docs` should be called after `sql_db_schema` (do not call the in parallel) to screen irrelevant datasets.\n"
    # "If all fails, I should use my background knowledge to give an approximate answer."
)


def create_sql_node():
    llm = ChatOpenAI(model=os.getenv('GPT3_MODEL_NAME'), streaming=True)
    db = SQLDatabase.from_uri(
        database_uri=os.getenv('POSTGRES_CONN'),
        sample_rows_in_table_info=1,
    )
    toolkit = CustomSQLDatabaseToolkit(llm=llm, db=db)
    tools = toolkit.get_tools() + [QueryDocsTool()]

    sql_agent = create_agent(
        llm=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        suffix=AI_SUFFIX
    )

    sql_agent_node = functools.partial(
        agent_node, agent=sql_agent)

    return sql_agent_node
