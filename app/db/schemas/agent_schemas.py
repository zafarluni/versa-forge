# schemas/agent_schemas.py

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    prompt: str
    is_public: bool

class AgentCreate(AgentBase):
    categories: Optional[List[int]] = []

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    is_public: Optional[bool] = None
    categories: Optional[List[int]] = None

class AgentResponse(AgentBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True
