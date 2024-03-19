from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage, StreamingChunk
import os
from dotenv import load_dotenv
from haystack.components.embedders import SentenceTransformersDocumentEmbedder

load_dotenv('../.env')

em = SentenceTransformersDocumentEmbedder()

client = OpenAIChatGenerator()

def on_new_token(chunks: [StreamingChunk]):
    print(chunks.content, end='')

client = OpenAIChatGenerator(api_key=os.environ.get("OPENAI_API_KEY"), model_name='gpt-3.5-turbo', streaming_callback=on_new_token)

# Try it out
while True:
    user_input = input("Human (type 'exit' or 'quit' to quit, 'memory' for agent's memory): ")
    if user_input.lower() == "exit" or user_input.lower() == "quit":
        break
    else:
        assistant_response = client.run(
            	  [ChatMessage.from_user(user_input)]
        )
        print("\nAssistant:", assistant_response)