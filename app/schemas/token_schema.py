from typing import Optional

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    """Represents a JWT access token."""

    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Payload data stored in a JWT."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
