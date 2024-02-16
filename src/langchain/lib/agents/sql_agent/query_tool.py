import json
import os
from typing import Type

from langchain_community.tools.sql_database.tool import BaseSQLDatabaseTool
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
from sqlalchemy.exc import SQLAlchemyError


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
    query: str = Field(..., description=(
        'SQL query. NEVER perform conversion to GeoJSON; this is handled by the function automatically. '
        'If show_in_map == True, select all columns.'
    ))
    # return_geojson: bool = Field(
    #     ..., description='Should be `True` if the the query is expected to include geometries.')
    # show_in_map: bool = Field(
    #     ..., description=(
    #         'Should be `True` if the the query is expected to include geometries, '
    #         'or if the user needs to see the result in the map. Default to True.'
    #     )
    # )
    layer_name: str = Field(...,
                            description='Name of the layer that\'s created from the query')


class CustomQuerySQLDataBaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for querying a SQL database."""

    name: str = "sql_db_query"
    args_schema: Type[BaseModel] = CustomQuerySQLDataBaseInput
    description: str = """
    Input to this tool is a detailed and correct SQL query, output is a path to a file storing the results.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    If no database table seems to contain the information you need, just answer using you background knowledge.
    The result will be a GeoJSON FeatureCollection that will be displayed to the user in a map.
    `return_geojson` should be true if the selected are expected to have geometries. 
    """

    def _run(
        self,
        query: str,
        # show_in_map: bool,
        layer_name: str
    ) -> str:
        """Execute the query, return the results or an error message."""
        try:
            result = self.db._execute(query)
            if len(result) and 'geom' not in result[0].keys():
                return result
        except SQLAlchemyError as e:
            """Format the error message"""
            return f"Error: {e}"

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

            output_path = os.path.join(os.getcwd(), 'output.geojson')
            with open(output_path, 'w') as file:
                json.dump(feature_collection, file)

            return {
                'path': output_path,
                'num_features': len(feature_collection['features']),
                'layer_name': layer_name
            }
        except json.JSONDecodeError as e:
            return f"Error parsing JSON result: {str(e)}"
        except ValueError as e:
            return str(e)
