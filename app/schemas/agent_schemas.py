from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AgentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    prompt: str
    is_public: bool = False


class AgentCreate(AgentBase):
    """Schema for creating a new agent."""

    categories: List[int] = Field(default_factory=list)


class AgentUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    prompt: Optional[str] = None
    is_public: Optional[bool] = None
    categories: Optional[List[int]] = None


class AgentResponse(AgentBase):
    """Schema returned for agent read operations."""

    id: int
    owner_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
