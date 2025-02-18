# schemas/category_schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Shared properties
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

# Properties to receive via API on creation
class CategoryCreate(CategoryBase):
    pass

# Properties to receive via API on update
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Properties to return via API
class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
