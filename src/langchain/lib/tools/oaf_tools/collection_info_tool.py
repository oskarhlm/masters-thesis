from typing import Optional, Type, List
import httpx
import os
import json
from collections import Counter

from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_community.tools.sql_database.tool import BaseSQLDatabaseTool
from langchain_core.pydantic_v1 import BaseModel, Field


class _OGCAPIFeaturesCollectionsInfoToolInput(BaseModel):
    collection_names: List[str] = Field(
        ...,
        description=(
            "A list of the collection_names names for which to return the schema."
        ),
    )


class InfoOGCAPIFeaturesCollectionsTool(BaseTool):
    """Tool for getting metadata about an OGC API Features endpoint."""

    name: str = "get_collections_info"
    description: str = "Get the schema and sample rows for the specified collections."
    args_schema: Type[BaseModel] = _OGCAPIFeaturesCollectionsInfoToolInput
    base_url: str = Field(exclude=True)

    def _run(
        self,
        collection_names: List[str],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Get the schema for tables in a comma-separated list."""
        raise NotImplementedError

    async def _arun(
        self,
        collection_names: List[str],
        *args, **kwargs
    ) -> str:
        """Get the schema for tables in a comma-separated list."""
        return f"\n\n{'-' * 100}\n\n".join(
            [f'{collection_name}\n\n{await get_collection_info(self.base_url, collection_name)}'
             for collection_name in collection_names]
        ) + '\n\nTHIS IS FOR YOUR USE ONLY, DO NOT PRESENT ALL THIS INFORMATION TO THE HUMAN.'


async def get_collection_info(base_url: str, collection_name: str) -> str:
    if not collection_name.startswith('public.'):
        collection_name = 'public.' + collection_name

    url = f'{base_url}/collections/{collection_name}.json'
    print(url)

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
            res.raise_for_status()

            data = res.json()
            del data['links']

            return json.dumps(data, indent=4) + f'\n\n{await get_properties_distribution(url)}'
            # return await get_properties_distribution(url)

    except httpx.HTTPStatusError as e:
        return f"Error response {e.response.status_code}. "


async def get_properties_distribution(collection_url):
    property_counters = {}
    async with httpx.AsyncClient() as client:
        res = await client.get(f'{collection_url}/items.json?limit=5000', timeout=None)
        res.raise_for_status()

        data = res.json()

        property_counters = {}

        for feature in data['features']:
            for key, value in feature['properties'].items():
                if key in ['id', 'code', 'osm_id', 'name', 'ref', 'layer', 'population']:
                    continue

                if key not in property_counters:
                    property_counters[key] = Counter()

                property_counters[key][value] += 1

    total_counts = {key: sum(counter.values())
                    for key, counter in property_counters.items()}

    percentages = {}
    cutoff = 0.5
    for key, counter in property_counters.items():
        percentages[key] = {}
        sorted_values = sorted(
            counter.items(), key=lambda x: x[1], reverse=True)
        for value, count in sorted_values:
            percentage = count / total_counts[key] * 100
            if len(percentages[key]) < 10 or percentage >= cutoff:
                percentages[key][value] = percentage

    output = ''
    for key, values in percentages.items():
        output += f"Property: {key}\n"
        sorted_values = sorted(
            values.items(), key=lambda x: x[1], reverse=True)
        for value, percentage in sorted_values:
            output += f"    {value}: {percentage:.1f}%\n"

    return output
