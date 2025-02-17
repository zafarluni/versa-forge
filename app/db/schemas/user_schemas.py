from pydantic import BaseModel, EmailStr
from datetime import datetime


# Base Schema
class UserBase(BaseModel):
    username: str
    email: EmailStr


# Schema for Creating a User
class UserCreate(UserBase):
    password: str


# Schema for Response
class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
