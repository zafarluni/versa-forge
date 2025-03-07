from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """
    Represents a JWT access token.

    Attributes:
        access_token (str): The JWT access token string.
        token_type (str): The type of token, typically "bearer".
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Represents the data stored within a JWT token.

    Attributes:
        username (str): The username associated with the token.
        full_name (Optional[str]): The full name of the user (if available).
        email (Optional[str]): The email address of the user (if available).
        disabled (Optional[bool]): Whether the user account is disabled.
    """

    id: int
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_active: bool
