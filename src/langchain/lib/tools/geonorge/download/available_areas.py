import requests
from pydantic import BaseModel, UUID4
from typing import Type

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
import httpx


class GeonorgeDatasetAvailableAreasInput(BaseModel):
    uuid: UUID4 = Field(description="UUID for the Geonorge dataset.")


class GeonorgeDatasetAvailableAreasTool(BaseTool):
    name = "geonorge_available_areas"
    description = (
        "Useful when you need to find available areas for a given Geonorge dataset from its UUID.\n"
        "There are often many areas, so don't use it to return all areas to the user, unless explicitely requested to."
    )
    args_schema: Type[BaseModel] = GeonorgeDatasetAvailableAreasInput

    def _run(self, uuid: str) -> str:
        """Use the tool."""
        url = 'https://nedlasting.geonorge.no/api/codelists/area/'
        res = requests.get(f'{url}{uuid}')
        area_names = list(map(lambda res: res['name'], res.json()))

        return area_names

    async def _arun(self, uuid: str) -> str:
        """Use the tool asynchronously."""
        url = 'https://nedlasting.geonorge.no/api/codelists/area/'

        async with httpx.AsyncClient() as client:
            res = await client.get(f'{url}{uuid}')
            area_names = list(map(lambda res: res['name'], res.json()))

        return area_names
