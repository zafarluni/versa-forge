# mypy: ignore-errors
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

from app.db.database import Base, get_db  # Import your Base and get_db
from app.main import app  # Import your FastAPI app


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:17.2-alpine3.21", driver=None) as postgres:
        yield postgres


@pytest.fixture(scope="session")
def db_url(postgres_container):
    # Get the sync URL (e.g., 'postgresql://user:password@host:port/dbname')
    raw_url = postgres_container.get_connection_url()
    # Convert to async psycopg3 URL for SQLAlchemy
    async_url = raw_url.replace("postgresql://", "postgresql+psycopg://")
    return async_url


@pytest.fixture(scope="session")
async def async_engine(db_url):
    engine = create_async_engine(db_url, poolclass=NullPool)
    # Create all tables once
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(async_engine):
    async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    from httpx import ASGITransport

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
