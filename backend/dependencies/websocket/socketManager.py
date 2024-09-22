import asyncio

from .redisManager import IRedisConnectionManager


class WebSocketManager:
    def __init__(self, pubsub_client: IRedisConnectionManager):
        self.rooms = {}
        self.pubsub_client = pubsub_client

    async def add_user_to_room(self, chat_id: str, websocket) -> None:
        await websocket.accept()

        if chat_id in self.rooms:
            self.rooms[chat_id].append(websocket)
        else:
            self.rooms[chat_id] = [websocket]

            await self.pubsub_client.connect()
            pubsub_subscriber = await self.pubsub_client.subscribe(chat_id)
            asyncio.create_task(self._pubsub_data_reader(pubsub_subscriber))

    async def broadcast_to_room(self, chat_id: str, message: str) -> None:
        await self.pubsub_client.publish(chat_id, message)

    async def remove_user_from_room(self, chat_id: str, websocket) -> None:
        self.rooms[chat_id].remove(websocket)

        if len(self.rooms[chat_id]) == 0:
            del self.rooms[chat_id]
            await self.pubsub_client.unsubscribe(chat_id)

    async def _pubsub_data_reader(self, pubsub_subscriber):
        while True:
            message = await pubsub_subscriber.get_message(
                ignore_subscribe_messages=True
            )
            if message is not None:
                chat_id = message["channel"].decode("utf-8")
                all_sockets = self.rooms[chat_id]
                for socket in all_sockets:
                    data = message["data"].decode("utf-8")
                    await socket.send_text(data)
