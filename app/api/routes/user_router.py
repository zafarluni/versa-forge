# ruff: noqa: B008
from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.exceptions import DuplicateResourceError, PermissionDeniedError, ResourceNotFoundError
from app.core.security import encode_jwt
from app.db.database import get_db
from app.schemas.token_schema import TokenData
from app.schemas.user_schemas import PasswordUpdate, UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.utils.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/login", response_model=dict[str, str], summary="Authenticate and obtain a JWT token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    try:
        user = await UserService.authenticate_user(db, username=form_data.username, password=form_data.password)
    except (ResourceNotFoundError, PermissionDeniedError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Authentication failed") from exc

    token_data = TokenData(id=user.id, username=user.username, full_name=user.full_name, email=user.email)
    access_token = encode_jwt(
        token_data, expires_delta=timedelta(minutes=settings.security.access_token_expire_minutes)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register a new user"
)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)) -> UserResponse:
    try:
        return await UserService.register_user(db, user_data)
    except DuplicateResourceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def read_current_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    return current_user


@router.put("/me", response_model=UserResponse, summary="Update current user details")
async def update_current_user(
    update_data: UserUpdate, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    try:
        return await UserService.update_user_details(db, user_id=current_user.id, data=update_data)
    except DuplicateResourceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except ResourceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") from None


@router.put("/me/password", response_model=dict[str, str], summary="Change password")
async def change_password(
    password_data: PasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> dict[str, str]:
    try:
        await UserService.change_password(
            db,
            user_id=current_user.id,
            old_password=password_data.old_password,
            new_password=password_data.new_password,
        )
    except ResourceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") from None
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    return {"message": "Password updated successfully"}


@router.get("/groups", response_model=List[int], summary="List groups for current user")
async def read_user_groups(
    db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)
) -> List[int]:
    return await UserService.get_user_groups(db, current_user.id)
