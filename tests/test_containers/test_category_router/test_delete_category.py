# mypy: ignore-errors
# ========================
# Test Delete Category
# ========================


def test_delete_category_and_verify(client):
    """Ensure a category can be deleted and is no longer accessible."""
    create_response = client.post("/categories/", json={"name": "CategoryToDelete"})
    category_id = create_response.json()["id"]
    delete_response = client.delete(f"/categories/{category_id}")
    assert delete_response.status_code == 204
    verify_response = client.get(f"/categories/{category_id}")
    assert verify_response.status_code == 404  # Confirm deletion


def test_delete_category_twice(client):
    """Ensure deleting an already deleted category still returns 204 (unless strict mode)."""
    create_response = client.post("/categories/", json={"name": "ToBeDeleted"})
    category_id = create_response.json()["id"]
    client.delete(f"/categories/{category_id}")

    response = client.delete(f"/categories/{category_id}")  # Second delete attempt
    assert response.status_code == 204  # Should return 204 unless strict mode is enabled


def test_delete_category_with_non_integer_id(client):
    """Ensure deleting a category with a non-integer ID fails validation."""
    response = client.delete("/categories/abc")
    assert response.status_code == 422  # Validation error


def test_delete_category_with_large_nonexistent_id(client):
    """Ensure deleting a large non-existent category ID returns 204 unless strict mode is used."""
    response = client.delete("/categories/999999")
    assert response.status_code == 204  # Nonexistent categories should still return 204 (unless strict)


def test_delete_category_with_strict_flag_for_nonexistent(client):
    """Ensure deleting a non-existent category with strict mode returns 404."""
    response = client.delete("/categories/999999?strict=true")
    assert response.status_code == 404  # Should return 404 since strict mode is on


# def test_delete_category_raises_exception(client, mocker):
#     """Ensure exception handling works when a database failure occurs during deletion."""
#     mocker.patch.object(CategoryService, "delete_category", side_effect=Exception("DB Error"))
#     response = client.delete("/categories/1")

#     print(response)
#     assert response.status_code == 500
#     assert response.json()["error"]["message"] == "Internal Server Error"
