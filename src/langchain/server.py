import os
import json
from typing import Dict, Any, List

from fastapi.responses import StreamingResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_core.agents import AgentStep, AgentAction, AgentFinish

from lib.agents.tool_agent import create_tool_agent, MEMORY_KEY


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


agent_executor, memory = create_tool_agent()


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


@app.get('/history')
def history():
    return memory.chat_memory.messages if memory else []


@app.get('/docker')
def docker():
    return f'Docker: {os.getenv("IS_DOCKER_CONTAINER") or "false"}'
