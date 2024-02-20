from pydantic import BaseModel
from typing import Type

from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from fastapi import WebSocket


class SetMapLayerPaintInput(BaseModel):
    pass


# class SetMapLayerPaintTool(BaseTool):
#     name = "set_map_layer_paint"
#     description = "Useful for when you need change the paint property of a MapBox layer."
#     args_schema: Type[BaseModel] = SetMapLayerPaintInput

#     ws: WebSocket = Field(exclude=True)

#     def _run(self) -> str:
#         return '_run'

#     async def _arun(self) -> str:
#         print(self.ws)
#         return {'ws': {'paint': '{...}'}}
