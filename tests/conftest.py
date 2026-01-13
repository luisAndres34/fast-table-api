import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import get_session

sqlite_url = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    sqlite_url,
    connect_args = {"check_same_thread": False},
    poolclass=StaticPool,
)

@pytest_asyncio.fixture(name="session")
async def session_fixture():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(name="client")
async def client_fixture(session: AsyncSession):

    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
        ) as client:
        yield client

    app.dependency_overrides.clear()
