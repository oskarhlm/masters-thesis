import json


class ToolCallsHandler:
    file_path = '/home/dev/masters-thesis/src/langchain/tool_calls.json'

    @staticmethod
    def tool_calls():
        try:
            with open(ToolCallsHandler.file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    @staticmethod
    def _save_data(data):
        with open(ToolCallsHandler.file_path, 'w') as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def initialize_file():
        """Write an empty list [] to the file"""
        with open(ToolCallsHandler.file_path, 'w') as file:
            json.dump([], file)

    @staticmethod
    def push(value):
        """Push a value onto the list."""
        data = ToolCallsHandler.tool_calls()
        data.append(value)
        ToolCallsHandler._save_data(data)

    @staticmethod
    def pop():
        """Pop the first value from the list in a FIFO manner."""
        data = ToolCallsHandler.tool_calls()
        if data:
            value = data.pop(0)  # Remove the first element to ensure FIFO
            ToolCallsHandler._save_data(data)
            return value
        else:
            return None  # Return None if there's nothing to pop

    @staticmethod
    def read_key(key):
        """Read a specific key from the list of tool calls."""
        data = ToolCallsHandler.tool_calls()
        # Find the first occurrence of a dict with the specified key
        for item in data:
            if item.get("key") == key:
                return item
        return None
