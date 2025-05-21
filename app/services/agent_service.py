from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    DatabaseError,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from app.db.models.database_models import Agent, AgentCategory
from app.schemas.agent_schemas import AgentCreate, AgentResponse, AgentUpdate


class AgentService:
    @staticmethod
    async def get_agents_by_user(db: AsyncSession, user_id: int) -> List[AgentResponse]:
        result = await db.scalars(select(Agent).where(Agent.owner_id == user_id))
        return [AgentResponse.model_validate(a) for a in result.all()]

    @staticmethod
    async def get_public_agents_by_user(db: AsyncSession, user_id: int) -> List[AgentResponse]:
        stmt = select(Agent).where((Agent.owner_id == user_id) & (Agent.is_public.is_(True)))
        result = await db.scalars(stmt)
        return [AgentResponse.model_validate(a) for a in result.all()]

    @staticmethod
    async def get_all_public_agents(db: AsyncSession) -> List[AgentResponse]:
        result = await db.scalars(select(Agent).where(Agent.is_public.is_(True)))
        return [AgentResponse.model_validate(a) for a in result.all()]

    @staticmethod
    async def get_agents_by_category(db: AsyncSession, category_id: int) -> List[AgentResponse]:
        stmt = (
            select(Agent)
            .join(Agent.categories)
            .where((Agent.is_public.is_(True)) & (AgentCategory.category_id == category_id))
        )
        result = await db.scalars(stmt)
        return [AgentResponse.model_validate(a) for a in result.all()]

    @staticmethod
    async def get_agent_by_id(db: AsyncSession, agent_id: int, user_id: Optional[int] = None) -> AgentResponse:
        agent = await db.get(Agent, agent_id)
        if not agent:
            raise ResourceNotFoundError("Agent", agent_id)
        if not agent.is_public and agent.owner_id != user_id:
            raise PermissionDeniedError("Access denied to this agent")
        return AgentResponse.model_validate(agent)

    @staticmethod
    async def create_agent(db: AsyncSession, agent_data: AgentCreate, owner_id: int) -> AgentResponse:
        new_agent = Agent(
            name=agent_data.name,
            description=agent_data.description,
            prompt=agent_data.prompt,
            is_public=agent_data.is_public,
            owner_id=owner_id,
        )
        try:
            async with db.begin():
                db.add(new_agent)
            return AgentResponse.model_validate(new_agent)
        except Exception as e:
            raise DatabaseError(f"Failed to create agent: {e}") from e

    @staticmethod
    async def update_agent(
        db: AsyncSession,
        agent_id: int,
        agent_data: AgentUpdate,
        user_id: int,
    ) -> AgentResponse:
        # Load with categories
        agent = await db.get(Agent, agent_id, options=[selectinload(Agent.categories)])
        if not agent:
            raise ResourceNotFoundError("Agent", agent_id)
        if agent.owner_id != user_id:
            raise PermissionDeniedError("No permission to update this agent")

        update_data = agent_data.model_dump(exclude_unset=True)

        # Handle categories
        if "categories" in update_data:
            agent.categories.clear()
            for cid in update_data.pop("categories") or []:
                agent.categories.append(AgentCategory(agent_id=agent.id, category_id=cid))

        # Apply other fields
        for field, value in update_data.items():
            setattr(agent, field, value)

        try:
            async with db.begin():
                db.add(agent)
            return AgentResponse.model_validate(agent)
        except Exception as e:
            raise DatabaseError(f"Failed to update agent: {e}") from e

    @staticmethod
    async def delete_agent(db: AsyncSession, agent_id: int, user_id: int) -> bool:
        agent = await db.get(Agent, agent_id)
        if not agent or agent.owner_id != user_id:
            return False
        try:
            async with db.begin():
                await db.delete(agent)
            return True
        except Exception as e:
            raise DatabaseError(f"Failed to delete agent: {e}") from e
