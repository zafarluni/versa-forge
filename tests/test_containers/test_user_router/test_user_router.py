# mypy: ignore-errors
import pytest

# Constants for test user payloads
TEST_USER = {
    "username": "testuser",
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "Strongp@ssword1",
}
DUP_USER = {
    "username": "dupuser",
    "full_name": "Dup User",
    "email": "dup@example.com",
    "password": "Strongp@ssword1",
}
LOGIN_USER = {
    "username": "loginuser",
    "full_name": "Login User",
    "email": "login@example.com",
    "password": "Strongp@ssword1",
}
ME_USER = {
    "username": "meuser",
    "full_name": "Me User",
    "email": "me@example.com",
    "password": "Strongp@ssword1",
}


@pytest.mark.asyncio
async def test_register_user_returns_created(client):
    """
    GIVEN valid user data
    WHEN POST /users/register is called
    THEN returns 201 and echoes username and email
    """
    response = await client.post("/users/register", json=TEST_USER)
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == TEST_USER["username"]
    assert body["email"] == TEST_USER["email"]


@pytest.mark.asyncio
async def test_register_duplicate_user_returns_error(client):
    """
    GIVEN a user is already registered
    WHEN POST /users/register is called twice with same payload
    THEN second call returns 400 with "already" in message
    """
    await client.post("/users/register", json=DUP_USER)
    response = await client.post("/users/register", json=DUP_USER)
    assert response.status_code == 400
    assert "already" in response.text.lower()


@pytest.mark.asyncio
async def test_login_success_returns_token(client):
    """
    GIVEN a registered user
    WHEN POST /users/login with correct credentials
    THEN returns 200 and includes access_token
    """
    await client.post("/users/register", json=LOGIN_USER)
    login_payload = {"username": LOGIN_USER["username"], "password": LOGIN_USER["password"]}
    response = await client.post("/users/login", data=login_payload)
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body


@pytest.mark.asyncio
async def test_login_failure_with_invalid_credentials(client):
    """
    GIVEN invalid credentials
    WHEN POST /users/login
    THEN returns 401 Unauthorized
    """
    response = await client.post("/users/login", data={"username": "nope", "password": "nope"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_info(client):
    """
    GIVEN a valid bearer token
    WHEN GET /users/me
    THEN returns 200 and correct username
    """
    # Register and login to obtain token
    await client.post("/users/register", json=ME_USER)
    login_resp = await client.post(
        "/users/login",
        data={"username": ME_USER["username"], "password": ME_USER["password"]},
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = await client.get("/users/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == ME_USER["username"]
