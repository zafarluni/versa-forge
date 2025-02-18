import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from app.db.database import Base, get_db
from app.main import app

# Fixture for setting up the test database per module
@pytest.fixture(scope="module")
def test_db():
    # Start a PostgreSQL container
    with PostgresContainer("postgres:17.2-alpine3.21") as postgres:
        # Create a new SQLAlchemy engine instance
        engine = create_engine(postgres.get_connection_url())
        # Create a configured "Session" class
        TestingSessionLocal = sessionmaker(bind=engine)
        # Create all tables in the database
        Base.metadata.create_all(bind=engine)
        
        # Provide the session to the tests
        yield TestingSessionLocal
        
        # Drop all tables in the database
        Base.metadata.drop_all(bind=engine)

# Fixture for overriding the get_db dependency in FastAPI
@pytest.fixture(scope="module")
def client(test_db):
    # Dependency override function
    def override_get_db():
        # Create a new database session
        db = test_db()
        try:
            yield db
        finally:
            db.close()

    # Override the default dependency with the test database session
    app.dependency_overrides[get_db] = override_get_db
    
    # Create a TestClient instance
    with TestClient(app) as c:
        yield c

# Test functions
def test_create_category(client):
    response = client.post("/categories/", json={"name": "Test Category", "description": "A test category"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Category"
    assert data["description"] == "A test category"
    assert "id" in data

def test_create_duplicate_category(client):
    input={"name": "Unique Category"}
    client.post("/categories/", json=input)
    response = client.post("/categories/", json={"name": "Unique Category"})
    assert response.status_code == 400
    assert response.json() == {"detail": f"Category with ${input['name']} name already exists."}

def test_get_all_categories(client):
    response = client.get("/categories/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_category_by_id(client):
    create_response = client.post("/categories/", json={"name": "Specific Category"})
    category_id = create_response.json()["id"]
    response = client.get(f"/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == "Specific Category"

def test_get_nonexistent_category(client):
    response = client.get("/categories/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}

def test_delete_category(client):
    create_response = client.post("/categories/", json={"name": "Category to Delete"})
    category_id = create_response.json()["id"]
    delete_response = client.delete(f"/categories/{category_id}")
    assert delete_response.status_code == 204
    get_response = client.get(f"/categories/{category_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_category(client):
    response = client.delete("/categories/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}
