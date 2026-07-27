from arq import create_pool
from arq.connections import ArqRedis, RedisSettings
from app.core.config import settings
from app.core.logger import logger

# Global ARQ Redis connection pool instance
arq_redis_pool: ArqRedis | None = None

async def create_arq_pool() -> ArqRedis:
    """
    Initializes the ARQ Redis connection pool on application startup.
    """
    global arq_redis_pool
    if settings.ENVIRONMENT != "testing":
        redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
        arq_redis_pool = await create_pool(redis_settings)
        logger.info("ARQ Redis pool initialized successfully.")
    return arq_redis_pool

async def close_arq_pool() -> None:
    """
    Closes the ARQ Redis connection pool on application shutdown.
    """
    global arq_redis_pool
    if arq_redis_pool:
        await arq_redis_pool.close()
        logger.info("ARQ Redis pool closed cleanly.")

async def enqueue_email_task(recipient_email: str, subject: str, html_content: str) -> None:
    """
    Safely enqueues an email dispatch job to the ARQ Redis queue.
    """
    global arq_redis_pool
    if arq_redis_pool:
        job = await arq_redis_pool.enqueue_job(
            "send_email_task",
            recipient_email=recipient_email,
            subject=subject,
            html_content=html_content
        )
        logger.info(f"Enqueued email task with Job ID: {job.job_id} for {recipient_email}")
    else:
        logger.warning("ARQ Redis pool is not initialized. Skipping email enqueue.")
