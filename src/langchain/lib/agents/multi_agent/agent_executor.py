import json
from typing import Sequence, Union, Any

from langchain_core.language_models import LanguageModelLike
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)

from langgraph.graph import END, StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor, ToolInvocation


def create_tool_calling_executor(
    model: LanguageModelLike,
    tools: Union[ToolExecutor, Sequence[BaseTool]],
    input_schema: Any | None = None,
    prompt: ChatPromptTemplate = None
):
    if isinstance(tools, ToolExecutor):
        tool_executor = tools
        tool_classes = tools.tools
    else:
        tool_executor = ToolExecutor(tools)
        tool_classes = tools

    model = (
        prompt
        | model.bind(tools=[convert_to_openai_tool(t) for t in tool_classes])
    )

    def should_continue(state: input_schema):
        last_message = state['agent_outcome']
        return 'tool_calls' in last_message.additional_kwargs

    def call_model(state: input_schema):
        response = model.invoke(state)
        return {"agent_outcome": response}

    async def acall_model(state: input_schema):
        response = await model.ainvoke(state)
        response.name = state['next']
        return {
            "agent_outcome": response,
            'intermediate_steps': [response]
        }

    def _get_actions(state: input_schema):
        agent_outcome = state['agent_outcome']
        return (
            [
                ToolInvocation(
                    tool=tool_call["function"]["name"],
                    tool_input=json.loads(tool_call["function"]["arguments"]),
                )
                for tool_call in agent_outcome.additional_kwargs["tool_calls"]
            ],
            [
                tool_call["id"]
                for tool_call in agent_outcome.additional_kwargs["tool_calls"]
            ],
        )

    def call_tool(state: input_schema):
        actions, ids = _get_actions(state)
        responses = tool_executor.batch(actions)
        tool_messages = [
            ToolMessage(content=str(response), tool_call_id=id)
            for response, id in zip(responses, ids)
        ]
        return {"intermediate_steps": tool_messages}

    async def acall_tool(state: input_schema):
        actions, ids = _get_actions(state)
        responses = await tool_executor.abatch(actions)
        tool_messages = [
            ToolMessage(content=str(response), tool_call_id=id)
            for response, id in zip(responses, ids)
        ]
        return {"intermediate_steps": tool_messages}

    workflow = StateGraph(input_schema)

    workflow.add_node("agent", RunnableLambda(call_model, acall_model))
    workflow.add_node("action", RunnableLambda(call_tool, acall_tool))

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            True: "action",
            False: END,
        },
    )

    workflow.add_edge("action", "agent")

    return workflow.compile()
