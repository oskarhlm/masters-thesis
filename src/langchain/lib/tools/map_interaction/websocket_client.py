import asyncio
import websockets
import json


async def send_message():
    async with websockets.connect('ws://localhost:8765') as websocket:
        await websocket.send(json.dumps({'action': 'echo', 'data': 'Hello, WebSocket server!'}))
        await websocket.send(json.dumps({'action': 'uppercase', 'data': 'hello, websocket server!'}))
        await websocket.send(json.dumps({'action': 'invalid', 'data': 'Invalid action'}))

asyncio.get_event_loop().run_until_complete(send_message())
