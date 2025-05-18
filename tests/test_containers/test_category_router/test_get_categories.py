# # mypy: ignore-errors
# import pytest
# # ========================
# # Test Get All Categories
# # ========================

# def test_get_all_categories_when_empty(client):
#     """Ensure retrieving categories when the database is empty returns an empty list."""
#     response = client.get("/categories/")
#     assert response.status_code == 200
#     assert response.json() == []


# def test_get_all_categories_with_pagination(client):
#     """Ensure retrieving multiple categories applies pagination correctly."""
#     for i in range(15):
#         client.post("/categories/", json={"name": f"Category {i}"})

#     response = client.get("/categories/?limit=10")
#     assert response.status_code == 200
#     assert len(response.json()) == 10  # Pagination should limit results to 10


# @pytest.mark.parametrize("limit, expected_count", [(5, 5), (10, 10), (20, 20)])
# def test_get_categories_with_various_limits(client, limit, expected_count):
#     """Ensure that different pagination limits return the expected number of results."""
#     for i in range(15):
#         client.post("/categories/", json={"name": f"TestCategory {i}"})

#     response = client.get(f"/categories/?limit={limit}")
#     assert response.status_code == 200
#     assert len(response.json()) == expected_count  # Ensures correct limit is applied


# def test_get_categories_response_structure(client):
#     """Ensure that retrieved categories contain expected fields."""
#     client.post("/categories/", json={"name": "TestCategory", "description": "Sample"})

#     response = client.get("/categories/")
#     assert response.status_code == 200
#     assert len(response.json()) > 0

#     category = response.json()[0]
#     assert "id" in category
#     assert "name" in category
#     assert "description" in category
#     assert "created_at" in category


# # def test_get_categories_raises_exception(client, mocker):
# #     """Ensure exception handling works when a database failure occurs while retrieving categories."""
# #     mocker.patch("app.services.categories_service.CategoryService.get_all_categories", side_effect=Exception("DB Error"))

# #     response = client.get("/categories/")
# #     assert response.status_code == 500
# #     assert response.json()["error"]["message"] == "Internal Server Error"
