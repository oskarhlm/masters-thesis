from typing import Optional
import json
import os

from langchain.chains.ernie_functions import create_structured_output_chain
from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor


class AISuffix(BaseModel):
    ai_suffix: Optional[str] = Field(
        '', description="A thought in relation to a human message. May be empty.")


def select_ai_suffix_message(agent_executor: AgentExecutor, user_query: str) -> str:
    suggested_ai_suffixes = [
        (
            "First, I should look at the tables in the database to see what I can query.\n"
            "Then I should query the schema of the most relevant tables (and not presenting unneccessary details to the human), before doing an SQL query to answer the user's request.\n"
            "Before querying, I should double check that the query is correct.\n"
            "If all fails, I should use my background knowledge to give an approximate answer."
        ),
        "I should use my background knowledge to give an approximate answer.",
        # (
        #     "I should check the state of the client-side map, which serves as a visualization for the human."
        #     # ", and then answer the their request. I should NOT use this map for geospatial analysis."
        # ),
        "I should answer with a friendly tone.",
    ]

    messages = agent_executor.agent.dict()['runnable']['middle'][0]['messages']
    system_message = messages[0]['content'] if messages[0]['type'] == 'system' else ''

    llm = ChatOpenAI(model=os.getenv('GPT3_MODEL_NAME'))
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                'system',
                (
                    # 'Based on a list of messages between a human user and an AI agent, '
                    # 'you will help decide a strategy for the AI agent by selecting its next "thought".\n'
                    # 'You will select between different strategies that are provided to you.\n\n'
                    'You will help provide an initial thought for an AI agent to a human message.\n\n'
                    # 'Here is the system message for the AI agent:\n"""{system_message}"""\n\n'
                    # 'Here is the conversation up to this point:\n\n{chat_history}\n\n'
                    'Message from the human: "{user_query}"\n\n'
                    'Suggestions for ai_suffixes:\n{suggested_ai_suffixes}\n\n'
                    'Set the ai_suffix to an empty string if none of the suggested ones make sense as a thought in relation to the human message. '
                    'Prefer the database query suffix when geospatial analysis is required. '
                )
            )
        ]
    )

    chain = create_structured_output_chain(AISuffix, llm, prompt)
    result = chain.invoke({
        'system_message': system_message,
        'chat_history': agent_executor.memory.chat_memory.messages + [user_query],
        'user_query': user_query,
        'suggested_ai_suffixes': json.dumps(suggested_ai_suffixes, indent=4)
    })

    return result['function'].ai_suffix
