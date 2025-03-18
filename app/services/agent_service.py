# agent_service.py
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.db.models.database_models import Agent, AgentCategory
from app.db.schemas.agent_schemas import AgentCreate, AgentUpdate, AgentResponse
from app.core.exceptions import ResourceNotFoundException, PermissionDeniedException, DatabaseException


class AgentService:
    @staticmethod
    async def get_agents_by_user(db: AsyncSession, user_id: int) -> List[AgentResponse]:
        """Retrieve all agents owned by a user (both public and private)"""
        query = select(Agent).where(Agent.owner_id == user_id)
        result = await db.execute(query)
        agents = result.scalars().all()
        return [AgentResponse.model_validate(agent) for agent in agents]

    @staticmethod
    async def get_public_agents_by_user(db: AsyncSession, user_id: int) -> List[AgentResponse]:
        """Retrieve public agents owned by a user"""
        query = select(Agent).where((Agent.owner_id == user_id) & (Agent.is_public.is_(True)))
        result = await db.execute(query)
        agents = result.scalars().all()
        return [AgentResponse.model_validate(agent) for agent in agents]

    @staticmethod
    async def get_all_public_agents(db: AsyncSession) -> List[AgentResponse]:
        """Retrieve all public agents system-wide"""
        query = select(Agent).where(Agent.is_public.is_(True))
        result = await db.execute(query)
        agents = result.scalars().all()
        return [AgentResponse.model_validate(agent) for agent in agents]

    @staticmethod
    async def get_agents_by_category(db: AsyncSession, category_id: int) -> List[AgentResponse]:
        """Retrieve agents by category ID with public check"""
        query = (
            select(Agent)
            .join(Agent.categories)
            .where((Agent.is_public.is_(True)) & (AgentCategory.category_id == category_id))
        )
        result = await db.execute(query)
        agents = result.scalars().all()
        return [AgentResponse.model_validate(agent) for agent in agents]

    @staticmethod
    async def get_agent_by_id(db: AsyncSession, agent_id: int, user_id: Optional[int] = None) -> AgentResponse:
        """Retrieve agent with access control checks"""
        query = select(Agent).where(Agent.id == agent_id)
        agent = await db.execute(query)
        agent_result = agent.scalar_one_or_none()

        if not agent_result:
            raise ResourceNotFoundException("Agent", agent_id)

        if not agent_result.is_public and agent_result.owner_id != user_id:
            raise PermissionDeniedException("Access denied to this agent")

        return AgentResponse.model_validate(agent_result)

    @staticmethod
    async def create_agent(db: AsyncSession, agent_data: AgentCreate, owner_id: int) -> AgentResponse:
        """Create new agent in the database"""
        new_agent = Agent(
            name=agent_data.name,
            description=agent_data.description,
            prompt=agent_data.prompt,
            is_public=agent_data.is_public,
            owner_id=owner_id,
        )

        try:
            db.add(new_agent)
            await db.flush()
            await db.refresh(new_agent)
            return AgentResponse.model_validate(new_agent)
        except SQLAlchemyError as e:
            await db.rollback()
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    async def update_agent(db: AsyncSession, agent_id: int, agent_data: AgentUpdate, user_id: int) -> AgentResponse:
        """Update existing agent with ownership check"""
        query = select(Agent).where((Agent.id == agent_id) & (Agent.owner_id == user_id))
        result = await db.execute(query)
        agent = result.scalar_one_or_none()

        if not agent:
            raise ResourceNotFoundException("Agent", agent_id)

        update_data = agent_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(agent, key, value)

        try:
            await db.flush()
            await db.refresh(agent)
            return AgentResponse.model_validate(agent)
        except SQLAlchemyError as e:
            await db.rollback()
            raise DatabaseException(f"Update failed: {str(e)}")

    @staticmethod
    async def delete_agent(db: AsyncSession, agent_id: int, user_id: int) -> bool:
        """Soft delete agent with ownership check"""
        query = delete(Agent).where((Agent.id == agent_id) & (Agent.owner_id == user_id))
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0
