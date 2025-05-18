from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.security import encode_jwt
from app.db.database import get_db
from app.db.schemas.token_schema import TokenData
from app.db.schemas.user_schemas import (
    PasswordUpdate,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import UserService
from app.utils.config import settings

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/login", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)) -> dict:
    """
    Authenticate a user and issue a JWT token.

    Args:
        form_data: OAuth2 form data (username=email, password).
        db: Async database session.

    Returns:
        Access token and token type.

    Raises:
        HTTP 401: If credentials are invalid.
    """
    user = await UserService.authenticate_user(db, form_data.username, form_data.password)
    token_data = TokenData(id=user.id, username=user.username, full_name=user.full_name, email=user.email)
    return {
        "access_token": encode_jwt(token_data, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)),
        "token_type": "bearer",
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)) -> UserResponse:
    """
    Register a new user.

    Args:
        user_data: User registration details.
        db: Async database session.

    Returns:
        The registered user's details.

    Raises:
        HTTP 400: If email/username is already taken.
    """
    return await UserService.register_user(db, user_data)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """
    Retrieve the authenticated user's details from the JWT token.

    Args:
        current_user: User details from the token.

    Returns:
        The user's details.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_details(
    update_data: UserUpdate, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Update the authenticated user's details (full name, email).

    Args:
        update_data: New user details.
        db: Async database session.
        current_user: Authenticated user details.

    Returns:
        Updated user details.

    Raises:
        HTTP 400: If the new email is already taken.
    """
    return await UserService.update_user_details(db, current_user.id, update_data)


@router.put("/me/password", response_model=dict)
async def change_password(
    password_data: PasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> dict:
    """
    Change the authenticated user's password.

    Args:
        password_data: Old and new password.
        db: Async database session.
        current_user: Authenticated user details.

    Returns:
        Success message.

    Raises:
        HTTP 401: If the old password is incorrect.
    """
    await UserService.change_password(
        db, current_user.id, old_password=password_data.old_password, new_password=password_data.new_password
    )
    return {"message": "Password updated successfully"}


@router.get("/groups", response_model=List[int])
async def get_user_groups(
    db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)
) -> List[int]:
    """
    Retrieve all group IDs the authenticated user belongs to.

    Args:
        db: Async database session.
        current_user: Authenticated user details.

    Returns:
        List of group IDs.
    """
    return await UserService.get_user_groups(db, current_user.id)
