from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.tools.requests.tool import RequestsGetTool
from langchain.requests import RequestsWrapper

from lib.tools.aof_tools.query_collection import QueryOGCAPIFeaturesCollectionTool
from ..sessions import MEMORY_KEY, get_session


AI_SUFFIX = """I should look at the collections in the data catalog to see what I can query.  
Then I should query the properties of the relevant collection (http://localhost:9000/collections/{collection_name}), 
before using CQL queries to answer the user's request."""


def create_aof_agent(session_id: str = None):
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=(
                'You are a helpful GIS agent/consultant that has access to an OGC API Features data catalog.\n'
                'You task is to help the user retrieve data from this data catalog.\n'
                'The data catalog is located at `http://localhost:9000`, and the collections are available at /collections.\n'
                'DO NOT call /items on a collection (might cause context_length_exceeded error).'
            )),
            MessagesPlaceholder(variable_name=MEMORY_KEY),
            HumanMessagePromptTemplate.from_template("{input}"),
            AIMessage(content=AI_SUFFIX),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    session_id, memory = get_session(session_id)

    llm = ChatOpenAI(model="gpt-4-0125-preview", temperature=0, streaming=True)
    # llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, streaming=True)

    tools = [RequestsGetTool(requests_wrapper=RequestsWrapper()),
             QueryOGCAPIFeaturesCollectionTool()]

    agent = create_openai_tools_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory
    )

    return session_id, agent_executor
