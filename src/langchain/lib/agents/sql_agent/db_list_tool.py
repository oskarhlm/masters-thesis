from typing import Optional

from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_community.tools.sql_database.tool import BaseSQLDatabaseTool

# 'table_name', pg_namespace.nspname || '.' || pg_class.relname,

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
    pg_description pd ON pg_class.oid = pd.objoid
WHERE 
    pg_class.relkind = 'r'
    AND pd.objsubid = 0;
"""


class CustomListSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting tables names."""

    name: str = "sql_db_list_tables"
    description: str = "Input is an empty string, output is a comma separated list of tables in the database."

    def _run(
        self,
        tool_input: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Get the schema for a specific table."""
        results = self.db._execute(QUERY)[0]['table_comments']
        return '\n'.join([f"{r['table_name']} ({r['comment']})" for r in results])
