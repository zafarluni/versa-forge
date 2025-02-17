from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# Base Schema
class AgentBase(BaseModel):
    name: str
    description: str
    prompt: str
    is_public: bool


# Create Agent Schema (Request)
class AgentCreate(AgentBase):
    categories: Optional[List[int]] = []


# Update Agent Schema
class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    categories: Optional[List[int]] = None


# Response Schema
class AgentResponse(AgentBase):
    id: int
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True
