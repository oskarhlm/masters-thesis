import json
from typing import Sequence, Union, Any

from langchain_core.language_models import LanguageModelLike
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool

from langgraph.graph import END, StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor, ToolInvocation


def create_tool_calling_executor(
    model: LanguageModelLike,
    tools: Union[ToolExecutor, Sequence[BaseTool]],
    input_schema: Any | None = None
):
    if isinstance(tools, ToolExecutor):
        tool_executor = tools
        tool_classes = tools.tools
    else:
        tool_executor = ToolExecutor(tools)
        tool_classes = tools
    model = model.bind(tools=[convert_to_openai_tool(t) for t in tool_classes])

    def should_continue(state: input_schema):
        messages = state["messages"]
        last_message = messages[-1]
        if "tool_calls" not in last_message.additional_kwargs:
            return "end"
        else:
            return "continue"

    def call_model(state: input_schema):
        messages = state["messages"]
        response = model.invoke(messages)
        return {"messages": [response]}

    async def acall_model(state: input_schema):
        messages = state["messages"]
        response = await model.ainvoke(messages)
        return {"messages": [response]}

    def _get_actions(state: input_schema):
        messages = state["messages"]
        last_message = messages[-1]
        return (
            [
                ToolInvocation(
                    tool=tool_call["function"]["name"],
                    tool_input=json.loads(tool_call["function"]["arguments"]),
                )
                for tool_call in last_message.additional_kwargs["tool_calls"]
            ],
            [
                tool_call["id"]
                for tool_call in last_message.additional_kwargs["tool_calls"]
            ],
        )

    def call_tool(state: input_schema):
        actions, ids = _get_actions(state)
        responses = tool_executor.batch(actions)
        tool_messages = [
            ToolMessage(content=str(response), tool_call_id=id)
            for response, id in zip(responses, ids)
        ]
        return {"messages": tool_messages}

    async def acall_tool(state: input_schema):
        actions, ids = _get_actions(state)
        responses = await tool_executor.abatch(actions)
        tool_messages = [
            ToolMessage(content=str(response), tool_call_id=id)
            for response, id in zip(responses, ids)
        ]
        return {"messages": tool_messages}

    workflow = StateGraph(input_schema)

    workflow.add_node("agent", RunnableLambda(call_model, acall_model))
    workflow.add_node("action", RunnableLambda(call_tool, acall_tool))

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "action",
            "end": END,
        },
    )

    workflow.add_edge("action", "agent")

    return workflow.compile()
