from typing import Annotated, Sequence, TypedDict
import operator
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langchain_core.messages import AIMessage
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.agents import AgentAction

from .agent_executor import create_tool_calling_executor

from ...utils.workdir_manager import WorkDirManager


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    working_directory: str
    current_files: str
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]


def prelude(state: AgentState) -> AgentState:
    written_files = WorkDirManager.list_files()
    if not written_files:
        return {**state, "current_files": "No files written."}
    else:
        formatted_files = "\n".join([f" - {f.name}" for f in written_files])
        return {
            **state,
            'working_directory': WorkDirManager.get_abs_path(),
            "current_files": "Below are files your team has written to the working directory:\n" + formatted_files,
        }


def create_agent(llm: ChatOpenAI, tools: Sequence[BaseTool], system_prompt: str, suffix: str = None):
    prompt = ChatPromptTemplate.from_messages([
        ('system', system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        *([AIMessage(content=suffix)] if suffix is not None else []),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    if len(tools) == 0:
        return (
            ChatPromptTemplate.from_template(system_prompt)
            | llm
            | StrOutputParser()
        )

    # agent = create_openai_tools_agent(llm, tools, prompt)
    # executor = AgentExecutor(agent=agent, tools=tools)

    executor = create_tool_calling_executor(
        model=llm, tools=tools, input_schema=AgentState, prompt=prompt)

    return executor


async def agent_node(state: AgentState, agent, name):
    res = await agent.ainvoke(state)
    for msg in res['messages']:
        if isinstance(msg, AIMessage):
            msg.name = name
    return {"messages": res['messages']}
