import os
from typing import Annotated, Sequence, TypedDict, Union
import operator
from typing_extensions import TypedDict, NotRequired
from datetime import datetime

from langchain_core.messages import BaseMessage
from langchain_core.messages import AIMessage
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
    last_system_message_time: NotRequired[datetime]


def prelude(state: AgentState) -> AgentState:
    written_files = WorkDirManager.list_files()
    working_directory_path = WorkDirManager.get_abs_path()

    if not written_files:
        current_files_msg = "There are currently no files written to the working directory."
    else:
        formatted_files = "\n".join(
            [f" - {f.name.split('/')[-1]}" for f in written_files])
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


SQL_CHECKLIST = """Checklist when generating SQL code for GIS-tasks: 
    - All input data uses lat/lon. Keep this in mind when working with metric units (common in buffering tasks, etc.)
    - ALWAYS return all columns (`SELECT *`, etc.).
    - If more than one layer is selected, perform separate queries in order to create separate files. 
    - NEVER perform conversion to GeoJSON in the SQL query.
"""


def create_sql_lg_agent_runnable() -> AgentState:
    import geoalchemy2  # To enable reflection of Geometry columns
    db = SQLDatabase.from_uri(
        database_uri=os.getenv('POSTGRES_CONN'),
        sample_rows_in_table_info=1,
    )
    llm = ChatOpenAI(model=os.getenv('GPT4_MODEL_NAME'), streaming=True)
    toolkit = CustomSQLDatabaseToolkit(db=db, llm=llm).get_tools()
    tools = toolkit + [PublishGeoJSONTool()]

    system_prompt = (
        'You are a helpful GIS agent/consultant that has access to an SQL database containing OpenStreetMap data from Norway.\n'
        'To retrieve data, list all tables, find info about relevant tables, and construct an SQL query to answer the human\'s question.\n'
        'Retrieve data by using  these tools (in order): `sql_db_list_tables` --> `sql_db_schema` --> `sql_db_query`\n\n'
        'Add data to the map to allow the human user to see the results of the analyses you perform.\n\n'
        'Results from `sql_db_query` are stored in {working_directory}.\n'
        '{current_files}\n\n'
        f'{SQL_CHECKLIST}'
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
