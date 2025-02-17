from sqlalchemy.orm import Session
from app.db.models.database_models import Agent, AgentFile, AgentCategory
from datetime import datetime, timezone


class AgentService:

    @staticmethod
    def create_agent(db: Session, agent_data, user_id: int):
        new_agent = Agent(
            name=agent_data.name,
            description=agent_data.description,
            prompt=agent_data.prompt,
            is_public=agent_data.is_public,
            owner_id=user_id,
            created_at=datetime.now(
                timezone.utc
            ),  # Updated for timezone-aware datetime
        )
        db.add(new_agent)
        db.commit()
        db.refresh(new_agent)
        return new_agent

    @staticmethod
    def delete_agent_categories(db: Session, agent_id: int):
        db.query(AgentCategory).filter(AgentCategory.agent_id == agent_id).delete()
        db.commit()

    @staticmethod
    def assign_categories(db: Session, agent_id: int, category_ids: list[int]):
        for category_id in category_ids:
            new_category = AgentCategory(agent_id=agent_id, category_id=category_id)
            db.add(new_category)
        db.commit()

    @staticmethod
    def get_public_agents(db: Session, category_id=None, limit=10, offset=0):
        query = db.query(Agent).filter(Agent.is_public.is_(True))
        if category_id:
            query = query.join(AgentCategory).filter(
                AgentCategory.category_id == category_id
            )
        return query.offset(offset).limit(limit).all()

    @staticmethod
    def get_private_agents(db: Session, user_id: int):
        return (
            db.query(Agent)
            .filter(Agent.owner_id == user_id, Agent.is_public.is_(False))
            .all()
        )

    @staticmethod
    def update_agent(db: Session, agent_id: int, agent_data):
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return None
        agent.name = agent_data.name
        agent.description = agent_data.description
        agent.prompt = agent_data.prompt
        db.commit()
        db.refresh(agent)
        return agent

    @staticmethod
    def delete_agent(db: Session, agent_id: int):
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if agent:
            db.delete(agent)
            db.commit()
            return True
        return False

    @staticmethod
    def upload_document(db: Session, agent_id: int, filename: str, content_type: str):
        new_doc = AgentFile(
            agent_id=agent_id, filename=filename, content_type=content_type
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        return new_doc

    @staticmethod
    def get_agent_files(db: Session, agent_id: int):
        return db.query(AgentFile).filter(AgentFile.agent_id == agent_id).all()
