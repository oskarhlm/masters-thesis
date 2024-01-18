import aiohttp
import requests
from typing import Type, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from typing import List
url = 'https://nedlasting.geonorge.no/api/codelists/projection'


{
    "orderLines": [
        {
            "metadataUuid": "24d7e9d1-87f6-45a0-b38e-3447f8d7f9a1",
            "areas": [
                {
                    "code": "33",
                    "name": "Buskerud",
                    "type": "fylke"
                }
            ],
            "formats": [
                {
                    "name": "SOSI 4.5"
                }
            ],
            "projections": [
                {
                    "code": "25832"
                }
            ]
        }
    ]
}


class MetaData(BaseModel):
    Uuid: str = Field(description='Unique identifier for the search result')
    Title: str = Field(description='Title of the search result')
    Abstract: str = Field(description='Abstract describing the result')


class GeonorgeDownloadResponse(BaseModel):
    NumFound: int = Field(
        description='Number of search results for the given query')
    Results: List[MetaData] = Field(
        description='List of metadata for the results')


class GeonorgeDownloadInput(BaseModel):
    """Input for GeonorgeSearchTool."""
    metadata_uuid: str = Field(
        description='Unique identifier for the item to download')
    data_format: Optional[str] = Field(
        description='Geospatial data format for downloaded data')


class GeonorgeDownloadTool(BaseTool):
    """Custom tool to search for geospatial data through the Geonorge API."""

    name: str = "geonorge-search"
    args_schema: Type[BaseModel] = GeonorgeDownloadInput
    description: str = "Use this tool for search for geospatial dataset and APIs through the Geonorge API."

    base_url = "https://kartkatalog.geonorge.no"
    endpoint = "/api/search"

    def _run(self, text: str) -> str:
        params = {
            'text': text,
            'limit': 10
        }

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
