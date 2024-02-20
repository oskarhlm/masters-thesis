from pydantic import BaseModel
from typing import Type

from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field

from ...utils.map_state import load_map_state

sample_map_state = """
{
    "center": {
        "lng": 10.315412783000056,
        "lat": 63.32068482345329
    },
    "bounds": {
        "_sw": {
            "lng": 10.292837816599388,
            "lat": 63.30880868143515
        },
        "_ne": {
            "lng": 10.337987749399474,
            "lat": 63.33255606861931
        }
    },
    "zoom": {
        "current": 12.897623384669835,
        "max": 22,
        "min": -2
    },
    "layers": [
        {
            "id": "roads_speed_limit_100",
            "type": "line",
            "source": "roads_speed_limit_100",
            "paint": {
                "line-color": "#eb76d8",
                "line-width": 3
            }
        }
    ]
}
"""


class GetMapStateTool(BaseTool):
    name = "get_map_state_tool"
    description = (
        "Useful for get updated information about the state of the map.\n\n"
        f"Sample return:\n{sample_map_state}"
    )

    def _run(self) -> str:
        return load_map_state()

    async def _arun(self) -> str:
        return self._run()
