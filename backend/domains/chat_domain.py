import json
import logging

from config import OPEN_AI_API_KEY, PINECONE_API_KEY
from dependencies.llm_service import (
    DocumentGPTSystem,
    EmbeddingsProvider,
    QuestionAnsweringService,
    VectorStoreManager,
)
from dependencies.websocket.redisManager import RedisPubSubManager
from domains.common import push_new_job


async def create_process_query(query):
    await push_new_job("process_query", query)


async def process_query(query: str):
    api_key_openai = OPEN_AI_API_KEY
    api_key_pinecone = PINECONE_API_KEY

    embeddings_provider = EmbeddingsProvider(api_key=api_key_openai)
    vector_store_manager = VectorStoreManager(
        api_key=api_key_pinecone, index_name="ramishtest1"
    )
    qa_service = QuestionAnsweringService(api_key=api_key_openai)

    answer = await DocumentGPTSystem(
        embeddings_provider=embeddings_provider,
        vector_store_manager=vector_store_manager,
        qa_service=qa_service,
    ).process_query(query)

    pubsub_manager = RedisPubSubManager()
    await pubsub_manager.connect()
    chat_id = "document-based-gpt"
    message = {
        "user_id": 2,
        "chat_id": chat_id,
        "message": str(answer),
    }
    message_json = json.dumps(message)

    logging.info(f"Message from OpenAI Document Based GPT: {message}")

    await pubsub_manager.publish(chat_id, message_json)
