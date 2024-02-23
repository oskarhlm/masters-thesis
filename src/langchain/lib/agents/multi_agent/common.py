from enum import Enum
from typing import Annotated, Sequence, TypedDict
import operator

from langchain_core.messages import BaseMessage
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import HumanMessage
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser


class Worker(Enum):
    ANALYSIS = 'analysis_worker'
    MAP = 'map_worker'

    @classmethod
    def get_description(cls, worker: 'Worker'):
        return {
            Worker.ANALYSIS.value: (
                'A worker/agent that can perform geospatial analyses'
                ' using Python code and other geospatial tooling'
            ),
            Worker.MAP.value: (
                'A worker/agent that controls a client-side map'
                ' that is visible to the user/human'
            )
        }.get(worker.value)


class AgentState(TypedDict):
    initial_query: str
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: Worker


def create_agent(llm: ChatOpenAI, tools: Sequence[BaseTool], system_prompt: str):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
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
    result = await agent.ainvoke(state)
    return {"messages": [HumanMessage(content=result['output'], name=name)]}
