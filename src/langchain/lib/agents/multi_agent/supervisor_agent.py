from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.chains.openai_functions import create_structured_output_runnable
from enum import Enum


class Next(Enum):
    ANALYSIS = 'spatial_analysis_worker'
    MAP = 'client_map_worker'
    FINISH = 'FINISH'


def create_agent_supervisor():
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        " following workers: {members}. Given the following user request,"
        " respond with the worker to act next. Each worker will perform a"
        " task and respond with their results and status. When finished,"
        " respond with FINISH."
    )

    members = [e.value for e in Next]
    options = ["FINISH"] + members

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, who should act next?"
                " Or should we FINISH? Select one of: {options}",
            ),
        ]
    ).partial(options=options, members=", ".join(members))

    llm = ChatOpenAI(model="gpt-4-1106-preview")

    return create_structured_output_runnable(Next, llm, prompt)
