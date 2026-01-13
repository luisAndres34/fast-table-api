from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import Annotated
from .config import settings

DATABASE_URL = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session():
    async with async_session_maker() as session:
        yield session

GetSession = Annotated[AsyncSession, Depends(get_session)]
