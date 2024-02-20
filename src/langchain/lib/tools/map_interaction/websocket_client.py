import asyncio
import websockets
import json
from fastapi import WebSocket


# async def send_message():
#     async with websockets.connect('ws://localhost:8765') as websocket:
#         await websocket.send(json.dumps({'action': 'echo', 'data': 'Hello, WebSocket server!'}))
#         await websocket.send(json.dumps({'action': 'uppercase', 'data': 'hello, websocket server!'}))
#         await websocket.send(json.dumps({'action': 'invalid', 'data': 'Invalid action'}))

# asyncio.get_event_loop().run_until_complete(send_message())


# async def echo(websocket, path):
#     async for message in websocket:
#         await websocket.send(message * 2)

# asyncio.get_event_loop().run_until_complete(
#     websockets.serve(echo, 'localhost', 8765))
# asyncio.get_event_loop().run_forever()
