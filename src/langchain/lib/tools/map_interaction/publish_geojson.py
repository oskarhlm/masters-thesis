from typing import Any, Optional, Type
from pathlib import Path

import geojson
from geojson import GeoJSON
from langchain_core.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field, root_validator

from ...utils.workdir_manager import WorkDirManager


class PublishGeoJSONInput(BaseModel):
    geojson_path: Optional[str] = Field(
        None, description='Path to the .geojson file to publish')
    geojson_data: Optional[str] = Field(
        None, description='GeoJSON data as a raw string')
    layer_name: str = Field(...,
                            description='Name of the layer (should be snake_case)')

    @root_validator
    def check_geojson_source(cls, values):
        geojson_path, geojson_data = values.get(
            'geojson_path'), values.get('geojson_data')
        if not geojson_path and not geojson_data:
            raise ValueError(
                'Either geojson_path or geojson_data must be provided')
        return values


class PublishGeoJSONTool(BaseTool):
    name = "add_geojson_to_map"
    description = (
        "Use this to add arbitrary geojson data to a client-side map visible to the user.\n"
        "Provide either a path to a file containing GeoJSON, or the data itself using the geojson_data parameter."
    )
    args_schema: Type[BaseModel] = PublishGeoJSONInput

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        return NotImplementedError

    async def _arun(
        self,
        geojson_path: Optional[str] = None,
        geojson_data: Optional[str] = None,
        layer_name: str = None,
    ) -> str:
        if geojson_path:
            loaded_geojson_path: Path = WorkDirManager.load_file(
                filename=geojson_path, return_path=True)
            if loaded_geojson_path:
                with open(loaded_geojson_path, 'r') as file:
                    geojson_data: GeoJSON = geojson.load(file)
            else:
                available_files = ', '.join(
                    [str(f.name) for f in WorkDirManager.list_files()])
                return f'Could not find GeoJSON file `{geojson_path}`.\nAvailable files are: {available_files}'
        elif geojson_data:
            geojson_data: GeoJSON = geojson.loads(geojson_data)
            geojson_path = str(
                WorkDirManager.add_file(
                    f'{layer_name}.geojson', geojson_data, save_as_json=True)
            )
        else:
            return 'Error: Specify either `geojson_path` or `geojson_data`'

        if not geojson_data.is_valid:
            return f'Errors found in geojson file:\n{geojson_data.errors()}'

        return {'geojson_path': geojson_path, 'layer_name': layer_name, 'add_to_map': True}
