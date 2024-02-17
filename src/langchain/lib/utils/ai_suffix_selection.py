from typing import List

from langchain.chains.ernie_functions import create_structured_output_chain
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor


class AISuffix(BaseModel):
    ai_suffix: str = Field(
        ..., description="The next thought of the AI agent, meant to help guide it solve the problem at hand")


def select_ai_suffix_message(agent_executor: AgentExecutor, user_query: str) -> str:
    suggested_ai_suffixes = [
        (
            "I should look at the tables in the database to see what I can query.\n"
            "Then I should query the schema of the most relevant tables, before doing an SQL query to answer the user's request.\n"
            "Before querying, I should double check that the query is correct.\n"
            "If all fails, I should use my background knowledge to give an approximate answer.",
        ),
        "I should use my background knowledge to give an approximate answer.",
    ]

    messages = agent_executor.agent.dict()['runnable']['middle'][0]['messages']
    system_message = messages[0]['content'] if messages[0]['type'] == 'system' else ''

    llm = ChatOpenAI()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                'system',
                (
                    'Based on a list of messages between a human user and an AI agent, '
                    'you will help decide a strategy for the AI agent by selecting its next "thought".\n'
                    'You will select between different strategies that are provided to you.\n\n'
                    'Here is the system message for the AI agent:\n\n"""{system_message}"""\n\n'
                    'Here is the conversation up to this point:\n\n{chat_history}\n\n'
                    'Here here are the suggested ai_suffixes for you to choose from:\n\n{available_ai_suffixes}\n\n'
                    'Prefer the database query suffix in most cases, unless it makes no sense at all.\n'
                    'If none of the suggested suffix seem fit, you may make one up yourself. Put emphasis on the last message.'
                )
            )
        ]
    )

    chain = create_structured_output_chain(AISuffix, llm, prompt)
    result = chain.invoke({
        'system_message': system_message,
        'chat_history': agent_executor.memory.chat_memory.messages + [user_query],
        'available_ai_suffixes': suggested_ai_suffixes
    })

    return result['function'].ai_suffix
