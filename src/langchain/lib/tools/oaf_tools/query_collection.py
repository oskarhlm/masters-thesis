import json
from typing import Dict, Any
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
from pydantic import BaseModel, Field
import os
import httpx


def describe_geojson_feature_collection(feature_collection: Dict[str, Any]) -> str:
    num_features = len(feature_collection.get('features', []))
    properties = set()
    geometry_types = set()

    for feature in feature_collection.get('features', []):
        properties.update(feature.get('properties', {}).keys())
        geometry_type = feature.get('geometry', {}).get('type')
        if geometry_type:
            geometry_types.add(geometry_type)

    description = f"This GeoJSON FeatureCollection contains {num_features} features.\n"
    description += f"It has properties: {', '.join(properties)}.\n"
    description += f"The geometry types include: {', '.join(geometry_types)}.\n"

    return description


class QueryOGCAPIFeaturesCollectionInput(BaseModel):
    """Input for GetOGCAPIFeaturesDescriptionTool."""
    collection_name: str = Field(
        ..., description='The name of the collection to be queried')
    cql: str = Field(..., description=("CQL (common query language) to be used for filtering like:\n"
                                       "'http://{BASE_URL}/collections/{collection_name}/items?filter=< cql goes here >"))
    layer_name: str = Field(...,
                            description='Name of the layer that\'s created from the query')


class QueryOGCAPIFeaturesCollectionTool(BaseTool):
    """Tool"""

    name: str = "ogc_api_features_cql_filtering"
    args_schema: Type[BaseModel] = QueryOGCAPIFeaturesCollectionInput
    description: str = (
        "Use this tool to retrieve specific items from an OGC API Features collection.\n"
        "Use CQL (Common Query Language) to filter the returned items.\n"
        "The items will be stored in a file, the path of which will be returned to you."
    )

    def _run(self, collection_name: str, cql: str, layer_name: str, *args: Any, **kwargs: Any) -> Any:
        url = f'http://localhost:9000/collections/{collection_name}/items?filter={cql}&limit=5000'
        try:
            geojson_response = requests.get(url)
            path = 'output.json'
            output_directory = os.getcwd()
            path = os.path.join(output_directory, 'output.geojson')
            with open(path, 'w') as file:
                json.dump(geojson_response, file)

            return {
                'path': path,
                'geojson_description': describe_geojson_feature_collection(geojson_response),
                'layer_name': layer_name
            }
        except requests.RequestException as e:
            return {'error': str(e)}

    async def _arun(self, collection_name: str, cql: str, layer_name: str, *args: Any, **kwargs: Any) -> Any:
        url = f'http://localhost:9000/collections/{collection_name}/items?filter={cql}&limit=5000'
        print(url)
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url)
                res.raise_for_status()
                geojson_response = res.json()
                path = 'output.geojson'
                output_directory = os.getcwd()
                path = os.path.join(output_directory, path)
                with open(path, 'w') as file:
                    json.dump(geojson_response, file)

                return {
                    'path': path,
                    'geojson_description': describe_geojson_feature_collection(geojson_response),
                    'layer_name': layer_name
                }
        except httpx.HTTPStatusError as e:
            return (
                f"Error response {e.response.status_code}. "
                f'Make sure that there is no issue with the CQL included in the URL: {e.request.url!r}.'
            )
