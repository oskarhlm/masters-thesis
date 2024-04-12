import os
from typing import Annotated, Sequence, TypedDict, Union
import operator
from typing_extensions import TypedDict, NotRequired
from datetime import datetime

from langchain_core.messages import BaseMessage
from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.sql_database import SQLDatabase

from ..redis_checkpointer import RedisSaver
from ..sessions import generate_session_id
from ..agent_executor import create_tool_calling_executor
from ...utils.workdir_manager import WorkDirManager
from ...tools.sql.toolkit import CustomSQLDatabaseToolkit
from ...tools.map_interaction.publish_geojson import PublishGeoJSONTool


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    working_directory: str
    current_files: str
    agent_outcome: Union[AIMessage, None]
    intermediate_steps: Annotated[Sequence[ToolMessage], operator.add]
    last_system_message_time: NotRequired[datetime]


def prelude(state: AgentState) -> AgentState:
    written_files = WorkDirManager.list_files()
    if not written_files:
        return {
            **state,
            'working_directory': WorkDirManager.get_abs_path(),
            "current_files": "There are currently no files written to the working directory.",
            'agent_outcome': None,
            'intermediate_steps': []
        }
    else:
        formatted_files = "\n".join(
            [f" - {f}" for f in written_files])
        return {
            **state,
            'working_directory': WorkDirManager.get_abs_path(),
            "current_files": (
                f"Below are files that are written to the working directory:\n{formatted_files}\n\n"
                'You can use Python to perform analyses on these files, if they are sufficient for the problem at hand.'
            ),
            'intermediate_steps': []
        }


def postlude(state: AgentState) -> AgentState:
    return state


PYTHON_CHECKLIST = """Checklist when generating Python code for GIS-tasks: 
    - All input data uses lat/lon. Keep this in mind when working with metric units (common in buffering tasks, etc.)
    - ALWAYS save results as GeoJSON in EPSG:4326 (WGS84) 
"""


def create_sql_lg_agent_runnable() -> AgentState:
    db = SQLDatabase.from_uri(
        database_uri=os.getenv('POSTGRES_CONN'),
        sample_rows_in_table_info=1,
    )
    llm = ChatOpenAI(model=os.getenv('GPT4_MODEL_NAME'), streaming=True)
    toolkit = CustomSQLDatabaseToolkit(db, llm).get_tools()
    tools = toolkit + [PublishGeoJSONTool()]

    system_prompt = (
        'You are a helpful GIS agent/consultant that has access to an OGC API Features data catalog.\n'
        'To retrieve data, list all collections, find info about relevant collections, and then fetch features from the collections.\n'
        'Retrieve data by using  these tools (in order): `list_collections` --> `get_collections_info` --> `query_collection`\n\n'
        'Use Python to perform additional analyses on the retrieved data.\n'
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
