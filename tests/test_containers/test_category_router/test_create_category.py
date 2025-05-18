# mypy: ignore-errors
import pytest
import asyncio


@pytest.mark.asyncio
async def test_create_category_various_cases(client):
    test_cases = [
        ("Valid Category", "A valid test category", 201),
        ("No Desc Category", None, 201),
        ("", "Invalid", 422),
        ("   ", "Invalid", 422),
        ("@#$%^&*", "Invalid", 422),
        ("A" * 101, "Too long", 422),
        ("A", "Too short", 422),
        ("Valid-Name", "Hyphens allowed", 201),
        ("O'Connor", "Apostrophe allowed", 201),
        ("12345", "Numbers only", 201),
    ]

    for name, desc, expected in test_cases:
        response = await client.post("/categories/", json={"name": name, "description": desc})
        assert response.status_code == expected


@pytest.mark.asyncio
async def test_create_duplicate_category_case_insensitive(client):
    response1 = await client.post("/categories/", json={"name": "TestCategory", "description": "Original"})
    assert response1.status_code == 201

    response2 = await client.post("/categories/", json={"name": "testcategory", "description": "Duplicate"})
    assert response2.status_code == 400
    assert "duplicate" in response2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_category_database_error(mocker, client):
    mocker.patch(
        "app.services.categories_service.CategoryService.create_category", side_effect=Exception("Database error")
    )

    response = await client.post("/categories/", json={"name": "TestFail", "description": "Should fail"})

    assert response.status_code == 500
    assert "Internal Server Error" in response.text


@pytest.mark.asyncio
async def test_pagination_behavior(client):
    # Create 25 categories
    for i in range(25):
        await client.post("/categories/", json={"name": f"Category {i}", "description": "Test"})

    # Test default pagination (10 items)
    response = await client.get("/categories/")
    assert response.status_code == 200
    assert len(response.json()) == 10

    # Test larger limit
    response = await client.get("/categories/?limit=20")
    assert len(response.json()) == 20

    # Test offset
    response = await client.get("/categories/?offset=20")
    assert len(response.json()) == 5


@pytest.mark.asyncio
async def test_concurrent_category_creation(client):
    # Test concurrent requests handling
    responses = await asyncio.gather(
        client.post("/categories/", json={"name": "Concurrent1"}),
        client.post("/categories/", json={"name": "Concurrent2"}),
        client.post("/categories/", json={"name": "Concurrent3"}),
    )

    assert all(r.status_code == 201 for r in responses)
    assert len({r.json()["name"] for r in responses}) == 3


@pytest.mark.asyncio
async def test_category_lifecycle(client):
    # Create
    create_response = await client.post("/categories/", json={"name": "TestLifecycle", "description": "Lifecycle test"})
    assert create_response.status_code == 201
    category_id = create_response.json()["id"]

    # Read
    read_response = await client.get(f"/categories/{category_id}")
    assert read_response.status_code == 200
    assert read_response.json()["name"] == "TestLifecycle"

    # Update
    update_response = await client.put(f"/categories/{category_id}", json={"name": "UpdatedName"})
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "UpdatedName"

    # Delete
    delete_response = await client.delete(f"/categories/{category_id}")
    assert delete_response.status_code == 204

    # Verify deletion
    final_response = await client.get(f"/categories/{category_id}")
    assert final_response.status_code == 404
