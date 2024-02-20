from enum import Enum
import os
import json
from typing import Dict, Any, List
import re

from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException, WebSocket
from dotenv import load_dotenv
from langchain_core.agents import AgentStep, AgentAction
from langchain.agents import AgentExecutor
from langchain.tools import BaseTool
from langchain_core.messages import AIMessageChunk, FunctionMessage
from fastapi import FastAPI, UploadFile, File, Form
import tempfile

from lib.agents.tool_agent import create_tool_agent, MEMORY_KEY
from lib.agents.sql_agent.agent import create_sql_agent, CustomQuerySQLDataBaseTool
from lib.agents.oaf_agent.agent import create_oaf_agent
from lib.tools.oaf_tools.query_collection import QueryOGCAPIFeaturesCollectionTool
from lib.utils.ai_suffix_selection import select_ai_suffix_message
# from lib.tools.map_interaction.set_layer_paint import SetMapLayerPaintTool

from pydantic import BaseModel


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


def create_data_event(data: Dict[Any, Any]):
    return f'data: {json.dumps(data)}\n\n'


agent_executor: AgentExecutor = None


@app.get('/session')
def get_session(session_id: str):
    if not session_id:
        return 'No session ID provided'

    session_id, executor = create_tool_agent(session_id)
    print(session_id)

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


@app.get('/chat')
def chat_endpoint(message: str):
    def event_stream():
        for chunk in agent_executor.stream({'input': message, MEMORY_KEY: []}):
            if 'actions' in chunk:
                actions: List[AgentAction] = chunk['actions']
                for action in actions:
                    yield create_data_event({
                        'message': f"Calling Tool `{action.tool}` with input `{action.tool_input}`"
                    })
            elif 'steps' in chunk:
                steps: List[AgentStep] = chunk['steps']
                for step in steps:
                    yield create_data_event({
                        'message': f'Got result: `{step.observation}`'
                    })
            if 'output' in chunk:
                output: str = chunk['output']
                yield create_data_event({'message': output})
        yield create_data_event({'stream_complete': True})

    return StreamingResponse(event_stream(), media_type='text/event-stream')


def get_tool_names(tool_classes: list[BaseTool]):
    overlapping_tools = filter(lambda t: type(t).__name__ in [
        tc.__name__ for tc in tool_classes], agent_executor.tools)
    return list(map(lambda t: t.name, overlapping_tools))


async def stream_response(message: str):
    tool_calls = {}

    async for chunk in agent_executor.astream_log(
        {
            'input': message,
            'ai_suffix': select_ai_suffix_message(agent_executor, message)
        },
        include_names=['ChatOpenAI']
    ):
        for op in chunk.ops:
            # print(op)
            if op['op'] != 'add':
                continue

            value = op['value']

            # if isinstance(value, FunctionMessage) and value.name in get_tool_names([
            #         SetMapLayerPaintTool]):
            #     print(value.name, json.loads(value.content))
            #     await ws.send_json(json.loads(value.content))

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

            if 'generations' in op['value'] and len(op['value']['generations'][0][0]['text']) > 0:
                yield create_data_event({'message_end': True})

            if not isinstance(value, AIMessageChunk):
                continue

            if 'tool_calls' in value.additional_kwargs:
                tool_call = value.additional_kwargs['tool_calls'][0]
                if tool_call['index'] not in tool_calls:
                    if len(tool_calls.keys()) > 0:
                        yield create_data_event({'message': '\n'})
                    tool_calls[tool_call['index']] = {
                        'id': tool_call['id'],
                        'name': tool_call['function']['name'],
                        'arguments': ''
                    }
                    yield create_data_event({'tool_invokation': f'Using tool: {tool_call["function"]["name"]}\n'})
                else:
                    tool_calls[tool_call['index']
                               ]['arguments'] += tool_call['function']['arguments']
                    yield create_data_event({'tool_arguments': tool_call['function']['arguments']})
                continue

            yield create_data_event({'message': value.content})

    yield create_data_event({'stream_complete': True})


@app.get('/streaming-chat')
async def chat_endpoint(message: str):
    return StreamingResponse(stream_response(message), media_type='text/event-stream')


@app.get('/geojson')
def get_geojson(geojson_path: str = "output.geojson"):
    with open(geojson_path, "r") as file:
        geojson_data = file.read()
    return json.loads(geojson_data)


# global ws


# class WebSocketManager:
#     def __init__(self):
#         self.clients: List[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.clients.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         self.clients.remove(websocket)

#     async def send_message(self, message: str, client: WebSocket):
#         await client.send_text(message)

# websocket_manager = WebSocketManager()

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket_manager.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_json()
#             # Handle received data
#             await websocket.send_text(f"Response to client: {data}")
#     except Exception as e:
#         print(f"WebSocket Error: {e}")
#     finally:
#         websocket_manager.disconnect(websocket)

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
