# mypy: ignore-errors
import pytest

# ========================
# Test Category Creation
# ========================

@pytest.mark.parametrize("name, description, expected_status", [
    ("Valid Category", "A valid test category", 201),  # ✅ Valid case
    ("No Desc Category", None, 201),  # ✅ `None` description is allowed
    ("", "Invalid", 422),  # ✅ Empty name should fail
    ("   ", "Invalid", 422),  # ✅ Name with only spaces should fail
    ("@#$%^&*", "Invalid", 422),  # ✅ Special characters should fail
    ("A" * 101, "Too long", 422),  # ✅ Exceeding max length (101 chars)
    ("A", "Too short", 422),  # ✅ Less than 5 chars should fail
    ("ABCD", "One char short", 422),  # ✅ 4 chars should fail
    ("Valid-Name", "Hyphens allowed", 201),  # ✅ Hyphen allowed
    ("O'Connor", "Apostrophe allowed", 201),  # ✅ Apostrophe allowed
    ("12345", "Numbers only", 201),  # ✅ Numbers allowed
])
def test_create_category_various_cases(client, name, description, expected_status):
    """Test category creation with various name inputs."""
    response = client.post("/categories/", json={"name": name, "description": description})
    assert response.status_code == expected_status

def test_create_large_number_of_categories(client):
    """Test the creation of multiple categories to ensure pagination works correctly."""
    response = client.get("/categories/?limit=100") 
    assert response.status_code == 200
    existing_categories = len(response.json())

    for i in range(20):
        client.post("/categories/", json={"name": f"Category {i}"})

    response = client.get("/categories/?limit=100") 
    assert response.status_code == 200
    assert len(response.json()) == (20 + existing_categories)

def test_create_duplicate_category_case_insensitive(client):
    """Ensure category names are case insensitive and should not allow duplicates."""
    client.post("/categories/", json={"name": "DuplicateCase"})  # First request
    response = client.post("/categories/", json={"name": "duplicatecase"})  # Duplicate in lowercase

    assert response.status_code == 400  # Expect HTTP 400 Bad Request

    response_data = response.json()

    # ✅ Correct error structure validation
    assert "error" in response_data
    assert "message" in response_data["error"]
    assert "duplicate" in response_data["error"]["message"].lower()


# ========================
# Test Exception Handling
# ========================

# def test_create_category_raises_exception(client, mocker):
#     """Ensure exception handling works when a database failure occurs."""
#     mocker.patch("app.services.categories_service.CategoryService.create_category", side_effect=Exception("DB Error"))
#     response = client.post("/categories/", json={"name": "TestFail"})

#     assert response.status_code == 500
#     assert "detail" in response.json() 
#     assert response.json()["detail"] in ["Internal Server Error", "DB Error"]
