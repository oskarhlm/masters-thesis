from typing import Optional, Type, List

from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_community.tools.sql_database.tool import BaseSQLDatabaseTool
from langchain_core.pydantic_v1 import BaseModel, Field, root_validator
from sqlalchemy.schema import CreateTable
from sqlalchemy.types import NullType


# def get_table_info(db, table_names: Optional[List[str]] = None) -> str:
#     """Get information about specified tables.

#     Follows best practices as specified in: Rajkumar et al, 2022
#     (https://arxiv.org/abs/2204.00498)

#     If `sample_rows_in_table_info`, the specified number of sample rows will be
#     appended to each table description. This can increase performance as
#     demonstrated in the paper.
#     """
#     all_table_names = db.get_usable_table_names()
#     if table_names is not None:
#         missing_tables = set(table_names).difference(all_table_names)
#         if missing_tables:
#             raise ValueError(
#                 f"table_names {missing_tables} not found in database")
#         all_table_names = table_names

#     meta_tables = [
#         tbl
#         for tbl in db._metadata.sorted_tables
#         if tbl.name in set(all_table_names)
#         and not (db.dialect == "sqlite" and tbl.name.startswith("sqlite_"))
#     ]

#     tables = []
#     for table in meta_tables:
#         if db._custom_table_info and table.name in db._custom_table_info:
#             tables.append(db._custom_table_info[table.name])
#             continue

#         # Ignore JSON datatyped columns
#         for v in table.columns.values():
#             if type(v.type) is NullType:
#                 table._columns.remove(v)

#         # Add create table command
#         create_table = str(CreateTable(table).compile(db._engine))
#         table_info = f"{create_table.rstrip()}"
#         has_extra_info = (
#             db._indexes_in_table_info or db._sample_rows_in_table_info
#         )
#         if has_extra_info:
#             table_info += "\n\n/*"
#         if db._indexes_in_table_info:
#             table_info += f"\n{db._get_table_indexes(table)}\n"
#         if db._sample_rows_in_table_info:
#             table_info += f"\n{db._get_sample_rows(table)}\n"
#         if has_extra_info:
#             table_info += "*/"
#         tables.append(table_info)
#     tables.sort()
#     final_str = "\n\n".join(tables)
#     return final_str

class _InfoSQLDatabaseToolInput(BaseModel):
    table_names: str = Field(
        ...,
        description=(
            "A comma-separated list of the table names for which to return the schema. "
            "Example input: 'table1, table2, table3'"
        ),
    )


class CustomInfoSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting metadata about a SQL database."""

    name: str = "sql_db_schema"
    description: str = "Get the schema and sample rows for the specified SQL tables."
    args_schema: Type[BaseModel] = _InfoSQLDatabaseToolInput

    def _run(
        self,
        table_names: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Get the schema for tables in a comma-separated list."""

        return self.db.get_table_info_no_throw(
            [t.strip() for t in table_names.split(",")]
        ) + '\n\nTHIS IS FOR YOUR USE ONLY, DO NOT PRESENT ALL THIS INFORMATION TO THE HUMAN.'
