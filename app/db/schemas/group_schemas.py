from pydantic import BaseModel
from datetime import datetime


# Base Schema
class GroupBase(BaseModel):
    name: str
    description: str


# Create Group
class GroupCreate(GroupBase):
    pass


# Response Schema
class GroupResponse(GroupBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Assign User to Group
class UserGroupAssign(BaseModel):
    user_id: int
    group_id: int
