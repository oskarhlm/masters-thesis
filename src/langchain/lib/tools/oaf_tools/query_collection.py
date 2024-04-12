from typing import Type, Dict, Any
import httpx
import os

from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ...utils.workdir_manager import WorkDirManager


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


QUERY_CHECKER_PROMPT = """
{query}

Double check the CQL filter above for common mistakes, including:
- Using single quotation marks around strings (VERY IMPORTANT), e.g. 

Examples: 
fclass=building --> fclass='building'
type=garage --> type='garage'

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

Output the final CQL filter only.

CQL Query: """


class QueryOGCAPIFeaturesCollectionInput(BaseModel):
    """Input for GetOGCAPIFeaturesDescriptionTool."""
    collection_name: str = Field(
        ..., description='The name of the collection to be queried')
    cql_filter: str = Field(None, description=(
        "Optional CQL (common query language) query to be used for retrieving a subset of the collection.\n"
        "Examples include filtering on `fclass` (fclass=<class name>) and `name` (name=<feature name>) attributes."
    ))
    bbox: str = Field(None,
                      description='Optional bounding box, like `160.6,-55.95,-170,-25.89`. Do not use unless absolutely necessary.')
    layer_name: str = Field(...,
                            description='Name of the layer that\'s created from the query')


class QueryOGCAPIFeaturesCollectionTool(BaseTool):
    """Tool"""

    name: str = "query_collection"
    args_schema: Type[BaseModel] = QueryOGCAPIFeaturesCollectionInput
    description: str = (
        "Use this tool to retrieve specific items from an OGC API Features collection.\n"
        "Use CQL (Common Query Language) to filter the returned items"
        " and the bounding box parameter to retrieve more specific data.\n"
        "The items will be stored in a file on the server, the path of which will be returned to you."
    )
    base_url: str = Field(exclude=True)

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    async def _arun(self, collection_name: str, layer_name: str, *args: Any, **kwargs: Any) -> Any:

        if not collection_name.startswith('public.'):
            collection_name = 'public.' + collection_name

        url = f'{self.base_url}/collections/{collection_name}/items?limit=10000'

        if 'cql_filter' in kwargs and kwargs['cql_filter'] is not None:
            cql_filter = kwargs['cql_filter']
            llm = ChatOpenAI(model=os.getenv('GPT3_MODEL_NAME'))
            prompt = ChatPromptTemplate.from_template(QUERY_CHECKER_PROMPT)
            chain = prompt | llm | StrOutputParser()
            corrected_cql_filter = chain.invoke({'query': cql_filter})
            print(corrected_cql_filter)
            url += f"&filter={corrected_cql_filter}"
        if 'bbox' in kwargs and kwargs['bbox']:
            url += f"&bbox={kwargs['bbox']}"

        print(url)

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, timeout=None)
                res.raise_for_status()
                geojson_response = res.json()
                filename = f'{layer_name}.geojson'

                num_features = len(geojson_response['features'])
                if num_features == 0:
                    return (
                        f'No features were found at {url}.\n'
                        'Try to change the parameters, or make them less restrictive.'
                    )

                WorkDirManager.add_file(
                    filename, geojson_response, save_as_json=True)
                num_features = len(geojson_response['features'])
                return f"Query returned {num_features} feature{'s' if num_features else ''}."

        except httpx.HTTPStatusError as e:
            return (
                f"Error response {e.response.status_code}. "
                f'Make sure that there is no issue with the CQL included in the URL: {e.request.url}.'
            )
