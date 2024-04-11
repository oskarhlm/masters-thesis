from langchain_core.pydantic_v1 import Field
from langchain_core.language_models import BaseLanguageModel
from langchain_community.agent_toolkits.base import BaseToolkit
from typing import List
from langchain_community.tools import BaseTool

from .collection_info_tool import InfoOGCAPIFeaturesCollectionsTool
from .collection_list_tool import ListOGCAPIFeaturesCollectionsTool
from .query_collection import QueryOGCAPIFeaturesCollectionTool
from .query_checker import QueryCQLCheckerTool


class OAFToolkit(BaseToolkit):
    base_url: str = Field(exclude=True)
    llm: BaseLanguageModel = Field(exclude=True)

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    def get_tools(self) -> List[BaseTool]:
        return [
            InfoOGCAPIFeaturesCollectionsTool(base_url=self.base_url),
            ListOGCAPIFeaturesCollectionsTool(base_url=self.base_url),
            QueryOGCAPIFeaturesCollectionTool(base_url=self.base_url),
            # QueryCQLCheckerTool(llm=self.llm)
        ]
