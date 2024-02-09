import json
import os

from langchain_community.tools.sql_database.tool import BaseSQLDatabaseTool
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
from typing import Type


collection_query_template = """
SELECT jsonb_build_object(
    'type',     'FeatureCollection',
    'features', jsonb_agg(features.feature)
)
FROM (
  SELECT jsonb_build_object(
    'type',       'Feature',
    'id',         id,
    'geometry',   ST_AsGeoJSON(ST_Transform(geom, 4326))::jsonb,
    'properties', to_jsonb(inputs) - 'id' - 'geom'
  ) AS feature
  FROM ({dynamic_query}) inputs) features;
"""


class CustomQuerySQLDataBaseInput(BaseModel):
    query: str
    return_geojson: bool = Field(
        ..., description='`True` if the query uses the geometry column (`geom`)')


class CustomQuerySQLDataBaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for querying a SQL database."""

    name: str = "sql_db_query"
    args_schema: Type[BaseModel] = CustomQuerySQLDataBaseInput
    description: str = """
    Input to this tool is a detailed and correct SQL query, output is a path to a file storing the results.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    The result will be a GeoJSON FeatureCollection that will be displayed in a map automatically. 
    """

    def _run(
        self,
        query: str,
        return_geojson: bool
    ) -> str:
        """Execute the query, return the results or an error message."""
        if not return_geojson:
            return self.db.run_no_throw(query)

        collection_query = collection_query_template.format(
            dynamic_query=query.strip(';'))
        result = self.db.run_no_throw(collection_query, include_columns=True)
        result = result.replace("'", '"').replace('None', 'null')

        try:
            json_result = json.loads(result)[0]['jsonb_build_object']
            path = 'output.json'
            output_directory = os.getcwd()
            path = os.path.join(output_directory, 'output.geojson')
            with open(path, 'w') as file:
                json.dump(json_result, file)

            return {
                'path': path,
                'num_features': len(json_result['features'])
                # 'geojson': json_result  # TODO: Compress this to avoid context window issues
            }

        except:
            return result