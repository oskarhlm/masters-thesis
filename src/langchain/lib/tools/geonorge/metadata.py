from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
from pydantic import BaseModel, Field
import aiohttp


class GeonorgeDatasetMetadataInput(BaseModel):
    """Input for GeonorgeSearchTool."""
    uuid: str = Field(description='Unique identifier for the data endpoint')


class GeonorgeDatasetMetadataTool(BaseTool):
    """Custom tool to retrieve metadata for a geospatial dataset through the Geonorge API."""

    name: str = "geonorge-dataset-metadata"
    args_schema: Type[BaseModel] = GeonorgeDatasetMetadataInput
    description: str = (
        "Use this tool to retrieve metadata for a geospatial dataset through the Geonorge API.\n"
        'Useful when the user requests more detailed information about a dataset.'
    )

    base_url = "https://kartkatalog.geonorge.no"
    endpoint = "/api/getdata"

    def _run(self, uuid: str) -> str:
        response = requests.get(
            url=f"{self.base_url}{self.endpoint}/{uuid}")
        data = response.json()

        return data

    async def _arun(self, uuid: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=f"{self.base_url}{self.endpoint}/{uuid}") as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return f"Error: HTTP {response.status}"
