from typing import List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
from typing import List
from pydantic import BaseModel, Field
import aiohttp


class MetaData(BaseModel):
    Uuid: str = Field(description='Unique identifier for the search result')
    Title: str = Field(description='Title of the search result')
    Abstract: str = Field(description='Abstract describing the result')


class GeonorgeSearchResponse(BaseModel):
    NumFound: int = Field(
        description='Number of search results for the given query')
    Results: List[MetaData] = Field(
        description='List of metadata for the results')


class GeonorgeSearchInput(BaseModel):
    """Input for GeonorgeSearchTool."""
    text: str = Field(..., description="The search query string")


class GeonorgeSearchTool(BaseTool):
    """Custom tool to search for geospatial data through the Geonorge API."""

    name: str = "geonorge-search"
    args_schema: Type[BaseModel] = GeonorgeSearchInput
    description: str = "Use this tool for search for geospatial dataset and APIs through the Geonorge API."

    base_url = "https://kartkatalog.geonorge.no"
    endpoint = "/api/search"

    def _run(self, text: str) -> str:
        params = {'text': text}

        response = requests.get(
            url=f"{self.base_url}{self.endpoint}", params=params)
        data = response.json()

        return GeonorgeSearchResponse(**data).model_dump_json(indent=4)

    async def _arun(self, text: str):
        params = {'text': text}

        async with aiohttp.ClientSession() as session:
            async with session.get(url=f"{self.base_url}{self.endpoint}", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return GeonorgeSearchResponse(**data).model_dump_json(indent=4)
                else:
                    return f"Error: HTTP {response.status}"
