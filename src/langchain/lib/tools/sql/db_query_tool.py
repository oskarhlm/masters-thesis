import json
import os
from typing import Type
from pathlib import Path

from langchain_community.tools.sql_database.tool import BaseSQLDatabaseTool
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
from sqlalchemy.exc import SQLAlchemyError

from ...utils.token_limit import get_context_window_percentage
from ...utils.workdir_manager import WorkDirManager


collection_query_template = """
SELECT jsonb_build_object(
    'type', 'FeatureCollection',
    'features', COALESCE(jsonb_agg(features.feature), '[]'::jsonb)
)
FROM (
  SELECT jsonb_build_object(
    'type', 'Feature',
    'geometry', ST_AsGeoJSON(ST_Transform(geom, 4326))::jsonb,
    'properties', to_jsonb(inputs) - 'id' - 'geom'
  ) AS feature
  FROM ({dynamic_query}) inputs
) features;
"""


class CustomQuerySQLDataBaseInput(BaseModel):
    query: str = Field(..., description='SQL query to be executed.')
    layer_name: str = Field(...,
                            description='A descriptive name for the result data. Should be snake_case.')


class CustomQuerySQLDataBaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for querying a SQL database."""

    name: str = "sql_db_query"
    args_schema: Type[BaseModel] = CustomQuerySQLDataBaseInput
    description: str = """
    Input to this tool is a detailed and correct SQL query.
    The result will be stored in a working directory on the server.
    If the query is incorrect, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    Input data is in WGS84 (which uses lat/lon). Keep this in mind when querying with metric units.
    """

    def _run(
        self,
        query: str,
        layer_name: str
    ) -> str:
        """Execute the query, return the results or an error message."""
        try:
            result = self.db._execute(query)

            if len(result) and 'geom' not in result[0].keys():
                if (percentage := get_context_window_percentage(
                        str(result), os.getenv('GPT3_MODEL_NAME'))) > 0.5:
                    raise ValueError(
                        (
                            f'The query result is probably too big in relation to your context window ({round(percentage*100)}%).\n'
                            'Here is a preview of the result:\n\n'
                            f'{str(result)[:1000]}'
                        ))

                return result
        except SQLAlchemyError as e:
            """Format the error message"""
            return f"Error: {e}"
        except ValueError as e:
            return str(e)

        collection_query = collection_query_template.format(
            dynamic_query=query.strip(';'))

        try:
            result = self.db._execute(collection_query)
        except SQLAlchemyError as e:
            """Format the error message"""
            return f"Error: {e}"

        try:
            feature_collection = result[0]['jsonb_build_object']
            if len(feature_collection['features']) == 0:
                raise ValueError("No features found in the result.")

            filename = f'{layer_name}.geojson'
            WorkDirManager.add_file(
                filename, feature_collection, save_as_json=True)

            num_features = len(feature_collection['features'])

            return f"Query returned {num_features} feature{'s' if num_features > 0 else ''}."

        except json.JSONDecodeError as e:
            return f"Error parsing JSON result: {str(e)}"
        except ValueError as e:
            return str(e)
