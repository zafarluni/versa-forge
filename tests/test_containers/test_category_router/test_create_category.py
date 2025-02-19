# type: ignore
# ========================
# Test Category Creation
# ========================
def test_create_category_with_valid_data(client):
    response = client.post("/categories/", json={"name": "Valid Category", "description": "A valid test category"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Valid Category"
    assert "id" in data

def test_create_category_without_description(client):
    response = client.post("/categories/", json={"name": "No Desc Category"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "No Desc Category"
    assert "description" in data and data["description"] is None

def test_create_category_with_empty_name(client):
    response = client.post("/categories/", json={"name": "", "description": "Invalid"})
    assert response.status_code == 422  # Should fail validation

def test_create_category_with_spaces_in_name(client):
    response = client.post("/categories/", json={"name": "   ", "description": "Invalid"})
    assert response.status_code == 422  # Should fail validation

def test_create_category_with_long_name(client):
    long_name = "A" * 300  # Assuming max length is 255
    response = client.post("/categories/", json={"name": long_name, "description": "Too long"})
    assert response.status_code == 422  # Should fail validation

def test_create_category_with_special_characters(client):
    response = client.post("/categories/", json={"name": "@#$%^&*", "description": "Invalid"})
    assert response.status_code == 422  # Should fail validation if name has restrictions

def test_create_duplicate_category_case_insensitive(client):
    client.post("/categories/", json={"name": "DuplicateCase"})
    response = client.post("/categories/", json={"name": "duplicatecase"})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
