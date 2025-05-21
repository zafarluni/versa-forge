from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AgentFileBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    filename: str
    content_type: str


class AgentFileUpload(AgentFileBase):
    """Schema for uploading a new agent file."""

    pass


class AgentFileResponse(AgentFileBase):
    """Schema returned for agent file read operations."""

    id: int
    agent_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
