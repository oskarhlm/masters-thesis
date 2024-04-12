from typing import Any, Optional
import re

import httpx
from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain.pydantic_v1 import Field


class ListOGCAPIFeaturesCollectionsTool(BaseTool):
    """Tool for getting tables names."""

    name: str = "list_collections"
    description: str = "Input is an empty string, output is a comma separated list of tables in the database."
    base_url: str = Field(exclude=True)

    def _run(
        self,
        tool_input: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs
    ) -> str:
        """Get the schema for a specific table."""
        raise NotImplementedError

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        url = f'{self.base_url}/collections.json'
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=None)
            res.raise_for_status()

            data = res.json()
            return '\n'.join(
                [f"`{collection['title']}` -- {collection['description']}"
                 for collection in data['collections']]
            )
