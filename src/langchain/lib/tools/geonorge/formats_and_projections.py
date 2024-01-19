import requests
from pydantic import BaseModel
from typing import Type

import aiohttp
from langchain.tools import BaseTool
import re
from langchain.pydantic_v1 import BaseModel, Field


class AvailableFormatsAndProjectsionsInput(BaseModel):
    metadata_uuid: str = Field(
        description='Unique identifier for the item to download')
    area: str = Field(
        description=(
            "The 'kommune' or 'fylke' to be queried for available data formats and projections.\n"
            'Areas can be single names: "Drammen", "Oslo", "Agder", etc.\n'
            'Areas can also have Sami variants, formatted like this: "Troms - Romsa - Tromssa", etc.'
        ))


class AvailableFormatsAndProjectionsTool(BaseTool):
    name = "available_formats_and_projections"
    description = "Useful for when you need to find available data formats and projections for a given geographical area."
    args_schema: Type[BaseModel] = AvailableFormatsAndProjectsionsInput

    def _run(self, metadata_uuid: str, area: str) -> str:
        """Use the tool."""
        area = area.replace("\n", "")  # Remove newline characters
        # Split names by hyphen, trimming spaces
        possible_names = re.split(r'\s*-\s*', area)

        res = requests.get(
            f'https://nedlasting.geonorge.no/api/codelists/area/{metadata_uuid}')
        data = res.json()

        for item in data:
            item_name = item.get("name", "")
            if any(name in item_name for name in possible_names):
                return item

        return (
            'Could not find formats and projections for provided area.\n'
            f'Available areas are:\n\n{[item.get("name") for item in data]}'
        )

    async def _arun(self, metadata_uuid: str, area: str) -> str:
        """Use the tool asynchronously."""
        area = area.replace("\n", "")
        possible_names = re.split(r'\s*-\s*', area)

        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://nedlasting.geonorge.no/api/codelists/area/{metadata_uuid}') as res:
                if res.status == 200:
                    data = await res.json()
                    for item in data:
                        item_name = item.get("name", "")
                        if any(name in item_name for name in possible_names):
                            return item
                    return (
                        'Could not find formats and projections for provided area.\n'
                        f'Available areas are:\n\n{[item.get("name") for item in data]}'
                    )
                else:
                    return 'Error fetching data'
