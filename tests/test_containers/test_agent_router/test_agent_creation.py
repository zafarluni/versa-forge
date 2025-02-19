import pytest

def test_create_private_agent(client):
    response = client.post(
        "/agents/",
        json={"name": "Private Agent", "is_public": False},
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Private Agent"
    assert data["is_public"] is False

def test_create_public_agent_without_categories(client):
    response = client.post(
        "/agents/",
        json={"name": "Public Agent", "is_public": True},
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Public agents must have categories"}

def test_create_public_agent_with_categories(client):
    response = client.post(
        "/agents/",
        json={"name": "Public Agent", "is_public": True, "categories": [1, 2]},
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Public Agent"
    assert data["is_public"] is True
    assert data["categories"] == [1, 2]
