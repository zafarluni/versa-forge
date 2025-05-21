# mypy: ignore-errors
# ========================
# Category GET Endpoint Tests
# ========================
import pytest
from fastapi import status
from httpx import AsyncClient

ENDPOINT = "/categories/"


@pytest.fixture(autouse=True)
def override_admin_user():
    """Force all requests to be from an admin user."""
    from app.core.auth import get_current_user
    from app.main import app as fastapi_app
    from app.schemas.user_schemas import UserResponse

    admin = UserResponse(
        id=1, username="admin", full_name="Admin User", email="admin@example.com", is_active=True, is_admin=True
    )
    fastapi_app.dependency_overrides[get_current_user] = lambda: admin
    yield
    fastapi_app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_category_invalid_id(client: AsyncClient):
    """Ensure retrieving a category with a non-integer ID fails validation."""
    resp = await client.get(f"{ENDPOINT}abc")
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_category_negative_id(client: AsyncClient):
    """Ensure retrieving a category with a negative ID returns 404."""
    resp = await client.get(f"{ENDPOINT}-1")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_category_not_found(client: AsyncClient):
    """Ensure retrieving a non-existent category returns 404."""
    resp = await client.get(f"{ENDPOINT}999999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in resp.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_get_existing_category(client: AsyncClient):
    """Ensure retrieving an existing category returns the correct data."""
    create_resp = await client.post(ENDPOINT, json={"name": "TestCategory", "description": "Desc"})
    assert create_resp.status_code == status.HTTP_201_CREATED
    created = create_resp.json()
    cat_id = created["id"]

    resp = await client.get(f"{ENDPOINT}{cat_id}")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["id"] == cat_id
    assert data["name"] == "TestCategory"
    assert "description" in data


@pytest.mark.asyncio
async def test_get_deleted_category(client: AsyncClient):
    """Ensure retrieving a deleted category returns 404."""
    create_resp = await client.post(ENDPOINT, json={"name": "ToDelete", "description": ""})
    assert create_resp.status_code == status.HTTP_201_CREATED
    cat_id = create_resp.json()["id"]
    del_resp = await client.delete(f"{ENDPOINT}{cat_id}")
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT

    resp = await client.get(f"{ENDPOINT}{cat_id}")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
