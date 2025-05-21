# mypy: ignore-errors
import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.auth import get_current_user
from app.main import app as fastapi_app
from app.schemas.user_schemas import UserResponse

# Constants
ENDPOINT = "/categories/"
DEFAULT_PAYLOAD = {"name": "Test Category", "description": "A sample category"}

# Mock users
ADMIN_USER = UserResponse(
    id=1,
    username="admin",
    full_name="Admin User",
    email="admin@example.com",
    is_active=True,
    is_admin=True,
)
NON_ADMIN_USER = UserResponse(
    id=2,
    username="user",
    full_name="Regular User",
    email="user@example.com",
    is_active=True,
    is_admin=False,
)


@pytest.fixture(autouse=True)
def override_auth():
    """Override authentication to ADMIN_USER by default for all tests."""
    fastapi_app.dependency_overrides[get_current_user] = lambda: ADMIN_USER
    yield
    fastapi_app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_category_success(client: AsyncClient):
    """
    GIVEN an admin user
    WHEN POST /categories/ with valid payload
    THEN returns 201 and persisted category data
    """
    response = await client.post(ENDPOINT, json=DEFAULT_PAYLOAD)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert isinstance(data.get("id"), int)
    assert data["name"] == DEFAULT_PAYLOAD["name"]
    assert data["description"] == DEFAULT_PAYLOAD["description"]


@pytest.mark.asyncio
async def test_create_category_duplicate_error(client: AsyncClient):
    """
    GIVEN an existing category
    WHEN POST /categories/ with same payload twice
    THEN second request returns 400 Bad Request
    """
    # First creation
    first = await client.post(ENDPOINT, json=DEFAULT_PAYLOAD)
    assert first.status_code == status.HTTP_201_CREATED

    # Duplicate creation
    second = await client.post(ENDPOINT, json=DEFAULT_PAYLOAD)
    assert second.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in second.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_create_category_forbidden_for_non_admin(client: AsyncClient):
    """
    GIVEN a non-admin user
    WHEN POST /categories/
    THEN returns 403 Forbidden
    """
    fastapi_app.dependency_overrides[get_current_user] = lambda: NON_ADMIN_USER
    response = await client.post(ENDPOINT, json=DEFAULT_PAYLOAD)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "admin privileges required" in response.json().get("detail", "").lower()
