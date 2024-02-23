import functools
import os

from langchain_openai import ChatOpenAI
from langchain.sql_database import SQLDatabase

from .common import agent_node, create_agent
from ...tools.sql.toolkit import CustomSQLDatabaseToolkit


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
    )
    sql_agent_node = functools.partial(
        agent_node, agent=sql_agent, name="SQL Coder")

    return sql_agent_node
