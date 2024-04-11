from typing import Annotated, Sequence, TypedDict, Union
import operator
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from .agent_executor import create_tool_calling_executor

from ...utils.workdir_manager import WorkDirManager


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    worker_query: str
    working_directory: str
    current_files: str
    agent_outcome: Union[AIMessage, None]
    intermediate_steps: Annotated[Sequence[ToolMessage], operator.add]


def prelude(state: AgentState) -> AgentState:
    written_files = WorkDirManager.list_files()
    if not written_files:
        return {
            **state,
            'working_directory': WorkDirManager.get_abs_path(),
            "current_files": "No files written.",
            'agent_outcome': None,
            'intermediate_steps': []
        }
    else:
        formatted_files = "\n".join(
            [f" - {f}" for f in written_files])
        return {
            **state,
            'working_directory': WorkDirManager.get_abs_path(),
            "current_files": "Below are files your team has written to the working directory:\n" + formatted_files,
            'intermediate_steps': []
        }


def postlude(state: AgentState) -> AgentState:
    return {
        **state,
        'messages': [state['agent_outcome']],
    }


def create_agent(llm: ChatOpenAI, tools: Sequence[BaseTool],
                 system_prompt: str, suffix: str = None, query_from_supervisor=False):
    if len(tools) == 0:
        return (
            ChatPromptTemplate.from_template(system_prompt)
            | llm
            | StrOutputParser()
        )

    prompt = ChatPromptTemplate.from_messages([
        ('system', system_prompt),
        *(MessagesPlaceholder(variable_name="messages")
          if not query_from_supervisor else [('human', '{worker_query}')]),
        *([AIMessage(content=suffix)] if suffix is not None else []),
        MessagesPlaceholder(variable_name="intermediate_steps")
    ])

    executor = create_tool_calling_executor(
        model=llm, tools=tools, input_schema=AgentState, prompt=prompt)

    return executor


async def agent_node(state: AgentState, agent) -> AgentState:
    agent_outcome = await (
        prelude
        | agent
        | postlude
    ).ainvoke(state)
    return agent_outcome
