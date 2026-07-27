# --- ARCHIVO: app/worker.py
from arq.connections import RedisSettings
from app.core.config import settings
from app.core.email import send_real_email
from app.core.logger import logger

async def send_email_task(ctx: dict, recipient_email: str, subject: str, html_content: str) -> None:
    """
    ARQ Background Task: Dispatches an email asynchronously via aiosmtplib.
    """
    logger.info(f"ARQ Worker processing email task for recipient: {recipient_email}")
    await send_real_email(
        recipient_email=recipient_email,
        subject=subject,
        html_content=html_content
    )


async def startup(ctx: dict) -> None:
    """
    Executed when the ARQ worker process starts up.
    """
    logger.info("ARQ Worker process started and connected to Redis.")


async def shutdown(ctx: dict) -> None:
    """
    Executed when the ARQ worker process shuts down.
    """
    logger.info("ARQ Worker process shutting down cleanly.")


class WorkerSettings:
    """
    ARQ Worker configuration class read by the ARQ CLI.
    Run command: uv run arq app.worker.WorkerSettings
    """
    functions = [send_email_task]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    max_jobs = 10
    job_timeout = 60
