# import json
# import os

# from langchain_community.tools.sql_database.tool import BaseSQLDatabaseTool
# from langchain_core.tools import BaseTool
# from pydantic import Field, BaseModel
# from typing import Type


# collection_query_template = """
# SELECT jsonb_build_object(
#     'type',     'FeatureCollection',
#     'features', jsonb_agg(features.feature)
# )
# FROM (
#   SELECT jsonb_build_object(
#     'type',       'Feature',
#     'id',         id,
#     'geometry',   ST_AsGeoJSON(ST_Transform(geom, 4326))::jsonb,
#     'properties', to_jsonb(inputs) - 'id' - 'geom'
#   ) AS feature
#   FROM ({dynamic_query}) inputs) features;
# """


# class CustomQuerySQLDataBaseInput(BaseModel):
#     query: str
#     return_geojson: bool = Field(
#         ..., description='`True` if the query uses the geometry column (`geom`)')


# class CustomQuerySQLDataBaseTool(BaseSQLDatabaseTool, BaseTool):
#     """Tool for querying a SQL database."""

#     name: str = "sql_db_query"
#     args_schema: Type[BaseModel] = CustomQuerySQLDataBaseInput
#     description: str = """
#     Input to this tool is a detailed and correct SQL query, output is a path to a file storing the results.
#     If the query is not correct, an error message will be returned.
#     If an error is returned, rewrite the query, check the query, and try again.
#     The result will be a GeoJSON FeatureCollection that will be displayed in a map automatically.
#     """

#     def _run(
#         self,
#         query: str,
#         return_geojson: bool
#     ) -> str:
#         """Execute the query, return the results or an error message."""
#         if not return_geojson:
#             return self.db.run_no_throw(query)

#         collection_query = collection_query_template.format(
#             dynamic_query=query.strip(';'))
#         result = self.db.run_no_throw(collection_query, include_columns=True)
#         result = result.replace("'", '"').replace('None', 'null')

#         try:
#             json_result = json.loads(result)[0]['jsonb_build_object']
#             path = 'output.json'
#             output_directory = os.getcwd()
#             path = os.path.join(output_directory, 'output.geojson')
#             with open(path, 'w') as file:
#                 json.dump(json_result, file)

#             return {
#                 'path': path,
#                 'num_features': len(json_result['features'])
#                 # 'geojson': json_result  # TODO: Compress this to avoid context window issues
#             }

#         except:
#             return result


import json
from typing import Any, Coroutine
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
from pydantic import BaseModel, Field
import os
import httpx


class OGCAPIFeaturesDescriptionInput(BaseModel):
    """Input for GetOGCAPIFeaturesDescriptionTool."""
    url: str = Field(..., description="The URL of the API endpoint")


class OGCAPIFeaturesDescriptionTool(BaseTool):
    """Tool"""

    name: str = "ogc_api_features_schema_description"
    args_schema: Type[BaseModel] = OGCAPIFeaturesDescriptionInput
    description: str = "Use this tool to get information about an OGC API Features endpoint."

    def _run(self, url: str, *args: Any, **kwargs: Any) -> Any:
        res = requests.get(url)
        raw_spec = res.json()
        relevant_endpoints = [
            {path: docs} for path, docs in raw_spec.get('paths').items()
            if '/collection' in path
        ]

        return json.dumps(relevant_endpoints)

    def _arun(self, *args: Any, **kwargs: Any) -> Coroutine[Any, Any, Any]:
        raise NotImplementedError


class QueryOGCAPIFeaturesCollectionInput(BaseModel):
    """Input for GetOGCAPIFeaturesDescriptionTool."""
    collection_url: str = Field(
        ..., description="The URL for the collection items, i.e., http://{BASE_URL}/collections/{collection_id}")
    cql: str = Field(..., description=("CQL (common query language) to be used for filtering like:\n"
                                       "'http://{BASE_URL}/collections/{collection_id}/items?filter=< cql goes here >"))


class QueryOGCAPIFeaturesCollectionTool(BaseTool):
    """Tool"""

    name: str = "ogc_features_cql_filtering"
    args_schema: Type[BaseModel] = QueryOGCAPIFeaturesCollectionInput
    description: str = (
        "Use this tool to retrieve specific items from an OGC API Features collection.\n"
        "Use CQL (Common Query Language) to filter the returned items.\n"
        "The items will be stored in a file, the path of which will be returned to you."
    )

    def _run(self, collection_url: str, cql: str, *args: Any, **kwargs: Any) -> Any:
        url = f'{collection_url}/items?filter={cql}'
        try:
            res = requests.get(url)
            path = 'output.json'
            output_directory = os.getcwd()
            path = os.path.join(output_directory, 'output.geojson')
            with open(path, 'w') as file:
                json.dump(res, file)

            return {
                'path': path,
                'num_features': len(res['features'])
            }
        except requests.RequestException as e:
            return {'error': str(e)}

    async def _arun(self, collection_url: str, cql: str, *args: Any, **kwargs: Any) -> Any:
        url = f'{collection_url}/items?filter={cql}&limit=5000'
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url)
                path = 'output.geojson'
                output_directory = os.getcwd()
                path = os.path.join(output_directory, path)
                with open(path, 'w') as file:
                    json.dump(res.json(), file)

                return {
                    'path': path,
                    'num_features': len(res.json().get('features', []))
                }
        except httpx.RequestError as e:
            return {'error': str(e)}
