# schemas/agent_schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Shared properties
class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    prompt: str
    is_public: bool

# Properties to receive via API on creation
class AgentCreate(AgentBase):
    categories: Optional[List[int]] = []

# Properties to receive via API on update
class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    is_public: Optional[bool] = None
    categories: Optional[List[int]] = None

# Properties to return via API
class AgentResponse(AgentBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True
