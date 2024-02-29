import os
import json
from typing import Dict, Any, List, Union, Sequence
import ast

from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException, Request
from fastapi import FastAPI, UploadFile, File
from dotenv import load_dotenv
from langchain.agents import AgentExecutor
from langchain.tools import BaseTool
from langchain_core.messages import (
    AIMessageChunk, FunctionMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage)
from pydantic import BaseModel
from langgraph.pregel import Pregel
from contextlib import asynccontextmanager
from langchain_core.messages import BaseMessage

from lib.agents.tool_agent import create_tool_agent_executor
from lib.agents.sql_agent.agent import create_sql_agent_executor, CustomQuerySQLDataBaseTool
from lib.tools.map_interaction.publish_geojson import PublishGeoJSONTool
from lib.agents.oaf_agent.agent import create_oaf_agent_executor
from lib.tools.oaf_tools.query_collection import QueryOGCAPIFeaturesCollectionTool
from lib.utils.ai_suffix_selection import select_ai_suffix_message
from lib.utils.tool_calls_handler import ToolCallsHandler
from lib.agents.multi_agent.agent import create_multi_agent_runnable
from lib.utils.workdir_manager import WorkDirManager


if os.getenv('IS_DOCKER_CONTAINER'):
    load_dotenv()
else:
    env_file_path = '../.env'
    if not os.path.exists(env_file_path):
        raise FileNotFoundError(f'Could not find .env file at {env_file_path}')
    load_dotenv(env_file_path)


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    try:
        print('Booting up...')
        WorkDirManager()
        WorkDirManager.add_file('random.geojson', 'random.geojson')
        print(WorkDirManager.list_files())
        yield
    except asyncio.exceptions.CancelledError:
        pass
    finally:
        WorkDirManager.cleanup()
        print('Shutting down...')


app = FastAPI(lifespan=lifespan)

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


agent_executor: Union[AgentExecutor, Pregel] = None
session_id: str = None


def get_tool_names(tool_classes: list[BaseTool]):
    overlapping_tools = filter(lambda t: type(t).__name__ in [
        tc.__name__ for tc in tool_classes], agent_executor.tools)
    return list(map(lambda t: t.name, overlapping_tools))


@app.get('/session')
def get_session(session_id: str):
    if not session_id:
        return 'No session ID provided'

    session_id, executor = create_tool_agent_executor(session_id)

    global agent_executor
    agent_executor = executor

    return {
        'session_id': session_id,
        'chat_history': agent_executor.memory.chat_memory.messages
    }


class SessionCreationRequest(BaseModel):
    agent_type: str


@app.post('/session')
def create_session(body: SessionCreationRequest):
    global agent_type
    agent_type = body.agent_type

    match body.agent_type:
        case 'sql':
            session_id_lok, executor = create_sql_agent_executor()
        case 'oaf':
            session_id_lok, executor = create_oaf_agent_executor()
        case 'tool':
            session_id_lok, executor = create_tool_agent_executor()
        case 'lg-agent-supervisor':
            session_id_lok, executor = create_multi_agent_runnable()
        case _:
            raise HTTPException(
                status_code=400, detail="Unsupported agent type")

    global agent_executor, session_id
    agent_executor = executor
    session_id = session_id_lok

    return {'session_id': session_id_lok}


def create_data_event(data: Dict[Any, Any]):
    return f'data: {json.dumps(data)}\n\n'


async def stream_response(message: str):
    geojson_outputting_tools = get_tool_names([
        CustomQuerySQLDataBaseTool,
        QueryOGCAPIFeaturesCollectionTool,
        PublishGeoJSONTool
    ])

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

            if isinstance(value, FunctionMessage) and value.name in geojson_outputting_tools:
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


async def langgraph_stream_response(message: Union[str, BaseMessage, Sequence[BaseMessage]]):
    geojson_outputting_tools = ['add_geojson_to_map']

    if isinstance(message, str):
        messages = [HumanMessage(content=message)]
    elif isinstance(message, BaseMessage):
        messages = [message]
    elif isinstance(message, Sequence):
        messages = message

    async for s in agent_executor.astream(
        {
            "messages": messages
        },
        {"recursion_limit": 100, 'configurable': {'thread_id': session_id}},
    ):
        if "supervisor" in s:
            yield create_data_event({'message': f'Supervisor selected  {s["supervisor"]["next"]}'})
            yield create_data_event({'message_end': True})
            continue
        elif '__end__' not in s:
            for value in s.values():
                if 'messages' in value:
                    for message in value['messages']:
                        print(type(message))
                        if isinstance(message, AIMessage) and len(message.content) > 0:
                            yield create_data_event({'message': f'<strong>[{message.name}]</strong><br>{message.content}'})
                            yield create_data_event({'message_end': True})
                        elif isinstance(message, ToolMessage):
                            try:
                                yield create_data_event(ast.literal_eval(message.content))
                            except:
                                print('Output type is not GeoJSON')
            continue

        yield create_data_event({'stream_complete': True})


@app.get('/streaming-chat')
async def chat_endpoint(message: str):
    if isinstance(agent_executor, Pregel):
        return StreamingResponse(langgraph_stream_response(message), media_type='text/event-stream')
    return StreamingResponse(stream_response(message), media_type='text/event-stream')


@app.post('/update-map-state')
async def update_map_state(state_data: Request):
    file_path = 'map_state_data.json'
    with open(file_path, 'w') as file:
        json.dump(await state_data.json(), file, indent=4)


@app.get('/geojson')
def get_geojson(geojson_path: str = "output.geojson"):
    geojson_data = WorkDirManager.load_file(geojson_path)
    return json.loads(geojson_data)


@app.get('/history')
async def history():
    if not agent_executor:
        return 'Agent executor is None'

    if isinstance(agent_executor, Pregel):
        checkpoint = await agent_executor.checkpointer.aget({'configurable': {'thread_id': session_id}})
        return checkpoint['channel_values']['messages']

    return agent_executor.memory.chat_memory.messages


@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    for file in files:
        try:
            contents = file.file.read()
            WorkDirManager.add_file(
                filename=file.filename, content_or_path=contents)
        except Exception as e:
            print(f"There was an error uploading the file(s): {e}")
        finally:
            file.file.close()

    print(WorkDirManager.list_files())

    message = SystemMessage(
        content=f'File(s) {[file.filename for file in files]} where just to the /tmp in the current environment.')

    return StreamingResponse(langgraph_stream_response(message), media_type='text/event-stream')


@app.get('/docker')
def docker():
    return f'Docker: {os.getenv("IS_DOCKER_CONTAINER") or "false"}'
