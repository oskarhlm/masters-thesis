import json
from typing import Type
import geopandas as gpd
import pandas as pd

from shapely import wkb
from langchain_community.tools.sql_database.tool import BaseSQLDatabaseTool
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
from sqlalchemy.exc import SQLAlchemyError

from ...utils.workdir_manager import WorkDirManager


class CustomQuerySQLDataBaseInput(BaseModel):
    query: str = Field(..., description='SQL query to be executed.')
    layer_name: str = Field(...,
                            description='A descriptive name for the result data. Should be snake_case.')


class CustomQuerySQLDataBaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for querying a SQL database."""

    name: str = "sql_db_query"
    args_schema: Type[BaseModel] = CustomQuerySQLDataBaseInput
    description: str = """
    Input to this tool is a detailed and correct SQL query.
    The result will be stored in a working directory on the server.
    If the query is incorrect, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    Input data is in WGS84 (which uses lat/lon). Keep this in mind when querying with metric units.
    """

    def _run(
        self,
        query: str,
        layer_name: str
    ) -> str:
        """Execute the query, return the results or an error message."""
        try:
            df = pd.read_sql(query.replace('%', '%%'), self.db._engine)

            if not len(df):
                return f'No features found using the provided query: {query}'
            if 'geom' not in df:
                if 'geojson' in df:
                    return '\nDO NOT perform conversion to GeoJSON, just include the `geom` column in the SELECT. Try again.'
                return f'{df[:50]}\n\nThe `geom` column is required to create a layer that can be added to the map.'

            df['geom'] = df['geom'].apply(lambda x: wkb.loads(x, hex=True))
            gdf = gpd.GeoDataFrame(df, geometry='geom')

            if not len(gdf):
                raise ValueError("No features found in the result.")

            filename = f'{layer_name}.geojson'
            WorkDirManager.add_file(
                filename, gdf, save_as_json=True)

            gdf_head = gdf[:50]
            feature_pluralized = f"feature{'s' if len(gdf) > 1 else ''}"
            output = f"Query returned {len(gdf)} {feature_pluralized}."
            output += f'Below are the first {len(gdf_head)} {feature_pluralized}:\n\n{gdf_head}'

            return output

        except SQLAlchemyError as e:
            """Format the error message"""
            return f"Error: {e}"
        except json.JSONDecodeError as e:
            return f"Error parsing JSON result: {str(e)}"
        except ValueError as e:
            return str(e)
