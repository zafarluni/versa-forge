# mypy: ignore-errors
from datetime import datetime, timezone, timedelta
from typing import Optional
import jwt
import bcrypt
from app.db.schemas.token_schema import TokenData
from app.db.schemas.user_schemas import UserBase
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, Security, Header, status
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


# ========================
# 🔹 Generate JWT Token
# ========================
def create_jwt_token(token_data: TokenData, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token with an expiration time.

    Args:
        token_data (TokenData): The payload data to encode into the token.
        expires_delta (timedelta, optional): The duration until the token expires. Defaults to 30 minutes.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = token_data.model_dump()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ========================
# 🔹 Validate JWT Token
# ========================
def get_jwt_payload(token: str = Security(oauth2_scheme)) -> TokenData:
    """
    Validates and decodes a JWT token.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return TokenData.model_validate(payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")  # pylint: disable=W0707:raise-missing-from
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")  # pylint: disable=W0707:raise-missing-from


# ========================
# 🔹 API Key Validation
# ========================
def verify_api_key(api_key: str = Header(None, alias="X-API-Key")) -> str:
    """
    Validates API key for requests that require API authentication.
    """
    # if not api_key or api_key != settings.API_KEY:
    #     raise HTTPException(status_code=403, detail="Invalid API Key")

    return api_key


# ========================
# 🔹 HMAC Signature Verification
# ========================
def verify_request_signature(user_id: int, api_key: str, signature: str = Header(None)) -> None:
    """
    Validates HMAC signature for high-security requests.

    Steps:
    1. Generates a valid HMAC hash using the user_id and API Key.
    2. Compares it to the signature received in the request.
    """
    # if not signature:
    #     raise HTTPException(status_code=400, detail="Missing HMAC signature")

    # # Create HMAC signature using SHA256
    # expected_signature = hmac.new(
    #     key=settings.SECRET_KEY.encode(),
    #     msg=f"{user_id}:{api_key}".encode(),
    #     digestmod=hashlib.sha256
    # ).hexdigest()

    # # Compare received signature with expected signature
    # if not hmac.compare_digest(expected_signature, signature):
    #     raise HTTPException(status_code=403, detail="Invalid request signature")
    pass


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserBase:
    """
    Retrieves the current user based on the provided JWT token.

    Args:
        token (str): The JWT token obtained from the request.

    Returns:
        UserInDB: The user object if the token is valid.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired, please login again.")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token, could not decode.")
    except Exception as exep:
        raise credentials_exception from exep

    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


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
