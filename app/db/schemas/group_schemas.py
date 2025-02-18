# schemas/group_schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Shared properties
class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None

# Properties to receive via API on creation
class GroupCreate(GroupBase):
    pass

# Properties to receive via API on update
class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Properties to return via API
class GroupResponse(GroupBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Schema for assigning a user to a group
class UserGroupAssign(BaseModel):
    user_id: int
    group_id: int
