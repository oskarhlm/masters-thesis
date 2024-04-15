import json
from typing import Sequence, Union, Any
from typing import Sequence, Union
from datetime import datetime
import asyncio

from langchain_core.language_models import LanguageModelLike
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor, ToolInvocation
from langchain_core.messages import ToolMessage
from langchain.tools import BaseTool

from ..utils.workdir_manager import WorkDirManager
from ..utils.map_state import load_map_state, get_map_state_modified_time


def create_tool_calling_executor(
    model: LanguageModelLike,
    tools: Union[ToolExecutor, Sequence[BaseTool]],
    input_schema: Any | None = None,
    prompt: ChatPromptTemplate = None,
    checkpointer=None
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
        raise NotImplementedError

    async def acall_model(state: input_schema):
        response = await model.ainvoke(state)
        return {
            "agent_outcome": response,
            'messages': [response]
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

    async def generate_system_messages(state):
        system_message_content = ''
        time_latest_file_added = WorkDirManager.get_latest_file_added()
        new_file_added = time_latest_file_added and (
            time_latest_file_added > state.get(
                'last_system_message_time', datetime.min)
        )
        if new_file_added:
            formatted_files = "\n".join(
                [f" - {f}" for f in WorkDirManager.list_files()])
            system_message_content += f'Files written to the working directory (`{WorkDirManager.get_abs_path()}`):\n{formatted_files}'

        if 'add_geojson_to_map' in [action.tool for action in _get_actions(state)[0]]:
            if system_message_content:
                system_message_content += '\n\n'
            for _ in range(10):
                print(get_map_state_modified_time(), state.get(
                    'last_system_message_time', datetime.min))
                if get_map_state_modified_time() > state.get('last_system_message_time', datetime.min):
                    map_state = load_map_state()
                    system_message_content += f'State of map on client:\n{json.dumps(map_state, indent=4)}'
                    break
                await asyncio.sleep(1)
            else:
                system_message_content += 'Call to `add_geojson_to-map` unsuccessful --- no update to client map.'

        return system_message_content

    def call_tool(state: input_schema):
        raise NotImplementedError

    async def acall_tool(state: input_schema):
        actions, ids = _get_actions(state)
        responses = await tool_executor.abatch(actions)
        tool_messages = [
            ToolMessage(content=str(response), tool_call_id=id)
            for response, id in zip(responses, ids)
        ]

        system_message_content = await generate_system_messages(state)
        if system_message_content:
            tool_messages.append(('system', system_message_content))
            state['last_system_message_time'] = datetime.now()

        return {
            **state,
            "messages": tool_messages
        }

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

    return workflow.compile(checkpointer=checkpointer)
