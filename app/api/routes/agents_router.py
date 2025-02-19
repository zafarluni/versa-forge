from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session


from app.db.models.database_models import User
from app.db.schemas.agent_schemas import AgentCreate, AgentResponse
from app.db.database import get_db
from app.services.agent_service import AgentService
from app.core.auth import get_current_user

router = APIRouter(prefix="/agents", tags=["Agents"])


# Create a New Agent
@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if agent_data.is_public and not agent_data.categories:
        raise HTTPException(
            status_code=400, detail="Public agents must have categories"
        )

    new_agent = AgentService.create_agent(db, agent_data, user.id)

    if agent_data.is_public:
        AgentService.assign_categories(db, new_agent.id, agent_data.categories)

    return new_agent


# Get Public Agents
@router.get("/public", response_model=List[AgentResponse])
def get_public_agents(
    category_id: int = Query(None),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    agents = AgentService.get_public_agents(db, category_id, limit, offset)
    return agents


# Get Private Agents
@router.get("/private", response_model=List[AgentResponse])
def get_private_agents(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return AgentService.get_private_agents(db, user.id)


# Update Agent
@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: int,
    agent_data: AgentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    agent = AgentService.update_agent(db, agent_id, agent_data)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found or unauthorized")

    if agent.is_public:
        AgentService.delete_agent_categories(db, agent.id)
        AgentService.assign_categories(db, agent.id, agent_data.categories)

    return agent


# Delete Agent
@router.delete("/{agent_id}")
def delete_agent(
    agent_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    deleted = AgentService.delete_agent(db, agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found or unauthorized")
    return {"message": "Agent deleted successfully"}


# Upload RAG Files
@router.post("/{agent_id}/upload")
def upload_file(
    agent_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Validate file type
    if file.content_type not in {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Save file to disk
    file_path = f"./uploads/{agent_id}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Save file metadata to DB
    doc = AgentService.upload_document(db, agent_id, file.filename, file.content_type)
    return {"message": "File uploaded successfully", "file_id": doc.id}


# Get Agent Files
@router.get("/{agent_id}/files")
def get_agent_files(
    agent_id: int, db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    files = AgentService.get_agent_files(db, agent_id)
    return files
