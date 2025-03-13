from fastapi import Depends
from sqlalchemy.orm import Session

import jwt
from app.core.security import extract_token_data, get_credentials_exception, oauth2_scheme
from app.db.database import get_db
from app.db.schemas.user_schemas import UserResponse
from app.services.user_service import UserService


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> UserResponse:
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
        tokenData = extract_token_data(token)
        if tokenData.username is None:
            raise get_credentials_exception()
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise get_credentials_exception()
    except Exception as exep:
        raise get_credentials_exception("Could not validate credentials") from exep

    if not hasattr(tokenData, "username") or not tokenData.username:
        raise get_credentials_exception("Invalid token payload")

    user = UserService.get_user_by_username(db, tokenData.username)
    if not user:
        raise get_credentials_exception("User not found")

    return user
