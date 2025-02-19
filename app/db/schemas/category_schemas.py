# schemas/category_schemas.py

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

# Shared properties
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=5, max_length=100)
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Reject names that contain only spaces and enforce allowed characters."""
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("Category name cannot be empty or contain only spaces.")
        if not all(c.isalnum() or c.isspace() or c in "-'" for c in stripped_value):
            raise ValueError("Category name must contain only letters, numbers, spaces, hyphens, or apostrophes.")
        return stripped_value  # Trim spaces before saving


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
