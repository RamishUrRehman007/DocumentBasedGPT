import asyncio
import logging

import config
from arq import Retry, create_pool
from arq.connections import RedisSettings
from domains import chat_domain, file_domain

logger = logging.getLogger(__name__)


async def process_files(ctx):
    try:
        await file_domain.process_files()
    except (Exception, asyncio.CancelledError) as e:
        logger.exception("Failed to Process Files")


async def process_query(ctx, query):
    try:
        await chat_domain.process_query(query)
    except (Exception, asyncio.CancelledError) as e:
        logger.exception("Failed to Process Query")


async def startup(*args, **kwargs) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)-5.5s [%(name)s:%(lineno)s][%(threadName)s] %(message)s",
        level=config.LOG_LEVEL,
    )


# WorkerSettings defines the settings to use when creating the work,
# it's used by the arq cli.
# For a list of available settings, see https://arq-docs.helpmanual.io/#arq.worker.Worker
class WorkerSettings:
    functions = [process_files, process_query]
    redis_settings = config.REDIS_SETTINGS
    job_timeout = 86400
    on_startup = startup


if __name__ == "__main__":
    asyncio.run(main())
