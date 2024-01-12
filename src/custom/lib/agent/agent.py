import os
from typing import Generator, Any


class Agent():
    def __init__(self, llm_config) -> None:
        self.model = llm_config['model']
        self.api_key = llm_config['api_key']
