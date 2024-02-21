from pydantic import BaseModel
from typing import Type, Dict, Union, Literal

from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field

LINE_PAINT_EXAMPLE = {
    "line-color": "#eb76d8",
    "line-width": 3
}


class SetMapLayerPaintInput(BaseModel):
    layer_id: str = Field(..., description='ID of the MapBox/MapLibre layer')
    layer_type: Literal["fill", "line",
                        "circle"] = Field(..., description="Rendering type of the layer")
    paint: Dict[str, str] = Field(..., description=(
        f'Paint properties for the layer. Example for `line`:\n{LINE_PAINT_EXAMPLE}'
    ))


class SetMapLayerPaintTool(BaseTool):
    name = "set_map_layer_paint"
    description = "Useful for when you need change the paint property of a MapBox layer."
    args_schema: Type[BaseModel] = SetMapLayerPaintInput

    def _run(self) -> str:
        raise NotImplementedError

    async def _arun(self) -> str:

        return {'ws': {'paint': '{...}'}}
