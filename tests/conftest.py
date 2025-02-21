from typing import Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from app.db.database import Base, get_db
from app.main import app

@pytest.fixture(scope="module")
def test_db() -> Any:
    """Set up and tear down a test database using a temporary PostgreSQL container."""
    with PostgresContainer("postgres:17.2-alpine3.21") as postgres:
        engine = create_engine(postgres.get_connection_url())
        TestingSessionLocal = sessionmaker(bind=engine)
        Base.metadata.create_all(bind=engine)
        yield TestingSessionLocal
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(test_db: Any) -> Any:
    """Override the database dependency in FastAPI and return a test client."""
    def override_get_db() -> Any:
        db = test_db()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c
