import json
from lib.utils import tool
from lib.functions.code_execution import execute_python_code
from lib.llms.openai_generator import OpenAIGenerator

from dotenv import load_dotenv

load_dotenv('../.env')

client = OpenAIGenerator()

client.chat('write me a poem', callback=lambda x: print(x, end=''))


resp = """{'role': 'assistant',
 'content': None,
 'tool_calls': [{'id': 'call_o7uyztQLeVIoRdjcDkDJY3ni',
                 'type': 'function',
                 'function': {'name': 'execute_python_code',
                              'arguments': '{\n  "code": "print('hei')"\n}'}}]}"""


def execute_function_call(message):
    if message["tool_calls"][0]["function"]["name"] == "ask_database":
        query = json.loads(message["tool_calls"][0]
                           ["function"]["arguments"])["query"]

    else:
        results = f"Error: function {message['tool_calls'][0]['function']['name']} does not exist"
    return results


resp_json = json.dumps(resp)['tool_calls']

print(resp_json)

tools = {tool.schema['name']: tool for tool in [execute_python_code]}
print(tools)
