"""Async SQLAlchemy session and engine."""
from collections.abc import AsyncGenerator

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

_eng_kwargs = {}
if ":memory:" in settings.database_url:
    _eng_kwargs["connect_args"] = {"check_same_thread": False}
    _eng_kwargs["poolclass"] = pool.StaticPool

engine = create_async_engine(
    settings.database_url,
    echo=False,
    **_eng_kwargs,
)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
