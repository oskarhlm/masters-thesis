from typing import Optional, Type, List

from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_community.tools.sql_database.tool import BaseSQLDatabaseTool
from langchain_core.pydantic_v1 import BaseModel, Field


class _InfoSQLDatabaseToolInput(BaseModel):
    table_names: List[str] = Field(
        ...,
        description=(
            "A list of the table names for which to return the schema."
        ),
    )


class CustomInfoSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting metadata about a SQL database."""

    name: str = "sql_db_schema"
    description: str = "Get the schema and sample rows for the specified SQL tables."
    args_schema: Type[BaseModel] = _InfoSQLDatabaseToolInput

    def _run(
        self,
        table_names: List[str],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Get the schema for tables in a comma-separated list."""

        return self.db.get_table_info_no_throw(
            [t.strip() for t in table_names]
        ) + '\n\nTHIS IS FOR YOUR USE ONLY, DO NOT PRESENT ALL THIS INFORMATION TO THE HUMAN.'
