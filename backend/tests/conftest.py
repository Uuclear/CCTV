"""Pytest: test DB = in-memory SQLite + explicit schema (TestClient lifespan is flaky with async)."""
import asyncio
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest

import app.models  # noqa: F401 — register ORM tables
from app.db import engine
from app.models import Base


@pytest.fixture(scope="session", autouse=True)
def _init_test_schema() -> None:
    async def setup() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(setup())


@pytest.fixture
def client():
    from starlette.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c
