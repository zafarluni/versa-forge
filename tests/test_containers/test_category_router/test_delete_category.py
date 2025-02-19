# type: ignore
# ========================
# Test Delete Category
# ========================
def test_delete_category_and_verify(client):
    create_response = client.post("/categories/", json={"name": "CategoryToDelete"})
    category_id = create_response.json()["id"]
    delete_response = client.delete(f"/categories/{category_id}")
    assert delete_response.status_code == 204
    verify_response = client.get(f"/categories/{category_id}")
    assert verify_response.status_code == 404  # Confirm deletion

def test_delete_category_twice(client):
    create_response = client.post("/categories/", json={"name": "ToBeDeleted"})
    category_id = create_response.json()["id"]
    client.delete(f"/categories/{category_id}")
    response = client.delete(f"/categories/{category_id}")  # Second delete
    assert response.status_code == 204  # Should return 204 even if already deleted

def test_delete_category_with_non_integer_id(client):
    response = client.delete("/categories/abc")
    assert response.status_code == 422  # Validation error

def test_delete_category_with_large_nonexistent_id(client):
    response = client.delete("/categories/999999")
    assert response.status_code == 204  # Nonexistent categories should still return 204 (unless strict)

def test_delete_category_with_strict_flag_for_nonexistent(client):
    response = client.delete("/categories/999999?strict=true")
    assert response.status_code == 404  # Should return 404 since strict mode is on
