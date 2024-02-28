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
from langchain_community.tools.sql_database.tool import QuerySQLCheckerTool

from .db_query_tool import CustomQuerySQLDataBaseTool
from .db_list_tool import CustomListSQLDatabaseTool
from .db_info_tool import CustomInfoSQLDatabaseTool

QUERY_CHECKER = """
{query}
Double check the {dialect} query above for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins
- Using double quotes for table names
- Using correct units for the given coordinate reference system (CRS) - i.e., degrees for WGS84 and meters for UTM 

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

Output the final SQL query only.

SQL Query: """


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
            QuerySQLCheckerTool(
                db=self.db,
                llm=ChatOpenAI(temperature=0),
                template=QUERY_CHECKER,
            ),
        ]
