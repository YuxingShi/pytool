#coding:utf-8
import asyncio
import websockets


async def hello(uri):
    async with websockets.connect(uri) as websocket:
        # await websocket.send("information")
        # print("< HELLO WORLD")
        # while True:
        recv_text = await websocket.recv()
        print("> {}".format(recv_text))

# asyncio.get_event_loop().run_until_complete(hello('ws://127.0.0.1:8765/information'))
asyncio.get_event_loop().run_until_complete(hello('ws://192.168.106.130:8765/information'))
# asyncio.get_event_loop().run_until_complete(hello('ws://192.168.106.133:8765/information'))
