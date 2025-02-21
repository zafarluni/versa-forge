from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from typing import List, Optional
from app.db.database import get_db
from app.db.schemas.agent_file_schema import AgentFileResponse
from app.services.agent_file_service import AgentFileService
from app.api.dependencies import get_current_user
from app.db.schemas.user_schemas import UserBase as User

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload", response_model=dict)
def upload_file(
    agent_id: int,
    file: UploadFile = File(...),
    db=Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = AgentFileService.save_file(db, agent_id, file, user.id)
    if not result:
        raise HTTPException(status_code=500, detail="File upload failed")
    return result


@router.get("/", response_model=List[AgentFileResponse])
def list_files(
    agent_id: int,
    db=Depends(get_db),
    user: User = Depends(get_current_user),
) -> List[AgentFileResponse]:
    files = AgentFileService.get_files(db, agent_id, user.id)
    if files is None:
        raise HTTPException(status_code=404, detail="No files found")
    return files
