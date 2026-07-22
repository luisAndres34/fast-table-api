import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

# 1. Force the environment to testing mode to bypass live Redis connection
from app.core.config import settings
settings.ENVIRONMENT = "testing"

from app.db.session import get_session
from app.main import app
FastAPICache.init(InMemoryBackend())

sqlite_url = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(sqlite_url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(name="session")
async def session_fixture():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest_asyncio.fixture(name="client")
async def client_fixture(session: AsyncSession):
    async def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def cleanup_engine():
    yield
    await engine.dispose()
