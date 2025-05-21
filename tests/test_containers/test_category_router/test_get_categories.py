# mypy: ignore-errors
import pytest
from fastapi import status
from httpx import AsyncClient

# ========================
# Category GET Endpoint Tests
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
async def test_get_category_success(client: AsyncClient):
    """Ensure retrieving an existing category by ID succeeds."""
    # Create a category first
    create_resp = await client.post(ENDPOINT, json={"name": "GetCat", "description": "Desc"})
    assert create_resp.status_code == status.HTTP_201_CREATED
    created = create_resp.json()
    cat_id = created["id"]

    # Retrieve by ID
    resp = await client.get(f"{ENDPOINT}{cat_id}")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == created


@pytest.mark.asyncio
async def test_get_category_not_found(client: AsyncClient):
    """Ensure retrieving a non-existent category returns 404."""
    resp = await client.get(f"{ENDPOINT}999999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in resp.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_get_all_categories_with_offset(client: AsyncClient):
    """Ensure offset parameter skips the correct number of records."""
    # Create 5 categories with valid names
    names = [f"Category{i}" for i in range(5)]
    for name in names:
        create_resp = await client.post(ENDPOINT, json={"name": name, "description": ""})
        assert create_resp.status_code == status.HTTP_201_CREATED

    # Fetch without offset
    resp_all = await client.get(ENDPOINT)
    assert resp_all.status_code == status.HTTP_200_OK
    all_list = resp_all.json()
    assert len(all_list) >= 5

    # Fetch with offset
    resp_offset = await client.get(f"{ENDPOINT}?offset=3&limit=10")
    assert resp_offset.status_code == status.HTTP_200_OK
    offset_list = resp_offset.json()
    returned_names = [c["name"] for c in offset_list]
    assert names[0] not in returned_names
    assert names[3] in returned_names


@pytest.mark.asyncio
async def test_get_all_categories_limit_bounds(client: AsyncClient):
    """Ensure limit respects bounds and validation."""
    # Minimum valid limit
    resp_min = await client.get(f"{ENDPOINT}?limit=1")
    assert resp_min.status_code == status.HTTP_200_OK
    assert len(resp_min.json()) <= 1

    # Maximum valid limit
    resp_max = await client.get(f"{ENDPOINT}?limit=100")
    assert resp_max.status_code == status.HTTP_200_OK
    assert len(resp_max.json()) <= 100

    # Invalid low limit
    resp_low = await client.get(f"{ENDPOINT}?limit=0")
    assert resp_low.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Invalid high limit
    resp_high = await client.get(f"{ENDPOINT}?limit=101")
    assert resp_high.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
