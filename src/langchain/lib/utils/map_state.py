import json


def load_map_state():
    map_state_path = '/home/dev/master-thesis/src/langchain/map_state_data.json'
    try:
        with open(map_state_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return {"error": "File not found"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format"}
