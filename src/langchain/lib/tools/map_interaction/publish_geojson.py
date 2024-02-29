from pydantic import BaseModel
from typing import Type, Dict, Literal, Optional
from pathlib import Path

from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
import geojson
from geojson import GeoJSON


from ...utils.workdir_manager import WorkDirManager

LINE_PAINT_EXAMPLE = {
    "line-color": "#eb76d8",
    "line-width": 3
}


class PublishGeoJSONInput(BaseModel):
    geojson_path: Optional[str] = Field(...,
                                        description='Path to the .geojson file to publish')
    # geojson_data: Optional[str] = Field(..., description='GeoJSON data')
    layer_name: str = Field(...,
                            description='Name of the layer (should be snake_case)')
    # layer_type: Literal["fill", "line",
    #                     "circle"] = Field(..., description="Rendering type of the layer")
    # paint: Dict[str, str] = Field(..., description=(
    #     f'Paint properties for the layer. Example for `line`:\n{LINE_PAINT_EXAMPLE}'
    # ))


class PublishGeoJSONTool(BaseTool):
    name = "add_geojson_to_map"
    description = (
        "Use this to add arbitrary geojson data to a client-side map visible to the user.\n"
        "Provide either a path to a file containing GeoJSON, or the data itself using the geojson_data parameter."
    )
    args_schema: Type[BaseModel] = PublishGeoJSONInput

    def _run(self) -> str:
        raise NotImplementedError

    async def _arun(self, geojson_path: Optional[str] = None, geojson_data: Optional[str] = None, layer_name: str = None) -> str:
        if not (geojson_path or geojson_data):
            return 'Error: Specify either `geojson_path` or `geojson_data`'

        if not geojson_data:
            loaded_geojson_path: Path = WorkDirManager.load_file(
                filename=geojson_path, return_path=True)
            if loaded_geojson_path:
                with open(loaded_geojson_path, 'r') as file:
                    geojson_data: GeoJSON = geojson.load(file)
            else:
                available_files = ', '.join(
                    [str(f.name) for f in WorkDirManager.list_files()])
                return (
                    f'Could not find GeoJSON file `{geojson_path}`.\n'
                    f'Available files are: {available_files}'
                )
        else:
            geojson_data: GeoJSON = geojson.loads(geojson_data)

        if not geojson_data.is_valid:
            return f'Errors found in geojson file:\n{geojson_data.errors()}'

        return {'geojson_path': geojson_path or geojson_data, 'layer_name': layer_name, 'add_to_map': True}
