from pydantic import BaseModel
from datetime import datetime


# Base Category Schema
class CategoryBase(BaseModel):
    name: str
    description: str


# Create Category
class CategoryCreate(CategoryBase):
    pass


# Response Schema
class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
