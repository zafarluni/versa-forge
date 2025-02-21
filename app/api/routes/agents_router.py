from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query

from app.db.database import get_db
from app.db.schemas.agent_schemas import AgentCreate, AgentUpdate, AgentResponse
from app.db.schemas.agent_file_schema import AgentFileResponse
from app.services.agent_service import AgentService
from app.core.auth import get_current_user
from app.db.schemas.user_schemas import UserBase as User

router = APIRouter(prefix="/agents", tags=["Agents"])

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/", response_model=AgentResponse)
def create_agent(
    agent_data: AgentCreate,
    db=Depends(get_db),
    user: User = Depends(get_current_user),
) -> AgentResponse:
    if agent_data.is_public and not agent_data.categories:
        raise HTTPException(status_code=400, detail="Public agents must have categories")
    new_agent = AgentService.create_agent(db, agent_data, owner_id=user.id)
    if agent_data.is_public and agent_data.categories:
        AgentService.assign_categories(db, new_agent.id, agent_data.categories)
    return new_agent


@router.get("/public", response_model=List[AgentResponse])
def get_public_agents(
    category_id: Optional[int] = Query(None),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
) -> List[AgentResponse]:
    return AgentService.get_public_agents(db, category_id, limit, offset)


@router.get("/private", response_model=List[AgentResponse])
def get_private_agents(
    db=Depends(get_db), user: User = Depends(get_current_user)
) -> List[AgentResponse]:
    return AgentService.get_private_agents(db, owner_id=user.id)


@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    db=Depends(get_db),
    user: User = Depends(get_current_user),
) -> AgentResponse:
    agent = AgentService.update_agent(db, agent_id, agent_data, owner_id=user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found or unauthorized")
    if agent.is_public and agent_data.categories:
        AgentService.delete_agent_categories(db, agent.id)
        AgentService.assign_categories(db, agent.id, agent_data.categories)
    return agent


@router.delete("/{agent_id}")
def delete_agent(
    agent_id: int, db=Depends(get_db), user: User = Depends(get_current_user)
) -> dict:
    deleted = AgentService.delete_agent(db, agent_id, owner_id=user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found or unauthorized")
    return {"message": "Agent deleted successfully"}


@router.post("/{agent_id}/upload", response_model=dict)
def upload_file(
    agent_id: int,
    file: UploadFile = File(...),
    db=Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    # Check ownership before uploading
    agent = AgentService.get_agent_by_id_and_owner(db, agent_id, owner_id=user.id)
    if not agent:
        raise HTTPException(status_code=403, detail="Not allowed to upload files to this agent.")
    allowed_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    safe_filename = f"{agent_id}_{file.filename.replace('/', '_')}"
    file_path = UPLOAD_DIR / safe_filename
    try:
        with file_path.open("wb") as f:
            f.write(file.file.read())
    except OSError as e:
        raise HTTPException(status_code=500, detail="File upload failed") from e
    doc = AgentService.upload_document(db, agent_id, file.filename, file.content_type)
    if not doc:
        raise HTTPException(status_code=500, detail="Failed to save file metadata")
    return {"message": "File uploaded successfully", "file_id": doc.id}


@router.get("/{agent_id}/files", response_model=List[AgentFileResponse])
def get_agent_files(
    agent_id: int, db=Depends(get_db), user: User = Depends(get_current_user)
) -> List[AgentFileResponse]:
    agent = AgentService.get_agent_by_id_and_owner(db, agent_id, owner_id=user.id)
    if not agent:
        raise HTTPException(status_code=403, detail="Not allowed to access these files.")
    files = AgentService.get_agent_files(db, agent_id)
    # Assuming AgentFileResponse.model_validate is available
    return [AgentFileResponse.model_validate(file) for file in files]
