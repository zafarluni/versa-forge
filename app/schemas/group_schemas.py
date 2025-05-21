from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GroupBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None


class GroupCreate(GroupBase):
    """Schema for creating a new group."""

    pass


class GroupUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None


class GroupResponse(GroupBase):
    """Schema returned for group read operations."""

    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserGroupAssign(BaseModel):
    """Schema for assigning a user to a group."""

    user_id: int
    group_id: int
    model_config = ConfigDict(from_attributes=True)
