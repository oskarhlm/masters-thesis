from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from interpreter import Interpreter
from dotenv import load_dotenv
import json
import tempfile
from typing import List, Dict, Any


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
interpreter.system_message += "Every response that needs to be formatted inside <pre> tags should be surrounded with triple backticks (```optional programming language specification\n content here```)"
interpreter.auto_run = True

def createDataEvent(data: Dict[Any, Any]):
    return f'data: {json.dumps(data)}\n\n'


@app.get("/chat")
def chat_endpoint(message: str):
    def event_stream():
        for result in interpreter.chat(message, stream=True, display=False):
            yield createDataEvent(result)
        yield createDataEvent({"stream_complete": True})

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get("/history")
def history_endpoint():
    return interpreter.messages

@app.delete('/history')
def history_delete_endpoint():
    num_messages = len(interpreter.messages)
    interpreter.messages.clear()
    return f'{num_messages} deleted from history.'


@app.post("/upload")
def upload(files: List[UploadFile] = File(...), should_respond: bool = Form(...)):
    print(should_respond)
    def event_stream():
        temp_dir = tempfile.gettempdir()
        for file in files:
            try:
                contents = file.file.read()
                save_loc = f'{temp_dir}/{file.filename}'
                with open(save_loc, 'wb') as f:
                    f.write(contents)
            except Exception:
                # yield createDataEvent({"message": "There was an error uploading the file(s)"})
                pass
            finally:
                file.file.close()

        success_msg = f"File(s) {[file.filename for file in files]} were just uploaded into the /tmp directory in your environment."
        
        if should_respond:
            success_msg += " Ask the user what he/she wants to do with these, in one or two short sentences."
            for result in interpreter.chat({"role": "assistant", 'message': success_msg}, stream=True, display=False):
                yield createDataEvent(result)
            yield createDataEvent({"stream_complete": True})
        else: 
            interpreter.messages.append({'role': 'assistant', 'message': success_msg})

    return StreamingResponse(event_stream(), media_type='text/event-stream')


@app.get("/test")
def chat_endpoint():
    def event_stream():
        message = "Some files were recently uploaded to the /tmp folder. Ask the user what to do with them."
        for result in interpreter.chat(message, stream=True, display=False):
            yield createDataEvent(result)
        yield createDataEvent({"stream_complete": True})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
