from typing import Any, Coroutine, Type

from geopy.distance import distance
from pydantic import BaseModel, Field
from langchain.tools import BaseTool


class GeoJSONURLInput(BaseModel):
    pass


class GeoJSONURLTool(BaseTool):
    """Tool for getting a GeoJSON URL."""

    name: str = "geojson_url"
    args_schema: Type[BaseModel] = GeoJSONURLInput
    description: str = "Use this tool to get a URL that points to a GeoJSON resource."

    def _run(self, *args: Any, **kwargs: Any) -> str:
        """Get the GeoJSON URL."""
        return 'https://google.com'

    async def _arun(self, *args: Any, **kwargs: Any) -> str:
        """Get the GeoJSON URL async."""
        return 'https://google.com'
