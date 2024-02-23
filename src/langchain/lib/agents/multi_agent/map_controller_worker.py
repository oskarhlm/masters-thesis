import functools
import os

from langchain_experimental.tools import PythonREPLTool
from langchain_openai import ChatOpenAI

from .common import agent_node, create_agent


def create_map_controller_node():
    llm = ChatOpenAI(model=os.getenv('GPT3_MODEL_NAME'))

    map_controller_agent = create_agent(
        llm=llm,
        tools=[PythonREPLTool()],
        system_prompt="You are a coding agent.",
    )
    map_controller_agent_node = functools.partial(
        agent_node, agent=map_controller_agent, name="Map Controller")

    return map_controller_agent_node
