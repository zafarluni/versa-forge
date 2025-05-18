# # mypy: ignore-errors
# import logging
# import pytest
# # ========================
# # Test User Registration
# # ========================

# # Initialize logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # @pytest.mark.parametrize(
# #     "username, email, password, expected_status",
# #     [
# #         ("validuser", "valid@example.com", "SecurePass123!", 201),  # Valid case
# #         ("", "invalidemail", "SecurePass123!", 422),  # Empty username
# #         ("short", "invalidemail", "SecurePass123!", 422),  # Username too short
# #         ("validuser", "invalidemail", "", 422),  # Empty password
# #         ("duplicateuser", "duplicate@example.com", "SecurePass123!", 400),  # Duplicate email
# #     ],
# # )
# # def test_register_user_various_cases(client, username, email, password, expected_status):
# #     """Test user registration with various inputs."""
# #     user_data = {"username": username, "email": email, "password": password}
# #     response = client.post("/users/register", json=user_data)
# #     assert response.status_code == expected_status


# def test_register_duplicate_user(client):
#     """Ensure duplicate users cannot be registered."""
#     user_data = {"username": "duplicateuser", "email": "duplicate@example.com", "password": "SecurePass123!"}
#     client.post("/users/register", json=user_data)  # First registration
#     response = client.post("/users/register", json=user_data)  # Duplicate registration
#     assert response.status_code == 400
#     assert "error" in response.json()
#     assert "message" in response.json()["error"]
#     assert "duplicate" in response.json()["error"]["message"].lower()


# # ========================
# # Test User Login
# # ========================


# # def test_login_with_valid_credentials(client):
# #     """Ensure a user can log in with valid credentials."""
# #     # Register a user first
# #     user_data = {"username": "testuser", "email": "test@example.com", "password": "SecurePass123!"}
# #     client.post("/users/register", json=user_data)
# #     # Attempt to log in
# #     login_data = {"username": "testuser", "password": "SecurePass123!"}
# #     response = client.post("/users/login", data=login_data)
# #     assert response.status_code == 200
# #     assert "access_token" in response.json()
# #     assert response.json()["token_type"] == "bearer"


# # def test_login_with_invalid_credentials(client):
# #     """Ensure login fails with invalid credentials."""
# #     login_data = {"username": "nonexistentuser", "password": "wrongpassword"}
# #     response = client.post("/users/login", data=login_data)
# #     assert response.status_code == 401
# #     assert "detail" in response.json()
# #     assert response.json()["detail"] == "Incorrect username or password"


# # ========================
# # Test Get Current User Info
# # ========================


# # def test_get_current_user_info(client):
# #     """Ensure the current user's info can be retrieved using a valid token."""
# #     # Register and log in a user
# #     user_data = {"username": "testuser", "email": "test@example.com", "password": "SecurePass123!"}
# #     client.post("/users/register", json=user_data)
# #     login_data = {"username": "testuser", "password": "SecurePass123!"}
# #     login_response = client.post("/users/login", data=login_data)
# #     token = login_response.json()["access_token"]
# #     # Retrieve user info
# #     headers = {"Authorization": f"Bearer {token}"}
# #     response = client.get("/users/me", headers=headers)
# #     assert response.status_code == 200
# #     assert "id" in response.json()
# #     assert "username" in response.json()
# #     assert "email" in response.json()


# # def test_get_current_user_info_with_expired_token(client):
# #     """Ensure expired tokens are rejected when retrieving user info."""
# #     # Create an expired token manually
# #     expired_token = client.post("/users/login", data={"username": "testuser", "password": "SecurePass123!"}).json()[
# #         "access_token"
# #     ]
# #     headers = {"Authorization": f"Bearer {expired_token}"}
# #     response = client.get("/users/me", headers=headers)
# #     assert response.status_code == 401
# #     assert response.json()["detail"] == "Token expired"


# # ========================
# # Test Update User Details
# # ========================


# # def test_update_user_details(client):
# #     """Ensure a user can update their details."""
# #     # Register and log in a user
# #     user_data = {"username": "testuser", "email": "test@example.com", "password": "SecurePass123!"}
# #     client.post("/users/register", json=user_data)
# #     login_data = {"username": "testuser", "password": "SecurePass123!"}
# #     login_response = client.post("/users/login", data=login_data)
# #     token = login_response.json()["access_token"]
# #     # Update user details
# #     update_data = {"username": "updateduser", "email": "updated@example.com"}
# #     headers = {"Authorization": f"Bearer {token}"}
# #     response = client.put("/users/me", json=update_data, headers=headers)
# #     assert response.status_code == 200
# #     assert response.json()["username"] == "updateduser"
# #     assert response.json()["email"] == "updated@example.com"


# # # ========================
# # # Test Change Password
# # # ========================


# # def test_change_password(client):
# #     """Ensure a user can change their password."""
# #     # Register and log in a user
# #     user_data = {"username": "testuser", "email": "test@example.com", "password": "SecurePass123!"}
# #     client.post("/users/register", json=user_data)
# #     login_data = {"username": "testuser", "password": "SecurePass123!"}
# #     login_response = client.post("/users/login", data=login_data)
# #     token = login_response.json()["access_token"]
# #     # Change password
# #     password_data = {"old_password": "SecurePass123!", "new_password": "NewSecurePass123!"}
# #     headers = {"Authorization": f"Bearer {token}"}
# #     response = client.put("/users/me/password", json=password_data, headers=headers)
# #     assert response.status_code == 200
# #     assert response.json()["message"] == "Password updated successfully"


# # def test_change_password_with_invalid_old_password(client):
# #     """Ensure password change fails with an incorrect old password."""
# #     # Register and log in a user
# #     user_data = {"username": "testuser", "email": "test@example.com", "password": "SecurePass123!"}
# #     client.post("/users/register", json=user_data)
# #     login_data = {"username": "testuser", "password": "SecurePass123!"}
# #     login_response = client.post("/users/login", data=login_data)
# #     token = login_response.json()["access_token"]
# #     # Attempt to change password with incorrect old password
# #     password_data = {"old_password": "WrongPass123!", "new_password": "NewSecurePass123!"}
# #     headers = {"Authorization": f"Bearer {token}"}
# #     response = client.put("/users/me/password", json=password_data, headers=headers)
# #     assert response.status_code == 401
# #     assert "detail" in response.json()
# #     assert response.json()["detail"] == "Old password is incorrect"


# # # ========================
# # # Test Get User Groups
# # # ========================


# # def test_get_user_groups(client):
# #     """Ensure a user's groups can be retrieved."""
# #     # Register a user
# #     user_data = {"username": "testuser", "email": "test@example.com", "password": "SecurePass123!"}
# #     client.post("/users/register", json=user_data)
# #     login_data = {"username": "testuser", "password": "SecurePass123!"}
# #     login_response = client.post("/users/login", data=login_data)
# #     token = login_response.json()["access_token"]
# #     # Retrieve user groups
# #     headers = {"Authorization": f"Bearer {token}"}
# #     response = client.get("/users/groups", headers=headers)
# #     assert response.status_code == 200
# #     assert isinstance(response.json(), list)
