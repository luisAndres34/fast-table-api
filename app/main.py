from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
import redis.asyncio as redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import sentry_sdk

from app.core.config import settings
from app.core.logger import logger
from app.core.exceptions import integrity_error_handler
from app.api.v1.api import api_router

# Initialize Sentry SDK conditionally
if settings.SENTRY_DSN and settings.ENVIRONMENT != "testing":
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=True,
    )
    logger.info(f"Sentry error tracking initialized for environment: {settings.ENVIRONMENT}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events: Code executed before the application starts receiving requests,
    and after the application finishes handling requests.
    """
    if settings.ENVIRONMENT != "testing":
        redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=False)
        FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
        logger.info("Redis cache configured successfully.")

        yield

        await redis_client.close()
        logger.info("Redis connection closed.")
    else:
        yield

# Create the FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register global exception handlers
app.add_exception_handler(IntegrityError, integrity_error_handler)

app.include_router(api_router, prefix="/api/v1")