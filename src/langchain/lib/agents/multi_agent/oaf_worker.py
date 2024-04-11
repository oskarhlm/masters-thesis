import functools
import os

from langchain_openai import ChatOpenAI

from .common import agent_node, create_agent
from ...tools.oaf_tools.toolkit import OAFToolkit

SYSTEM_PROMPT = (
    "You are an agent that has access to an OGC API Features endpoint.\n"
    "Your only task is to retrieve features from the API, and you DO NOT have any ability"
    " of performing common GIS-analyses (buffering, intersection, difference, etc.).\n"
)

AI_SUFFIX = (
    "First, I should list the collections to see what I can query.\n"
    "Then I should query the schema of the most relevant collections (minimum of four),"
    " optionally creating a cql filter that should be checked for syntactical correctness,"
    " before finally performing a query to answer the user's request.\n"
    "Do not query all datasets, only those that are relevant."
)


def create_oaf_node():
    llm = ChatOpenAI(model=os.getenv('GPT3_MODEL_NAME'), streaming=True)
    base_url = os.getenv('OGC_API_FEATURES_BASE_URL')
    toolkit = OAFToolkit(llm=llm, base_url=base_url)
    tools = toolkit.get_tools()

    oaf_agent = create_agent(
        llm=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        suffix=AI_SUFFIX,
        query_from_supervisor=True
    )

    oaf_agent_node = functools.partial(
        agent_node, agent=oaf_agent)

    return oaf_agent_node
