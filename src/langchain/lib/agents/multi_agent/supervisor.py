from typing import Sequence
import os

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableAssign

from .worker import Worker


def create_agent_supervisor_node(workers: Sequence[Worker], system_prompt: str = None):
    if not system_prompt:
        system_prompt = (
            "You are a supervisor tasked with managing a conversation between the"
            " following workers:\n{workers}\n\nGiven the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " actions in the background and return their response to the main conversation.\n"
            "Remember to add any geospatial data retrieved to the map using `map_controller`."
            ' When the user\'s question has been answered, respond with "FINISH".'
        )

    options = ["FINISH"] + [m.readable_name for m in workers]

    function_def = {
        "name": "route",
        "description": "Select the next role.",
        "parameters": {
            "title": "routeSchema",
            "type": "object",
            "properties": {
                "next": {
                    'type': 'string',
                    'enum': options
                },
                "worker_query": {
                    'type': 'string',
                    "description": "A description of what subtask the worker is expected do or and return to you, the supervisor."
                },
            },
            "required": ["next"],
        },
    }

    bullet_point_list = "\n".join(f"{i+1}) {worker.readable_name} - {worker.description}"
                                  for i, worker in enumerate(workers))

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                (
                    "Given the conversation above, who should act next, if any?"
                    ' Return "FINISH" if the initial user question has been answered.\n\n'
                    "Select one of: {options}\n\n"
                )
            )
        ]
    ).partial(options=options, workers=bullet_point_list)

    llm = ChatOpenAI(model=os.getenv('GPT4_MODEL_NAME'), streaming=True)
    # llm = ChatOpenAI(model=os.getenv('GPT3_MODEL_NAME'), streaming=True)

    return (
        prompt
        | llm.bind_tools(
            tools=[convert_to_openai_tool(function_def)],
            tool_choice={'type': 'function', 'function': {'name': 'route'}}
        )
        | JsonOutputToolsParser()
        | RunnableLambda(lambda x: x[0]['args'])
    )
