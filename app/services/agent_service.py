from typing import Optional, List, Any
from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.database_models import Agent, AgentCategory, AgentFile
from app.db.schemas.agent_schemas import AgentCreate, AgentUpdate, AgentResponse

class AgentService:
    @staticmethod
    def create_agent(db: Session, agent_data: AgentCreate, owner_id: int) -> AgentResponse:
        new_agent = Agent(
            name=agent_data.name,
            description=agent_data.description,
            prompt=agent_data.prompt,
            is_public=agent_data.is_public,
            owner_id=owner_id,
            created_at=datetime.now(timezone.utc),
        )
        db.add(new_agent)
        db.commit()
        db.refresh(new_agent)
        return AgentResponse.model_validate(new_agent)

    @staticmethod
    def delete_agent_categories(db: Session, agent_id: int) -> None:
        stmt = delete(AgentCategory).where(AgentCategory.agent_id == agent_id)
        db.execute(stmt)
        db.commit()

    @staticmethod
    def assign_categories(db: Session, agent_id: int, category_ids: Optional[List[int]]) -> None:
        if not category_ids:
            return
        objs = [AgentCategory(agent_id=agent_id, category_id=cat_id) for cat_id in category_ids]
        db.bulk_save_objects(objs)
        db.commit()

    @staticmethod
    def get_public_agents(
        db: Session, category_id: Optional[int] = None, limit: int = 10, offset: int = 0
    ) -> List[AgentResponse]:
        stmt = select(Agent).where(Agent.is_public.is_(True))
        if category_id:
            stmt = stmt.join(AgentCategory).where(AgentCategory.category_id == category_id)
        stmt = stmt.offset(offset).limit(limit)
        result = db.execute(stmt).scalars().all()
        return [AgentResponse.model_validate(agent) for agent in result]

    @staticmethod
    def get_private_agents(db: Session, owner_id: int) -> List[AgentResponse]:
        stmt = select(Agent).where(Agent.owner_id == owner_id, Agent.is_public.is_(False))
        result = db.execute(stmt).scalars().all()
        return [AgentResponse.model_validate(agent) for agent in result]

    @staticmethod
    def update_agent(db: Session, agent_id: int, agent_data: AgentUpdate, owner_id: int) -> Optional[AgentResponse]:
        stmt = select(Agent).where(Agent.id == agent_id, Agent.owner_id == owner_id)
        agent = db.execute(stmt).scalar_one_or_none()
        if not agent:
            return None
        update_data = agent_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        db.commit()
        db.refresh(agent)
        return AgentResponse.model_validate(agent)

    @staticmethod
    def delete_agent(db: Session, agent_id: int, owner_id: int) -> bool:
        stmt = select(Agent).where(Agent.id == agent_id, Agent.owner_id == owner_id)
        agent = db.execute(stmt).scalar_one_or_none()
        if agent:
            db.delete(agent)
            db.commit()
            return True
        return False

    @staticmethod
    def upload_document(db: Session, agent_id: int, filename: str, content_type: str) -> Optional[AgentFile]:
        try:
            new_doc = AgentFile(agent_id=agent_id, filename=filename, content_type=content_type)
            db.add(new_doc)
            db.commit()
            db.refresh(new_doc)
            return new_doc
        except SQLAlchemyError:
            db.rollback()
            return None

    @staticmethod
    def get_agent_files(db: Session, agent_id: int) -> List[AgentFile]:
        stmt = select(AgentFile).where(AgentFile.agent_id == agent_id)
        result = db.execute(stmt).scalars().all()
        return result

    @staticmethod
    def get_agent_by_id_and_owner(db: Session, agent_id: int, owner_id: int) -> Optional[Agent]:
        stmt = select(Agent).where(Agent.id == agent_id, Agent.owner_id == owner_id)
        return db.execute(stmt).scalar_one_or_none()
