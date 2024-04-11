# flake8: noqa
"""Tools for interacting with a SQL database."""
from typing import Any, Dict, Optional, Type

from langchain_core.pydantic_v1 import BaseModel, Field, root_validator

from langchain_core.language_models import BaseLanguageModel
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool

QUERY_CHECKER = """
{query}
Double check the CQL filter above for common mistakes, including:
- Using single quotation marks around strings (VERY IMPORTANT), e.g. 
        fclass='building' AND type='garage'

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

Output the final CQL filter only.

SQL Query: """


class QueryCQLCheckerInput(BaseModel):
    query: str = Field(..., description='The query to be checked/validated')


class QueryCQLCheckerTool(BaseTool):
    """Use an LLM to check if a query is correct.
    Adapted from https://www.patterns.app/blog/2023/01/18/crunchbot-sql-analyst-gpt/"""

    template: str = QUERY_CHECKER
    llm: BaseLanguageModel
    llm_chain: Any = Field(init=False)
    name: str = "cql_filter_query_checker"
    description: str = """
    Use this tool to double check if your CQL filter is correct before using it.
    Always use this tool **before** using the `query_collection` tool!
    """
    args_schema: Type[BaseModel] = QueryCQLCheckerInput

    @root_validator(pre=True)
    def initialize_llm_chain(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if "llm_chain" not in values:
            from langchain.chains.llm import LLMChain

            values["llm_chain"] = LLMChain(
                llm=values.get("llm"),
                prompt=PromptTemplate(
                    template=QUERY_CHECKER,
                    input_variables=["query"]
                ),
            )

        if values["llm_chain"].prompt.input_variables != ["query"]:
            raise ValueError(
                "LLM chain for QueryCheckerTool must have input variables ['query']"
            )

        return values

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs
    ) -> str:
        """Use the LLM to check the query."""
        raise NotImplementedError

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
        **kwargs
    ) -> str:
        return await self.llm_chain.apredict(
            query=query,
            callbacks=run_manager.get_child() if run_manager else None,
        )
