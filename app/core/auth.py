# ruff: noqa: B008
import jwt
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import extract_token_data, get_credentials_exception, oauth2_scheme
from app.db.database import get_db
from app.schemas.user_schemas import UserResponse
from app.services.user_service import UserService


async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> UserResponse:
    """
    Retrieves the current user based on the provided JWT token.

    Args:
        token (str): The JWT token obtained from the request.

    Returns:
        UserInDB: The user object if the token is valid.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    try:
        token_data = extract_token_data(token)
        if token_data.username is None:
            raise get_credentials_exception() from None
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise get_credentials_exception() from None
    except Exception as exep:
        raise get_credentials_exception("Could not validate credentials") from exep

    if not hasattr(token_data, "username") or not token_data.username:
        raise get_credentials_exception("Invalid token payload")

    user = await UserService.get_user_by_username(db, token_data.username)
    if not user:
        raise get_credentials_exception("User not found")

    return user
