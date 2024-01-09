from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import json
import tempfile
from typing import List, Dict, Any
import os

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


@app.get("/chat")
def chat_endpoint(message: str):
    def event_stream():
        yield createDataEvent({'message': message})
        yield createDataEvent({"stream_complete": True})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/history")
def history_endpoint():
    return []


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
