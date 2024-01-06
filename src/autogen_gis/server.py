from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import subprocess

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

@app.get('/')
def root():
    return f'hei hallo: {os.environ.get("PASS")} {subprocess.run(["python3", "--version"], capture_output=True, text=True)}'
    # return f'hei hallo: testing'