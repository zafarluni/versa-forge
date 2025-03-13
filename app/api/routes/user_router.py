from datetime import timedelta
from typing import Dict, List

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.db.database import get_db
from app.db.schemas.token_schema import TokenData
from app.db.schemas.user_schemas import (
    PasswordUpdate,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import UserService
from app.core.security import encode_jwt, extract_token_data, get_credentials_exception
from app.utils.config import settings

# ===========================
# Router Initialization
# ===========================
router = APIRouter(prefix="/users", tags=["Users"])

# ===========================
# Authentication Endpoints
# ===========================


@router.post("/login", response_model=Dict[str, str])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Authenticate a user and issue a JWT token.

    Args:
        form_data (OAuth2PasswordRequestForm): Login credentials (username=email, password).
        db (Session): Database session.

    Returns:
        Dict[str, str]: Access token and token type.
    """
    user = UserService.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise get_credentials_exception("Incorrect username or password")

    # Generate JWT token data
    token_data = TokenData(id=user.id, username=user.username, full_name=user.full_name, email=user.email)

    return {
        "access_token": encode_jwt(token_data, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)),
        "token_type": "bearer",
    }


# ===========================
# User Management Endpoints
# ===========================


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """
    Register a new user.

    Args:
        user_data (UserCreate): User registration details.
        db (Session): Database session.

    Returns:
        UserResponse: The registered user's details.

    Raises:
        DuplicateResourceException: If the email or username already exists.
    """
    return UserService.register_user(db, user_data)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    token_data: TokenData = Depends(extract_token_data), db: Session = Depends(get_db)
) -> UserResponse:
    """
    Retrieve the currently authenticated user from the JWT token.

    Args:
        token_data (TokenData): Decoded JWT token data.
        db (Session): Database session.

    Returns:
        UserResponse: The authenticated user's details.

    Raises:
        HTTPException: If the token is expired or invalid.
    """
    try:
        user = UserService.get_user_by_username(db, token_data.username)
        if not user:
            raise get_credentials_exception("User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@router.put("/me", response_model=UserResponse)
def update_user_details(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """
    Update the logged-in user's details (excluding password).

    Args:
        user_data (UserUpdate): Updated user details.
        db (Session): Database session.
        current_user (UserResponse): The currently authenticated user.

    Returns:
        UserResponse: The updated user's details.
    """
    updated_user = UserService.update_user_details(db, current_user.id, user_data)
    return updated_user


@router.put("/me/password", response_model=Dict[str, str])
def change_password(
    password_data: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Change the logged-in user's password.

    Args:
        password_data (PasswordUpdate): The old and new passwords.
        db (Session): Database session.
        current_user (UserResponse): The currently authenticated user.

    Returns:
        Dict[str, str]: A success message indicating the password was updated.

    Raises:
        HTTPException: If the old password is incorrect.
    """
    UserService.change_password(
        db,
        current_user.id,
        old_password=password_data.old_password,
        new_password=password_data.new_password,
    )
    return {"message": "Password updated successfully"}


# ===========================
# Group Management Endpoints
# ===========================


@router.get("/groups", response_model=List[int])
def get_user_groups(user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)) -> List[int]:
    """
    Retrieve all groups the logged-in user belongs to.

    Args:
        user (UserResponse): The currently authenticated user.
        db (Session): Database session.

    Returns:
        List[int]: List of group IDs the user is assigned to.
    """
    return UserService.get_user_groups(db, user.id)
