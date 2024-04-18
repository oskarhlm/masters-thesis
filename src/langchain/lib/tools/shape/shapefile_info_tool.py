from typing import Type, List


import geopandas as gpd
from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field

from ...utils.workdir_manager import WorkDirManager


class _InfoShapefileToolInput(BaseModel):
    shapefile_names: List[str] = Field(
        ...,
        description=(
            "A list of shapefile names from the working directory (without the workdir path)"
        ),
    )


class InfoShapefileTool(BaseTool):
    """Tool for getting metadata about a Shapefile."""

    name: str = "get_shapefile_info"
    description: str = "Get schema, sample rows, and other info for Shapefiles."
    args_schema: Type[BaseModel] = _InfoShapefileToolInput

    def _run(self, *args, **kwargs) -> str:
        """Get the schema for tables in a comma-separated list."""
        raise NotImplementedError

    async def _arun(
        self,
        shapefile_names: List[str],
        *args, **kwargs
    ) -> str:
        """Get the schema for tables in a comma-separated list."""
        return f"\n\n{'-' * 100}\n\n".join(
            [get_shapefile_info(shapefile_name)
             for shapefile_name in shapefile_names]
        ) + '\n\nTHIS IS FOR YOUR USE ONLY, DO NOT PRESENT ALL THIS INFORMATION TO THE HUMAN.'


def get_shapefile_info(shapefile_name: str) -> str:
    shapefile_path = str(WorkDirManager.load_file(
        filename=shapefile_name, return_path=True))
    print(shapefile_path)
    df = gpd.read_file(shapefile_path, rows=5000)

    output = shapefile_name
    output += f'\n\nColumns: {df.columns}'
    output += f'\nCRS: {df.crs.to_string()}'

    exclude_columns = ['id', 'code', 'osm_id',
                       'name', 'ref', 'layer', 'population', 'geometry']
    for column_name in [c for c in df.columns if c not in exclude_columns]:
        output += f'\n\n{get_properties_distribution(df, column_name)}'

    return output


def get_properties_distribution(df, column_name: str):
    fclass_counts = df[column_name].value_counts()

    total = len(df)
    percentages = (fclass_counts / total * 100).rename('percent')
    formatted_percentages = percentages.apply(lambda x: f'{x:.2f}%')

    return str(formatted_percentages.head(10))
