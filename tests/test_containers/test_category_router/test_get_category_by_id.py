# type: ignore
# ========================
# Test Get Category by ID
# ========================
def test_get_category_with_invalid_id(client):
    response = client.get("/categories/abc")  # Non-integer ID
    assert response.status_code == 422

def test_get_category_with_negative_id(client):
    response = client.get("/categories/-1")
    assert response.status_code == 404

def test_get_category_with_large_nonexistent_id(client):
    response = client.get("/categories/999999")
    assert response.status_code == 404
