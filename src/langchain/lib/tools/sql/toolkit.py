from pathlib import Path

from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import (
    QuerySQLCheckerTool,
)
from langchain_core.pydantic_v1 import Field
from langchain_core.language_models import BaseLanguageModel
from langchain_community.agent_toolkits.base import BaseToolkit
from typing import List
from langchain_community.tools import BaseTool

from langchain_openai import ChatOpenAI
from langchain.sql_database import SQLDatabase

from .db_query_tool import CustomQuerySQLDataBaseTool
from .db_list_tool import CustomListSQLDatabaseTool
from .db_info_tool import CustomInfoSQLDatabaseTool
from .query_checker import CustomQuerySQLCheckerTool


class CustomSQLDatabaseToolkit(BaseToolkit):
    db: SQLDatabase = Field(exclude=True)
    llm: BaseLanguageModel = Field(exclude=True)

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def get_tools(self) -> List[BaseTool]:
        return [
            CustomQuerySQLDataBaseTool(db=self.db),
            CustomListSQLDatabaseTool(db=self.db),
            CustomInfoSQLDatabaseTool(db=self.db),
            # CustomQuerySQLCheckerTool(
            #     db=self.db,
            #     llm=ChatOpenAI(temperature=0),
            # ),
        ]
