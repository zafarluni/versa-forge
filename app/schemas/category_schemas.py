from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoryBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=5, max_length=100)
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Reject blank names and enforce allowed characters."""
        v = value.strip()
        if not v:
            raise ValueError("Category name cannot be empty or whitespace.")
        if any(not (c.isalnum() or c.isspace() or c in "-'") for c in v):
            raise ValueError("Category name must contain only letters, numbers, spaces, hyphens, or apostrophes.")
        return v


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""

    pass


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: Optional[str]) -> Optional[str]:
        return value.strip() if value is not None else None


class CategoryResponse(CategoryBase):
    """Schema returned for category read operations."""

    id: int
    model_config = ConfigDict(from_attributes=True)
