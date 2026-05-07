"""Async SQLAlchemy engine for education models (asyncpg)."""

from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings

settings = get_settings()
engine_async = create_async_engine(settings.async_database_url, echo=False)
async_session = async_sessionmaker(engine_async, expire_on_commit=False)


class BaseAsync(AsyncAttrs, DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        yield session
