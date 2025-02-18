# schemas/agent_file_schemas.py

from pydantic import BaseModel
from datetime import datetime

# Shared properties
class AgentFileBase(BaseModel):
    filename: str
    content_type: str

# Properties to receive via API on file upload
class AgentFileUpload(AgentFileBase):
    pass

# Properties to return via API
class AgentFileResponse(AgentFileBase):
    id: int
    agent_id: int
    created_at: datetime

    class Config:
        from_attributes = True
