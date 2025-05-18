# mypy: ignore-errors
from typing import AsyncGenerator
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from testcontainers.postgres import PostgresContainer
from app.db.database import Base, get_db
from app.main import app


@pytest.fixture(scope="module")
async def async_test_db():
    """Set up and tear down an async test database using a temporary PostgreSQL container."""
    with PostgresContainer("postgres:17.2-alpine3.21") as postgres:
        connection_url = postgres.get_connection_url().replace("postgresql", "postgresql+asyncpg", 1)
        engine = create_async_engine(connection_url)
        AsyncTestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield AsyncTestingSessionLocal

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.fixture(scope="module")
async def client(async_test_db):
    """Async client fixture with database override"""

    async def override_get_db():
        async with async_test_db() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
