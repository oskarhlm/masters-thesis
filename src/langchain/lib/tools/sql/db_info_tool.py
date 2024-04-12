from typing import Optional, Type, List

from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_community.tools.sql_database.tool import BaseSQLDatabaseTool
from langchain_core.pydantic_v1 import BaseModel, Field
from sqlalchemy.schema import CreateTable
from sqlalchemy.types import NullType
from sqlalchemy import text


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

        table_infos = []
        for table_name in table_names:
            table = self.db._metadata.tables[table_name]

            for k, v in table.columns.items():
                if type(v.type) is NullType:
                    table._columns.remove(v)

            create_table = str(CreateTable(
                table).compile(self.db._engine))
            srid = self._get_srid(table_name)

            column_names = table.columns.keys()
            exclude_columns = ['id', 'code', 'osm_id',
                               'name', 'ref', 'layer', 'population', 'geom']
            column_distributions = self._get_column_distributions(
                table_name=table_name,
                column_names=[
                    cname for cname in column_names if not cname in exclude_columns]
            )
            distribution_string = self._create_distribution_string(
                column_distributions)

            table_infos.append(
                f'{create_table}{srid}\n\n{distribution_string}')

        return f'\n{"-" * 100}\n'.join(table_infos)

    def _get_srid(self, table_name):
        query = text(f"""SELECT auth_name, auth_srid, proj4text
                FROM spatial_ref_sys
                WHERE srid = (SELECT ST_SRID(geom) FROM public.{table_name} LIMIT 1);""")
        with self.db._engine.connect() as conn:
            result = conn.execute(query).fetchone()
            print(result)
        auth_name, auth_srid, proj4text = result
        return f"{auth_name}:{auth_srid} ({proj4text})"

    def _get_column_distributions(self, table_name: str, column_names: List[str]):
        distributions = {}
        for column_name in column_names:
            query = text(f"""
            WITH RandomSubset AS (
                SELECT {column_name}
                FROM {table_name}
                ORDER BY RANDOM() 
                LIMIT 10000
            )
            SELECT {column_name}, (COUNT(*) * 100.0) / 10000 AS percent
            FROM RandomSubset
            GROUP BY {column_name}
            ORDER BY percent DESC
            LIMIT 10;
            """)
            with self.db._engine.connect() as conn:
                results = conn.execute(query).fetchall()

            distributions[column_name] = [
                {'value': value, 'percent': round(percent, 1)} for value, percent in results]

            return distributions

    def _create_distribution_string(self, distributions):
        output_string = ''
        for column_name, distribution_data in distributions.items():
            output_string += f"Column: {column_name}\n"
            for data in distribution_data:
                output_string += f"    {data['value']}: {data['percent']}\n"
        return output_string
