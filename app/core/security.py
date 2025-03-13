# mypy: ignore-errors
from datetime import datetime, timezone, timedelta
from typing import Optional
import jwt
import bcrypt
from app.db.schemas.token_schema import TokenData
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Security, status
from passlib.context import CryptContext
from app.utils.config import settings

# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for JWT-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# Ensure bcrypt.__about__ exists to avoid compatibility issues with Passlib
if not hasattr(bcrypt, "__about__"):
    try:
        setattr(
            bcrypt, "__about__", type("about", (object,), {"__version__": getattr(bcrypt, "__version__", "unknown")})
        )
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
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ========================
# 🔹 Validate JWT Token
# ========================
def extract_token_data(token: str = Security(oauth2_scheme)) -> TokenData:
    """
    Validates and decodes a JWT token.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return TokenData.model_validate(payload)
    except jwt.ExpiredSignatureError:
        raise get_credentials_exception("Token expired, please login again.")
    except jwt.DecodeError:
        raise get_credentials_exception("Invalid token format.")
    except jwt.InvalidTokenError:
        raise get_credentials_exception("Invalid token signature.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
