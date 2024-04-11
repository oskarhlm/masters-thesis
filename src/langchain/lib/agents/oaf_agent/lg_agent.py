import os
from typing import Annotated, Sequence, TypedDict, Union
import operator
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langchain_core.messages import AIMessage, ToolMessage
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_experimental.tools.python.tool import PythonAstREPLTool

from ..redis_checkpointer import RedisSaver
from ..sessions import generate_session_id
from ..agent_executor import create_tool_calling_executor
from ...utils.workdir_manager import WorkDirManager
from ...tools.oaf_tools.toolkit import OAFToolkit
from ...tools.map_interaction.publish_geojson import PublishGeoJSONTool


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    working_directory: str
    current_files: str
    agent_outcome: Union[AIMessage, None]
    intermediate_steps: Annotated[Sequence[ToolMessage], operator.add]


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
    print(state['__end__']['agent_outcome'])
    state['__end__']['messages'] += state['__end__']['agent_outcome']
    # print(state)
    return state


def create_oaf_lg_agent_runnable() -> AgentState:
    llm = ChatOpenAI(model=os.getenv('GPT3_MODEL_NAME'), streaming=True)
    tools = OAFToolkit(base_url=os.getenv('OGC_API_FEATURES_BASE_URL'), llm=llm).get_tools() + \
        [PythonAstREPLTool(), PublishGeoJSONTool()]
    system_prompt = (
        'You are a helpful GIS agent/consultant that has access to an OGC API Features data catalog.\n'
        'Use tools to list collections, get info about relevant collections and fetching features from the collections.\n'
        'Use Python to perform additional analyses on the data.\n'
        'Add data to the map to allow the human user to see the results of the analyses you perform.\n\n'
        'The working directory is {working_directory}. Make sure to save all files to this directory.\n'
        '{current_files}\n\n'
    )

    prompt = ChatPromptTemplate.from_messages([
        ('system', system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="intermediate_steps")
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
