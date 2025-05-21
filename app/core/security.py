# mypy: ignore-errors
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.schemas.token_schema import TokenData
from app.utils.config import get_settings

settings = get_settings()

# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for JWT-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# Ensure bcrypt.__about__ exists to avoid compatibility issues with Passlib
if not hasattr(bcrypt, "__about__"):
    try:
        bcrypt.__about__ = type("about", (object,), {"__version__": getattr(bcrypt, "__version__", "unknown")})  # type: ignore
    except AttributeError:
        pass  # In case bcrypt.__version__ does not exist, we skip setting __about__


def get_credentials_exception(detail_message="Token expired, please login again.") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail_message,
        headers={"WWW-Authenticate": "Bearer"},
    )


# ========================
# 🔹 Generate JWT Token
# ========================
def encode_jwt(token_data: TokenData, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token with an expiration time.

    Args:
        token_data (TokenData): The payload data to encode into the token.
        expires_delta (timedelta, optional): The duration until the token expires. Defaults to 30 minutes.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = token_data.model_dump()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.security.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.security.secret_key, algorithm=settings.security.algorithm)


# ========================
# 🔹 Validate JWT Token
# ========================
def extract_token_data(token: str = Security(oauth2_scheme)) -> TokenData:
    """
    Validates and decodes a JWT token.
    """
    try:
        payload = jwt.decode(token, settings.security.secret_key, algorithms=[settings.security.algorithm])
        return TokenData.model_validate(payload)
    except jwt.ExpiredSignatureError:
        raise get_credentials_exception("Token expired, please login again.") from None
    except jwt.DecodeError:
        raise get_credentials_exception("Invalid token format.") from None
    except jwt.InvalidTokenError:
        raise get_credentials_exception("Invalid token signature.") from None
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


# ========================
# 🔹 Password Hashing & Verification
# ========================
def get_password_hash(password: str) -> str:
    """
    Generates a hashed password using the configured password hashing context.

    Args:
        password (str): The plain-text password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed password using the configured password hashing context.

    Args:
        plain_password (str): The plain-text password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the plain-text password matches the hashed password, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
