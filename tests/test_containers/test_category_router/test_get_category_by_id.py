# # mypy: ignore-errors
# # ========================
# # Test Get Category by ID
# # ========================

# def test_get_category_with_invalid_id(client):
#     """Ensure retrieving a category with a non-integer ID fails validation."""
#     response = client.get("/categories/abc")  # Non-numeric ID
#     assert response.status_code == 422


# def test_get_category_with_negative_id(client):
#     """Ensure retrieving a category with a negative ID returns 404."""
#     response = client.get("/categories/-1")
#     assert response.status_code == 404


# def test_get_category_with_large_nonexistent_id(client):
#     """Ensure retrieving a non-existent category returns 404."""
#     response = client.get("/categories/999999")
#     assert response.status_code == 404


# def test_get_existing_category(client):
#     """Ensure retrieving an existing category returns the correct data."""
#     create_response = client.post("/categories/", json={"name": "TestCategory"})
#     category_id = create_response.json()["id"]

#     response = client.get(f"/categories/{category_id}")
#     assert response.status_code == 200

#     data = response.json()
#     assert data["id"] == category_id
#     assert data["name"] == "TestCategory"
#     assert "description" in data
#     assert "created_at" in data


# def test_get_deleted_category(client):
#     """Ensure retrieving a deleted category returns 404."""
#     create_response = client.post("/categories/", json={"name": "ToDelete"})
#     category_id = create_response.json()["id"]
#     client.delete(f"/categories/{category_id}")  # Delete the category

#     response = client.get(f"/categories/{category_id}")
#     assert response.status_code == 404


# # def test_get_category_raises_exception(client, mocker):
# #     """Ensure exception handling works when a database failure occurs while retrieving a category."""
# #     mocker.patch("app.services.categories_service.CategoryService.get_category_by_id", side_effect=Exception("DB Error"))

# #     response = client.get("/categories/1")
# #     assert response.status_code == 500
# #     assert response.json()["error"]["message"] == "Internal Server Error"
