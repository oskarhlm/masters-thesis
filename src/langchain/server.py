from enum import Enum
import os
import json
from typing import Dict, Any, List
import tempfile

from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException, Request
from fastapi import FastAPI, UploadFile, File, Form
from dotenv import load_dotenv
from langchain.agents import AgentExecutor
from langchain.tools import BaseTool
from langchain_core.messages import AIMessageChunk, FunctionMessage
from pydantic import BaseModel

from lib.agents.tool_agent import create_tool_agent
from lib.agents.sql_agent.agent import create_sql_agent, CustomQuerySQLDataBaseTool
from lib.agents.oaf_agent.agent import create_oaf_agent
from lib.tools.oaf_tools.query_collection import QueryOGCAPIFeaturesCollectionTool
from lib.utils.ai_suffix_selection import select_ai_suffix_message
from lib.utils.tool_calls_handler import ToolCallsHandler


if os.getenv('IS_DOCKER_CONTAINER'):
    load_dotenv()
else:
    env_file_path = '../.env'
    if not os.path.exists(env_file_path):
        raise FileNotFoundError(f'Could not find .env file at {env_file_path}')
    load_dotenv(env_file_path)

app = FastAPI()

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

agent_executor: AgentExecutor = None


@app.get('/session')
def get_session(session_id: str):
    if not session_id:
        return 'No session ID provided'

    session_id, executor = create_tool_agent(session_id)

    global agent_executor
    agent_executor = executor

    return {
        'session_id': session_id,
        'chat_history': agent_executor.memory.chat_memory.messages
    }


class AgentType(str, Enum):
    SQL = 'sql'
    OAF = 'oaf'
    TOOL = 'tool'


class SessionCreationRequest(BaseModel):
    agent_type: AgentType


@app.post('/session')
def create_session(body: SessionCreationRequest):
    print(f'agent type: {body.agent_type}')
    match body.agent_type:
        case AgentType.SQL:
            session_id, executor = create_sql_agent()
        case AgentType.OAF:
            session_id, executor = create_oaf_agent()
        case AgentType.TOOL:
            session_id, executor = create_tool_agent()
        case _:
            raise HTTPException(
                status_code=400, detail="Unsupported agent type")

    global agent_executor
    agent_executor = executor

    return {
        'session_id': session_id,
        'chat_history': agent_executor.memory.chat_memory.messages
    }


def get_tool_names(tool_classes: list[BaseTool]):
    overlapping_tools = filter(lambda t: type(t).__name__ in [
        tc.__name__ for tc in tool_classes], agent_executor.tools)
    return list(map(lambda t: t.name, overlapping_tools))


def create_data_event(data: Dict[Any, Any]):
    return f'data: {json.dumps(data)}\n\n'


async def stream_response(message: str):
    async for chunk in agent_executor.astream_log(
        {
            'input': message,
            'ai_suffix': select_ai_suffix_message(agent_executor, message)
        },
        include_names=['ChatOpenAI'],
    ):
        for op in chunk.ops:
            if op['op'] != 'add':
                continue

            value = op['value']

            if isinstance(value, FunctionMessage) and (tool_call := ToolCallsHandler.pop()):
                yield create_data_event({'tool_invokation': tool_call})

            if isinstance(value, FunctionMessage) and value.name in get_tool_names([
                    CustomQuerySQLDataBaseTool,
                    QueryOGCAPIFeaturesCollectionTool]):
                try:
                    data = json.loads(value.content)
                    yield create_data_event({
                        'geojson_path': f'/home/dev/master-thesis/src/langchain/output_data/{data["layer_name"]}.geojson',
                        'layer_name': data['layer_name']
                    })
                except:
                    print('Output type is not GeoJSON')

            if ('generations' in op['value']
                    and len(op['value']['generations'][0][0]['text']) > 0):
                # and op['value']['generations'][0][0]['type'] == 'ChatGenerationChunk'):
                yield create_data_event({'message_end': True})

            if isinstance(value, AIMessageChunk):
                yield create_data_event({'message': value.content})

    yield create_data_event({'stream_complete': True})

    assert len(ToolCallsHandler.tool_calls()) == 0


@app.get('/streaming-chat')
async def chat_endpoint(message: str):
    return StreamingResponse(stream_response(message), media_type='text/event-stream')


@app.post('/update-map-state')
async def update_map_state(state_data: Request):
    file_path = 'map_state_data.json'
    with open(file_path, 'w') as file:
        json.dump(await state_data.json(), file, indent=4)


@app.get('/geojson')
def get_geojson(geojson_path: str = "output.geojson"):
    with open(geojson_path, "r") as file:
        geojson_data = file.read()
    return json.loads(geojson_data)


@app.get('/history')
def history():
    if not agent_executor:
        return 'Agent executor is None'
    return agent_executor.memory.chat_memory.messages


@app.post("/upload")
def upload(files: List[UploadFile] = File(...), should_respond: bool = Form(...)):
    temp_dir = tempfile.gettempdir()
    for file in files:
        try:
            contents = file.file.read()
            save_loc = f'{temp_dir}/{file.filename}'
            with open(save_loc, 'wb') as f:
                f.write(contents)
        except Exception as e:
            print(f"There was an error uploading the file(s): {e}")
        finally:
            file.file.close()

    success_msg = f'I just uploaded file(s) {[file.filename for file in files]} to the /tmp in the current environment.'

    return StreamingResponse(stream_response(success_msg), media_type='text/event-stream')


@app.get('/docker')
def docker():
    return f'Docker: {os.getenv("IS_DOCKER_CONTAINER") or "false"}'
