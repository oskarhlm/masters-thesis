import json
import os
from datetime import datetime

map_state_path = '/home/dev/master-thesis/src/langchain/map_state_data.json'


def load_map_state():
    try:
        with open(map_state_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return {"error": "File not found"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format"}


def get_map_state_modified_time():
    return datetime.fromtimestamp(os.path.getmtime(map_state_path))
