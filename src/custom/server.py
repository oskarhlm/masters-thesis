from lib.utils import tool
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import json
import tempfile
from typing import Annotated, List, Dict, Any
import os

from lib.llms.openai_generator import OpenAIGenerator
from lib.functions.code_execution import execute_python_code

if os.getenv('IS_DOCKER_CONTAINER'):
    load_dotenv()
else:
    env_file_path = "../.env"
    if not os.path.exists(env_file_path):
        raise FileNotFoundError(f"Could not find .env file at {env_file_path}")
    load_dotenv(env_file_path)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def createDataEvent(data: Dict[Any, Any]):
    return f'data: {json.dumps(data)}\n\n'


client = OpenAIGenerator()


@tool()
def plot_map(
    lat: Annotated[float, 'latitude'],
    lon: Annotated[float, 'longitude']
):
    """Plots a map at a given latitude and longitude."""
    pass


tools = [execute_python_code, plot_map]

tool_schemas = [{
    'type': 'function',
    'function': tool.schema
} for tool in tools]
print(json.dumps(tool_schemas, indent=4))


@app.get("/chat")
def chat_endpoint(message: str):
    def event_stream():
        for chunk_content in client.chat(message, callback=lambda x: print(x, end=''), tools=tool_schemas):
            data_event = createDataEvent({"chunk_content": chunk_content})
            yield data_event
        yield createDataEvent({"stream_complete": True})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/history")
def history_endpoint():
    return client.messages


@app.delete('/history')
def history_delete_endpoint():
    num_messages = 0
    return f'{num_messages} deleted from history.'


@app.post("/upload")
def upload(files: List[UploadFile] = File(...), should_respond: bool = Form(...)):
    print(should_respond)

    def event_stream():
        pass

    return StreamingResponse(event_stream(), media_type='text/event-stream')
