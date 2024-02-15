from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase

from ..sessions import MEMORY_KEY, get_session
from .query_tool import CustomQuerySQLDataBaseTool


AI_SUFFIX = """I should look at the tables in the database to see what I can query.  
Then I should query the schema of the most relevant tables, before doing an SQL query to answer the user's request."""


def create_sql_agent(session_id: str = None):
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=(
                'You are a helpful GIS agent/consultant.\n'
                'Table names should be surrounded in double quotes.\n'
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
