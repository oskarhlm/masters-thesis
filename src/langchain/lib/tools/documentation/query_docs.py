import fnmatch
from typing import Coroutine, Optional, Type, List
import os

from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain.schema.output_parser import StrOutputParser


from .get_docs import get_documentation


SYSTEM_PROMPT = (
    "You are a helper that will respond to a question"
    " about something that can be found in documentation you are given."
    "\nIf you cannot answer the question using the documentation,"
    " you should say that say something like 'The docs for `{dataset_name}`"
    " do not contain information about what you are asking.'\n"
    "Keep your responses brief and to the point."
)


class _QueryDocsInput(BaseModel):
    dataset_name: str = Field(...,
                              description="The dataset which documentation is to be queried.")
    query: str = Field(...,
                       description="Fields etc. in the dataset that are important to the task task you a trying to solve.")


class QueryDocsTool(BaseTool):
    """Tool for querying a dataset's documentation."""

    name: str = "query_docs"
    description: str = "Use to query a dataset's documentation."
    args_schema: Type[BaseModel] = _QueryDocsInput

    def _run(self, *args, **kwargs) -> str:
        return NotImplementedError

    async def _arun(self, dataset_name: str, query: str, *args, **kwargs):
        prompt = ChatPromptTemplate.from_messages([
            ('system', SYSTEM_PROMPT),
            ('human', (
                "{docs}"
                f"{'-' * 100}\n"
                "{query}"
            ))
        ])

        # model_name = 'GPT4_MODEL_NAME'
        model_name = 'GPT3_MODEL_NAME'

        llm = ChatOpenAI(model=os.getenv(model_name))

        chain = prompt | llm | StrOutputParser()

        return await chain.ainvoke({
            'dataset_name': dataset_name,
            'docs': await get_documentation(dataset_name, query=query),
            'query': query
        })
