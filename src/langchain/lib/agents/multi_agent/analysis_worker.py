import functools
import os

from langchain_experimental.tools import PythonREPLTool
from langchain_openai import ChatOpenAI

from .common import agent_node, create_agent, postlude


def create_analysis_node():
    llm = ChatOpenAI(model=os.getenv('GPT3_MODEL_NAME'), streaming=True)

    code_agent = (
        create_agent(
            llm=llm,
            tools=[PythonREPLTool()],
            system_prompt="You are a coding agent.",
        )
        | postlude
    )

    code_node = functools.partial(
        agent_node, agent=code_agent)

    return code_node
