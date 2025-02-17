# app/auth/mock_auth.py
from fastapi import Depends
from app.db.models.database_models import User


def get_current_user():
    """Returns a mock user for testing."""
    return User(
        id=1,
        username="admin",
        email="admin@example.com",
        password_hash="pass",
    )
