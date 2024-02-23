from typing import Sequence
import os

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser

from .common import Worker


def create_agent_supervisor_node(workers: Sequence[Worker]):
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        " following workers:\n{workers}\n\n Given the following user request,"
        " respond with the worker to act next. Each worker will perform a"
        " task and respond with their results and status. When finished,"
        " respond with FINISH."
    )

    options = ["FINISH"] + [m.value for m in workers]

    function_def = {
        "name": "route",
        "description": "Select the next role.",
        "parameters": {
            "title": "routeSchema",
            "type": "object",
            "properties": {
                "next": {
                    "title": "Next",
                    "anyOf": [
                        {"enum": options},
                    ],
                },
            },
            "required": ["next"],
        },
    }

    bullet_point_list = "\n".join(f"{i+1}) {worker.value} - {Worker.get_description(worker)}"
                                  for i, worker in enumerate(workers))

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                (
                    "Given the conversation above, who should act next, if any?"
                    ' Return "FINISH" if the initial human query ("{initial_query}") has been answered?\n\n'
                    "Select one of: {options}\n\n"
                )
            )
        ]
    ).partial(options=options, workers=bullet_point_list)

    llm = ChatOpenAI(model=os.getenv('GPT4_MODEL_NAME'), streaming=True)

    return (
        prompt
        | llm.bind_functions(functions=[function_def], function_call="route")
        | JsonOutputFunctionsParser()
    )
