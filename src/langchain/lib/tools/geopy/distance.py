"""
Borrowed from Development Seed.

https://github.com/developmentseed/llllm/blob/main/tools/geopy/distance.py
"""

from typing import Type

from geopy.distance import distance
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from typing import List, Tuple


class GeopyDistanceInput(BaseModel):
    """Input for GeopyDistanceTool."""

    point_1: List[float] = Field(
        ..., description="Tuple of lenght 2 representing the (lat, lng) of a place")
    point_2: List[float] = Field(
        ..., description="Tuple of lenght 2 representing the (lat, lng) of a place")


class GeopyDistanceTool(BaseTool):
    """Custom tool to calculate geodesic distance between two points."""

    name: str = "distance"
    args_schema: Type[BaseModel] = GeopyDistanceInput
    description: str = "Use this tool to compute distance between two points available in lat,lng format."

    def _run(self, point_1, point_2) -> float:
        return f'{distance(point_1, point_2).km} kilometers'

    async def _arun(self, point_1, point_2):
        return self._run(point_1, point_2)
