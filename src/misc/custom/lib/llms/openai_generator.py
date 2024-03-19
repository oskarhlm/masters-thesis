from typing import Callable, Generator, Any, Union
from .base_llm import BaseLLM


from openai import OpenAI


class OpenAIGenerator(BaseLLM):

    def __init__(self) -> None:
        super().__init__()
        self.client = OpenAI()
        self.model_name = 'gpt-4-1106-preview'

    def chat(
        self,
        prompt: str,
        stream=True,
        callback: Union[Callable[[str], None], None] = None,
        tools=[],
        *args,
        **kwargs
    ) -> Generator[str, Any, None]:
        self.messages.append({'role': 'user', 'content': prompt})

        stream = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.messages,
            stream=True,
            tools=tools,
            **kwargs
        )
        response = ''
        for chunk in stream:
            print(chunk)
            chunk_content = chunk.choices[0].delta.content
            if chunk_content is not None:
                response += chunk_content
                yield chunk_content
                if callback:
                    callback(chunk_content)

        self.messages.append({'role': 'assistant', 'content': response})
