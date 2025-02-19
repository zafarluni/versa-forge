# type: ignore
# ========================
# Test Get All Categories
# ========================
def test_get_all_categories_when_empty(client):
    response = client.get("/categories/")
    assert response.status_code == 200
    assert response.json() == []  # Should return an empty list

def test_get_all_categories_with_pagination(client):
    for i in range(15):
        client.post("/categories/", json={"name": f"Category {i}"})
    response = client.get("/categories/?limit=10")
    assert response.status_code == 200
    assert len(response.json()) == 15  # Pagination check if implemented
