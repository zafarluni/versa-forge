from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    full_name: Optional[str] = Field(None, max_length=100)
    email: EmailStr

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must contain only letters, numbers, underscores, and hyphens")
        return v


class UserCreate(UserBase):
    """Schema for registering a new user."""

    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None


class PasswordUpdate(BaseModel):
    """Schema for changing a user's password."""

    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v

    @model_validator(mode="after")
    def passwords_different(self) -> "PasswordUpdate":
        if self.old_password == self.new_password:
            raise ValueError("New password must be different from the old password")
        return self


class UserResponse(UserBase):
    """Schema returned for user read operations."""

    id: int
    is_active: bool
    is_admin: bool
