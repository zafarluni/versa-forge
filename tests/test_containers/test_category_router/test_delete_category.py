# mypy: ignore-errors
import pytest
from fastapi import status
from httpx import AsyncClient

# ========================
# Category Router Integration Tests
# ========================

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
async def test_create_and_get_category(client: AsyncClient):
    """Create a category then retrieve it by ID and list all."""
    create_resp = await client.post(ENDPOINT, json={"name": "NewCat", "description": "Desc"})
    assert create_resp.status_code == status.HTTP_201_CREATED
    created = create_resp.json()
    cat_id = created["id"]

    get_resp = await client.get(f"{ENDPOINT}{cat_id}")
    assert get_resp.status_code == status.HTTP_200_OK
    assert get_resp.json() == created

    list_resp = await client.get(ENDPOINT)
    assert list_resp.status_code == status.HTTP_200_OK
    assert any(c["id"] == cat_id for c in list_resp.json())


@pytest.mark.asyncio
async def test_update_category(client: AsyncClient):
    """Create then update a category and verify the update."""
    created = (await client.post(ENDPOINT, json={"name": "OldName", "description": "OldDesc"})).json()
    cat_id = created["id"]

    updated = (await client.put(f"{ENDPOINT}{cat_id}", json={"name": "NewName", "description": "NewDesc"})).json()
    assert updated["id"] == cat_id
    assert updated["name"] == "NewName"
    assert updated["description"] == "NewDesc"

    assert (await client.get(f"{ENDPOINT}{cat_id}")).json() == updated


@pytest.mark.asyncio
async def test_delete_category_behavior(client: AsyncClient):
    """Test normal, repeated, and strict deletion behavior."""
    created = (await client.post(ENDPOINT, json={"name": "DelCat"})).json()
    cid = created["id"]

    assert (await client.delete(f"{ENDPOINT}{cid}")).status_code == status.HTTP_204_NO_CONTENT
    assert (await client.delete(f"{ENDPOINT}{cid}")).status_code == status.HTTP_204_NO_CONTENT
    assert (await client.delete(f"{ENDPOINT}{cid}?strict=true")).status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_non_admin_forbidden(client: AsyncClient):
    """Verify non-admin cannot create, update, or delete."""
    from app.core.auth import get_current_user
    from app.main import app as fastapi_app
    from app.schemas.user_schemas import UserResponse

    non_admin = UserResponse(
        id=2, username="user", full_name="User", email="user@example.com", is_active=True, is_admin=False
    )
    fastapi_app.dependency_overrides[get_current_user] = lambda: non_admin

    assert (await client.post(ENDPOINT, json={"name": "ValidName"})).status_code == status.HTTP_403_FORBIDDEN
    assert (
        await client.put(f"{ENDPOINT}1", json={"name": "AnotherValidName"})
    ).status_code == status.HTTP_403_FORBIDDEN
    assert (await client.delete(f"{ENDPOINT}1")).status_code == status.HTTP_403_FORBIDDEN
    fastapi_app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_invalid_inputs(client: AsyncClient):
    """Ensure invalid inputs raise proper errors."""
    assert (await client.post(ENDPOINT, json={"name": "a"})).status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (await client.get(f"{ENDPOINT}9999")).status_code == status.HTTP_404_NOT_FOUND
