import functools
import os

from langchain_openai import ChatOpenAI
from langchain.sql_database import SQLDatabase

from .common import agent_node, create_agent
from ...tools.sql.toolkit import CustomSQLDatabaseToolkit

AI_SUFFIX = (
    "First, I should look at the tables in the database to see what I can query.\n"
    "Then I should query the schema of the most relevant tables (and not presenting unneccessary details to the human), before doing an SQL query to answer the user's request.\n"
    "Before querying, I should double check that the query is correct.\n"
    "If all fails, I should use my background knowledge to give an approximate answer."
)


def create_sql_node():
    llm = ChatOpenAI(model=os.getenv('GPT3_MODEL_NAME'))
    db = SQLDatabase.from_uri(
        database_uri=os.getenv('POSTGRES_CONN'),
        sample_rows_in_table_info=1,
    )
    toolkit = CustomSQLDatabaseToolkit(llm=llm, db=db)
    tools = toolkit.get_tools()

    sql_agent = create_agent(
        llm=llm,
        tools=tools,
        system_prompt="You are an SQL agent that has access to a PostGIS database.",
        suffix=AI_SUFFIX
    )
    sql_agent_node = functools.partial(
        agent_node, agent=sql_agent, name="SQL Coder")

    return sql_agent_node
