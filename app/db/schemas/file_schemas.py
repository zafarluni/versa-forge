from pydantic import BaseModel
from datetime import datetime


# Base Schema
class FileBase(BaseModel):
    filename: str
    content_type: str


# Upload File Schema
class FileUpload(FileBase):
    pass


# File Response Schema
class FileResponse(FileBase):
    id: int
    agent_id: int
    created_at: datetime

    class Config:
        from_attributes = True
