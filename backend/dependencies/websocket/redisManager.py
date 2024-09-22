import asyncio
from abc import ABC, abstractmethod

import redis.asyncio as aioredis


class IRedisConnectionManager(ABC):
    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def publish(self, chat_id: str, message: str) -> None:
        pass

    @abstractmethod
    async def subscribe(self, chat_id: str) -> aioredis.Redis:
        pass

    @abstractmethod
    async def unsubscribe(self, chat_id: str) -> None:
        pass


class RedisPubSubManager(IRedisConnectionManager):
    def __init__(self, host="redis", port=6379):
        self.redis_host = host
        self.redis_port = port
        self.redis_connection = None
        self.pubsub = None

    async def connect(self) -> None:
        self.redis_connection = await aioredis.Redis(
            host=self.redis_host, port=self.redis_port, auto_close_connection_pool=False
        )
        self.pubsub = self.redis_connection.pubsub()

    async def publish(self, chat_id: str, message: str) -> None:
        await self.redis_connection.publish(chat_id, message)

    async def subscribe(self, chat_id: str) -> aioredis.Redis:
        await self.pubsub.subscribe(chat_id)
        return self.pubsub

    async def unsubscribe(self, chat_id: str) -> None:
        await self.pubsub.unsubscribe(chat_id)
