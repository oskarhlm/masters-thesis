from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from interpreter import Interpreter
from dotenv import load_dotenv
import json

load_dotenv()

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

interpreter = Interpreter()
interpreter.model = "gpt-3.5-turbo"
interpreter.system_message += "You are a GIS agent living on a server, answering to a user on a web client."
interpreter.auto_run = True


@app.get("/chat")
def chat_endpoint(message: str):
    def event_stream():
        for result in interpreter.chat(message, stream=True, display=False):
            json_result = json.dumps(result)
            yield f'data: {json_result}\n\n'

        termination_data = json.dumps({"stream_complete": True})
        yield f'data: {termination_data}\n\n'

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get("/history")
def history_endpoint():
    return interpreter.messages

@app.delete('/history')
def history_delete_endpoint():
    num_messages = len(interpreter.messages)
    interpreter.messages.clear()
    return f'{num_messages} deleted from history.'
