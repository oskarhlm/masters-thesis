import functools
import os

from langchain_openai import ChatOpenAI
from langchain_experimental.tools.python.tool import PythonAstREPLTool

from .common import agent_node, create_agent, prelude


def create_python_analysis_node():
    llm = ChatOpenAI(model=os.getenv('GPT3_MODEL_NAME'))

    tools = [PythonAstREPLTool()]

    python_analysis_agent = prelude | create_agent(
        llm=llm,
        tools=tools,
        system_prompt=(
            'You are an analysis agent that that can perform spatial analysis'
            ' by generating and executing Python code.\n\n'
            'Save all results from analysis as GeoJSON in this folder: `{working_directory}`\n'
            '{current_files}'
        )
    )
    python_analysis_agent_node = functools.partial(
        agent_node, agent=python_analysis_agent, name="Python Coder")

    return python_analysis_agent_node
