# agents_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_user, get_db
from app.db.schemas.agent_schemas import AgentCreate, AgentUpdate, AgentResponse
from app.db.schemas.user_schemas import UserResponse
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("/", response_model=list[AgentResponse])
async def get_user_agents(
    db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)
) -> list[AgentResponse]:
    """Get all agents (public and private) for a specific user"""
    return await AgentService.get_agents_by_user(db, current_user.id)


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> AgentResponse:
    """Create new agent for a user (Authorization required)"""
    return await AgentService.create_agent(db, agent_data, current_user.id)


@router.get("/public", response_model=list[AgentResponse])
async def get_all_public_agents(
    db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)
) -> list[AgentResponse]:
    """Get all public agents available in the system"""
    return await AgentService.get_all_public_agents(db)


@router.get("/user/{user_id}/public", response_model=list[AgentResponse])
async def get_public_user_agents(
    user_id: int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)
) -> list[AgentResponse]:
    """Get public agents for a specific user"""
    return await AgentService.get_public_agents_by_user(db, user_id)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)
) -> AgentResponse:
    """Get agent details by ID with access control"""
    return await AgentService.get_agent_by_id(db, agent_id, current_user.id)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> AgentResponse:
    """Update existing agent (Owner only)"""
    return await AgentService.update_agent(db, agent_id, agent_data, current_user.id)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)
) -> None:
    """Delete agent (Owner only)"""
    success = await AgentService.delete_agent(db, agent_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found or unauthorized")


@router.get("/category/{category_id}", response_model=list[AgentResponse])
async def get_agents_by_category(
    category_id: int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)
) -> list[AgentResponse]:
    """Get all public agents in a specific category"""
    return await AgentService.get_agents_by_category(db, category_id)
