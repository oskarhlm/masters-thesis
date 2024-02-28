from enum import Enum
from typing import Annotated, Sequence, TypedDict,  Callable, Dict
import operator
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import HumanMessage, AIMessage, FunctionMessage, SystemMessage
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from ...utils.workdir_manager import WorkDirManager


class AgentState(TypedDict):
    initial_query: str
    messages: Annotated[Sequence[BaseMessage], operator.add]
    function_messages: Annotated[Sequence[FunctionMessage], operator.add]
    next: str
    current_files: str


def prelude(state: AgentState):
    written_files = WorkDirManager.list_files()
    if not written_files:
        return {**state, "current_files": "No files written."}
    else:
        formatted_files = "\n".join([f" - {f.name}" for f in written_files])
        return {
            **state,
            "current_files": "Below are files your team has written to the working directory:\n" + formatted_files,
        }


def create_agent(llm: ChatOpenAI, tools: Sequence[BaseTool], system_prompt: str, suffix: str = None):
    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            AIMessage(content=suffix or ''),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    if len(tools) == 0:
        return (
            ChatPromptTemplate.from_template(system_prompt)
            | llm
            | StrOutputParser()
        )

    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor


async def agent_node(state: AgentState, agent, name):
    messages = []
    function_messages = []
    async for s in agent.astream(state):
        message = s['messages'][-1]
        if isinstance(message, AIMessage) and message.content:
            message.name = name
            messages.append(message)
        elif isinstance(message, FunctionMessage):
            messages.append(message)
    return {"messages": messages, 'function_messages': function_messages}
