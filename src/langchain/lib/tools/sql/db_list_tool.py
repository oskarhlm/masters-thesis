from typing import Optional

from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_community.tools.sql_database.tool import BaseSQLDatabaseTool

QUERY = """
SELECT 
    json_agg(json_build_object(
        'table_name', pg_class.relname,
        'comment', pd.description
    )) AS table_comments
FROM 
    pg_class
JOIN 
    pg_namespace ON pg_class.relnamespace = pg_namespace.oid
LEFT JOIN 
    pg_description pd ON pg_class.oid = pd.objoid AND pd.objsubid = 0
JOIN 
    information_schema.columns ON pg_class.relname = information_schema.columns.table_name 
    AND pg_namespace.nspname = information_schema.columns.table_schema
WHERE 
    pg_class.relkind = 'r'
    AND information_schema.columns.column_name = 'geom';
"""


class CustomListSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting tables names."""

    name: str = "sql_db_list_tables"
    description: str = "Input is an empty string, output is a comma separated list of tables in the database."

    def _run(
        self,
        tool_input: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs
    ) -> str:
        """Get the schema for a specific table."""
        results = self.db._execute(QUERY)[0]['table_comments']

        table_descriptions = []
        for table in results:
            desc = f"`{table['table_name']}`"
            if (comment := table['comment']):
                desc += f' -- {comment}'
            table_descriptions.append(desc)

        return '\n'.join(table_descriptions)
