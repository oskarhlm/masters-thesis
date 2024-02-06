import json
from typing import Any, Coroutine, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
from typing import List
from pydantic import BaseModel, Field
import aiohttp


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


class QueryOGCAPIFeaturesItemsInput(BaseModel):
    """Input for GetOGCAPIFeaturesDescriptionTool."""
    items_url: str = Field(
        ..., description="The URL for the collection items, i.e., http://{BASE_URL}/collections/{collection_id}/items")
    cql: str = Field(..., description=("CQL (common query language) to be used for filtering like:\n"
                                       "'http://{BASE_URL}/collections/{collection_id}/items?filter=< cql goes here >"))


class QueryOGCAPIFeaturesItemsTool(BaseTool):
    """Tool"""

    name: str = "ogc_features_cql_filtering"
    args_schema: Type[BaseModel] = QueryOGCAPIFeaturesItemsInput
    description: str = "Use this tool to retrieve specific items from an OGC API Features collection, using CQL to filter the returned items."

    # return_direct = True

    def _run(self, items_url: str, cql: str, *args: Any, **kwargs: Any) -> Any:
        url = f'{items_url}?filter={cql}'
        try:
            res = requests.get(url)
            res.raise_for_status()
            return res.json()
        except requests.RequestException as e:
            return {'error': str(e)}

    def _arun(self, *args: Any, **kwargs: Any) -> Coroutine[Any, Any, Any]:
        raise NotImplementedError
