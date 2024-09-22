from arq.connections import create_pool
from config import REDIS_SETTINGS


async def push_new_job(job_name, query=None):
    redis = await create_pool(REDIS_SETTINGS)

    if query:
        job = await redis.enqueue_job(job_name, query)
    else:
        job = await redis.enqueue_job(job_name)
