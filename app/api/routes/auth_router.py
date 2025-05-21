# ruff: noqa: B008
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PermissionDeniedError, ResourceNotFoundError
from app.core.security import encode_jwt
from app.db.database import get_db
from app.schemas.token_schema import Token, TokenData
from app.services.user_service import UserService
from app.utils.config import get_settings

settings = get_settings()

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/token",
    response_model=Token,
    summary="Obtain JWT access token",
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Handles user login and generates a JWT token upon successful authentication.

    Args:
        form_data: OAuth2 form data (username, password).
        db: Async database session.

    Returns:
        The access token and its type.
    """
    try:
        user = await UserService.authenticate_user(db, username=form_data.username, password=form_data.password)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    # Prepare token payload
    token_payload = TokenData(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
    )
    expires = timedelta(minutes=settings.security.access_token_expire_minutes)
    access_token = encode_jwt(token_payload, expires_delta=expires)

    return Token(access_token=access_token, token_type="bearer")
