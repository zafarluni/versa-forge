from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schemas.agent_schemas import AgentCreate, AgentUpdate, AgentResponse
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["Agents"])

# ============================================================================  
# 1️⃣ Get All Agents for a User (Private + Public)
# ============================================================================
@router.get("/user/{user_id}", response_model=List[AgentResponse])
def get_agents_by_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve **all** agents of a user (both private and public).
    """
    return AgentService.get_agents_by_user(db, user_id)


# ===================================================================================
# 2️⃣ Get Only Public Agents for a User
# ===================================================================================
@router.get("/user/{user_id}/public", response_model=List[AgentResponse])
def get_public_agents_by_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve **only public** agents for a user.
    """
    return AgentService.get_public_agents_by_user(db, user_id)


# ==========================================================
# 3️⃣ Get a Specific Agent
# ==========================================================
@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific agent by ID.
    """
    return AgentService.get_agent_by_id(db, agent_id, None)


# ===========================================
# 4️⃣ Create a New Agent for a User
# ===========================================
@router.post("/user/{user_id}", response_model=AgentResponse, status_code=201)
def create_agent(
    user_id: int,
    agent_data: AgentCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new agent for a specific user.
    """
    return AgentService.create_agent(db, agent_data, user_id)


# =======================================================
# 5️⃣ Update an Agent for a User
# =======================================================
@router.put("/user/{user_id}/{agent_id}", response_model=AgentResponse)
def update_agent(
    user_id: int,
    agent_id: int,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing agent for a specific user.
    """
    updated_agent = AgentService.update_agent(db, agent_id, agent_data, user_id)
    if not updated_agent:
        raise HTTPException(status_code=404, detail="Agent not found or unauthorized")
    return updated_agent


# =============================================================
# 6️⃣ Delete an Agent for a User
# =============================================================
@router.delete("/user/{user_id}/{agent_id}", response_model=dict)
def delete_agent(
    user_id: int,
    agent_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete an agent for a specific user.
    """
    deleted = AgentService.delete_agent(db, agent_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found or unauthorized")
    return {"message": "Agent deleted successfully", "agent_id": agent_id}


# =========================================================================
# 7️⃣ Get All Public Agents
# =========================================================================
@router.get("/public", response_model=List[AgentResponse])
def get_all_public_agents(
    db: Session = Depends(get_db),
):
    """
    Retrieve **all public agents**.
    """
    return AgentService.get_all_public_agents(db)


# ============================================================================
# 8️⃣ Get Agents by Category
# ============================================================================
@router.get("/category/{category_id}", response_model=List[AgentResponse])
def get_agents_by_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve **all public agents** in a specific category.
    """
    return AgentService.get_agents_by_category(db, category_id)
