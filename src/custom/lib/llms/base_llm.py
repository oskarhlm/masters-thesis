from typing import Generator, Any

import os


class BaseLLM():

    def __init__(self, config={}) -> None:
        self.model_name = 'gpt-4'
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.messages = []

    def chat(self, prompt: str) -> Generator[str, Any, None]:
        raise NotImplementedError()

    def history():
        return []
