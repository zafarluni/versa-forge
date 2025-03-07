from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.database_models import Agent, AgentCategory
from app.db.schemas.agent_schemas import AgentCreate, AgentUpdate, AgentResponse
from app.core.exceptions import ResourceNotFoundException, PermissionDeniedException


class AgentService:
    """
    Service layer for managing Agents.
    
    - Ensures that only authorized users can modify or delete agents.
    - Returns structured Pydantic objects.
    """

    # ===========================
    # 1️⃣ Get All Agents for a User (Private + Public)
    # ===========================
    @staticmethod
    def get_agents_by_user(db: Session, user_id: int) -> List[AgentResponse]:
        """
        Retrieve all agents of a specific user (both private and public).
        """
        stmt = select(Agent).where(Agent.owner_id == user_id)
        agents = db.execute(stmt).scalars().all()

        return [AgentResponse.model_validate(agent) for agent in agents]

    # ===========================
    # 2️⃣ Get Only Public Agents for a User
    # ===========================
    @staticmethod
    def get_public_agents_by_user(db: Session, user_id: int) -> List[AgentResponse]:
        """
        Retrieve only public agents for a user.
        """
        stmt = select(Agent).where(Agent.owner_id == user_id, Agent.is_public.is_(True))
        agents = db.execute(stmt).scalars().all()

        return [AgentResponse.model_validate(agent) for agent in agents]

    # ===========================
    # 3️⃣ Get a Specific Agent (Public or Private)
    # ===========================
    @staticmethod
    def get_agent_by_id(db: Session, agent_id: int) -> AgentResponse:
        """
        Retrieve a specific agent by ID.
        - If the agent is public, any authenticated user can access.
        - If the agent is private, only the owner can access.
        """
        stmt = select(Agent).where(Agent.id == agent_id)
        agent = db.execute(stmt).scalar_one_or_none()

        if not agent:
            raise ResourceNotFoundException("Agent", agent_id)

        if not agent.is_public and agent.owner_id != user_id:
            raise PermissionDeniedException("You do not have access to this agent.")

        return AgentResponse.model_validate(agent)

    # ===========================
    # 4️⃣ Create a New Agent
    # ===========================
    @staticmethod
    def create_agent(db: Session, agent_data: AgentCreate, owner_id: int) -> AgentResponse:
        """
        Creates a new agent for the specified user.
        """
        new_agent = Agent(
            name=agent_data.name,
            description=agent_data.description,
            prompt=agent_data.prompt,
            is_public=agent_data.is_public,
            owner_id=owner_id
        )

        try:
            db.add(new_agent)
            db.commit()
            db.refresh(new_agent)
            return AgentResponse.model_validate(new_agent)
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Failed to create agent: {str(e)}")

    # ===========================
    # 5️⃣ Update an Existing Agent
    # ===========================
    @staticmethod
    def update_agent(db: Session, agent_id: int, agent_data: AgentUpdate, owner_id: int) -> Optional[AgentResponse]:
        """
        Updates an existing agent.
        - Ensures that only the owner can modify the agent.
        """
        stmt = select(Agent).where(Agent.id == agent_id, Agent.owner_id == owner_id)
        agent = db.execute(stmt).scalar_one_or_none()

        if not agent:
            raise ResourceNotFoundException("Agent", agent_id)

        # Apply updates
        update_data = agent_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)

        try:
            db.commit()
            db.refresh(agent)
            return AgentResponse.model_validate(agent)
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Failed to update agent: {str(e)}")

    # ===========================
    # 6️⃣ Delete an Agent
    # ===========================
    @staticmethod
    def delete_agent(db: Session, agent_id: int, owner_id: int) -> bool:
        """
        Deletes an agent.
        - Ensures only the owner can delete it.
        """
        stmt = select(Agent).where(Agent.id == agent_id, Agent.owner_id == owner_id)
        agent = db.execute(stmt).scalar_one_or_none()

        if not agent:
            return False  # No need to raise an error, just return False

        try:
            db.delete(agent)
            db.commit()
            return True
        except SQLAlchemyError:
            db.rollback()
            return False

    # ===========================
    # 7️⃣ Get All Public Agents (Authorized Users Only)
    # ===========================
    @staticmethod
    def get_all_public_agents(db: Session) -> List[AgentResponse]:
        """
        Retrieve all public agents, accessible only to authenticated users.
        """
        stmt = select(Agent).where(Agent.is_public.is_(True))
        agents = db.execute(stmt).scalars().all()

        return [AgentResponse.model_validate(agent) for agent in agents]

    # ===========================
    # 8️⃣ Get Agents by Category
    # ===========================
    @staticmethod
    def get_agents_by_category(db: Session, category_id: int) -> List[AgentResponse]:
        """
        Retrieve all public agents in a specific category.
        """
        stmt = select(Agent).join(AgentCategory).where(
            AgentCategory.category_id == category_id, Agent.is_public.is_(True)
        )
        agents = db.execute(stmt).scalars().all()

        return [AgentResponse.model_validate(agent) for agent in agents]
