# schemas/user_schemas.py

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: EmailStr


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# Properties to receive via API on update
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str


# Properties to return via API
class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
