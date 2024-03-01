from typing import Annotated, Sequence, TypedDict, Union
import operator
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import AIMessage, ToolMessage
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.agents import AgentAction

import uuid

from .agent_executor import create_tool_calling_executor

from ...utils.workdir_manager import WorkDirManager


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    working_directory: str
    current_files: str
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]
    last_message_id: str | None
    agent_outcome: Union[AgentAction, AgentFinish, None]
    test: str


def prelude(state: AgentState) -> AgentState:
    written_files = WorkDirManager.list_files()
    if not written_files:
        return {
            **state,
            'working_directory': WorkDirManager.get_abs_path(),
            "current_files": "No files written."
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
        # 'messages': state['messages']
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


async def agent_node(state: AgentState, agent, name) -> AgentState:
    res = await agent.ainvoke(state)
    last_message_id = state.get("last_message_id", None)
    messages = res.get('messages', [])

    last_message_index = next((i for i, msg in enumerate(
        messages) if msg.additional_kwargs.get('message_id') == last_message_id), -1)

    new_messages = messages[last_message_index + 1:]
    for msg in new_messages:
        msg.additional_kwargs['message_id'] = str(uuid.uuid4())
        if isinstance(msg, AIMessage):
            msg.name = name
    return {
        "messages": new_messages,
        'last_message_id': new_messages[-1].additional_kwargs['message_id']
    }
