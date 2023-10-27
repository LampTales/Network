import asyncio
import websockets


class DanmakuServer:
    def __init__(self):
        self.clients = set()


    async def reply(self, websocket):
        self.clients.add(websocket)
        try:
            async for message in websocket:
                await self.broadcast(message)
        finally:
            self.clients.remove(websocket)

    async def broadcast(self, message):
        for client in self.clients:
            await client.send(message)


if __name__ == "__main__":
    server = DanmakuServer()
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(server.reply, 'localhost', 8765))
    asyncio.get_event_loop().run_forever()
