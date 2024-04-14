import os
from typing import Annotated, Sequence, TypedDict, Union
import operator
from typing_extensions import TypedDict, NotRequired
from datetime import datetime
from pathlib import Path
from columnar import columnar

from langchain_core.messages import BaseMessage
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_experimental.tools.python.tool import PythonAstREPLTool

from ..redis_checkpointer import RedisSaver
from ..sessions import generate_session_id
from ..agent_executor import create_tool_calling_executor
from ...utils.workdir_manager import WorkDirManager
from ...tools.map_interaction.publish_geojson import PublishGeoJSONTool
from ...tools.shape.shapefile_info_tool import InfoShapefileTool


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    working_directory: str
    current_files: str
    agent_outcome: Union[AIMessage, None]
    last_system_message_time: NotRequired[datetime]


def filter_file_names(file_names, exclude_extensions):
    filtered_file_names = []
    for file_name in file_names:
        if name == 'README':
            continue
        name, extension = file_name.rsplit('.', 1)
        if extension not in exclude_extensions:
            filtered_file_names.append(file_name)
    return filtered_file_names


def get_size(path: Path) -> str:
    size_bytes = path.stat().st_size
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} YB"


def prelude(state: AgentState) -> AgentState:
    written_files: list[Path] = WorkDirManager.list_files()
    working_directory_path = WorkDirManager.get_abs_path()

    if not written_files:
        current_files_msg = "There are currently no files written to the working directory."
    else:
        formatted_files = columnar([[f, get_size(f)] for f in written_files], headers=[
                                   'FILE', 'SIZE'], no_borders=True)
        current_files_msg = f"Below are files that are written to the working directory:\n{formatted_files}\n\nYou can use Python to perform analyses on these files, if they are sufficient for the problem at hand."

    return {
        **state,
        'working_directory': working_directory_path,
        "current_files": current_files_msg,
        'agent_outcome': None,
        'last_system_message_time': datetime.now()
    }


def postlude(state: AgentState) -> AgentState:
    return state


PYTHON_CHECKLIST = """Checklist when generating Python code for GIS-tasks: 
    - All input data uses lat/lon. Keep this in mind when working with metric units (common in buffering tasks, etc.)
    - ALWAYS save results as GeoJSON in EPSG:4326 (WGS84) 
    - Do not forget to import both geopandas (gpd) and pandas (pd), when using both
    - Using SQL when reading very large files (bbox query, etc.) to load less data into memory (which can be time consuming) 
"""


def create_python_lg_agent_runnable() -> AgentState:
    llm = ChatOpenAI(model=os.getenv('GPT4_MODEL_NAME'), streaming=True)
    tools = [PythonAstREPLTool(), PublishGeoJSONTool(), InfoShapefileTool()]
    system_prompt = (
        'You are a helpful GIS agent/consultant that has access to a working directoy with geospatial files.\n'
        'Get info about relevant files for analysis using `get_shapefile_info`'
        ' and use Python to perform geospatial analyses on them.\n'
        'Add data to the map to allow the human user to see the results of the analyses you perform.\n\n'
        'The working directory is {working_directory}. Make sure to save all files to this directory.\n'
        '{current_files}\n\n'
        f'{PYTHON_CHECKLIST}'
    )

    prompt = ChatPromptTemplate.from_messages([
        ('system', system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])

    session_id = generate_session_id()
    memory = RedisSaver.from_conn_string(os.getenv('REDIS_URL'))

    agent_executor = create_tool_calling_executor(
        model=llm, tools=tools, input_schema=AgentState, prompt=prompt, checkpointer=memory)

    return session_id, (
        prelude
        | agent_executor
        | postlude
    )
