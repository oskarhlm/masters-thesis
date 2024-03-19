from typing import Dict, Any
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from fastapi.responses import StreamingResponse

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
        yield createDataEvent({"message": message})
        yield createDataEvent({"stream_complete": True})

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get('/docker')
def docker():
    return f'Docker: {os.getenv("IS_DOCKER_CONTAINER") or "false"} ({os.getenv("IS_DOCKER_CONTAINER")})'