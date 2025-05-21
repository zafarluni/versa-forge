# ruff: noqa: B008
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.core.exceptions import (
    DuplicateResourceError,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from app.schemas.agent_schemas import AgentCreate, AgentResponse, AgentUpdate
from app.schemas.user_schemas import UserResponse
from app.services.agent_service import AgentService

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
)


@router.get(
    "/",
    response_model=List[AgentResponse],
    summary="List all agents for the current user",
)
async def get_user_agents(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> List[AgentResponse]:
    """
    Get all agents (public and private) for the authenticated user.
    """
    return await AgentService.get_agents_by_user(db, current_user.id)


@router.post(
    "/",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new agent",
)
async def create_agent(
    agent_data: AgentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> AgentResponse:
    """
    Create a new agent owned by the authenticated user.
    """
    try:
        return await AgentService.create_agent(db, agent_data=agent_data, owner_id=current_user.id)
    except DuplicateResourceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create agent",
        ) from exc


@router.get(
    "/public",
    response_model=List[AgentResponse],
    summary="List all public agents",
)
async def get_all_public_agents(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> List[AgentResponse]:
    """
    Get all public agents available in the system.
    """
    return await AgentService.get_all_public_agents(db)


@router.get(
    "/user/{user_id}/public",
    response_model=List[AgentResponse],
    summary="List public agents for a specific user",
)
async def get_public_user_agents(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> List[AgentResponse]:
    """
    Get public agents belonging to the specified user.
    """
    return await AgentService.get_public_agents_by_user(db, user_id)


@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Get an agent by ID",
)
async def get_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> AgentResponse:
    """
    Get details of a specific agent, checking access permissions.
    """
    try:
        return await AgentService.get_agent_by_id(db, agent_id=agent_id, user_id=current_user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e


@router.put(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Update an existing agent",
)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> AgentResponse:
    """
    Update fields of an existing agent (owner only).
    """
    try:
        return await AgentService.update_agent(db, agent_id=agent_id, agent_data=agent_data, user_id=current_user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update agent",
        ) from exc


@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an agent",
)
async def delete_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> None:
    """
    Delete an agent owned by the authenticated user.
    """
    try:
        deleted = await AgentService.delete_agent(db, agent_id=agent_id, user_id=current_user.id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete agent",
        ) from exc

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or unauthorized",
        )


@router.get(
    "/category/{category_id}",
    response_model=List[AgentResponse],
    summary="List public agents in a category",
)
async def get_agents_by_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> List[AgentResponse]:
    """
    Get all public agents that belong to the specified category.
    """
    return await AgentService.get_agents_by_category(db, category_id=category_id)
