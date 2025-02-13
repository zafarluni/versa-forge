from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Agent, Document
from app.schemas import AgentCreate

def create_agent(db: Session, agent_data: AgentCreate, user_id: int):
    new_agent = Agent(**agent_data.dict(), owner_id=user_id, created_at=datetime.utcnow())
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    return new_agent

def get_user_agents(db: Session, user_id: int, limit: int, offset: int):
    return db.query(Agent).filter(Agent.owner_id == user_id).offset(offset).limit(limit).all()

def get_public_agents(db: Session, limit: int, offset: int):
    return db.query(Agent).filter(Agent.is_public == True).offset(offset).limit(limit).all()

def get_agent_by_id(db: Session, agent_id: int, user_id: int):
    return db.query(Agent).filter(Agent.id == agent_id, Agent.owner_id == user_id).first()

def upload_document(db: Session, agent_id: int, user_id: int, file):
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    max_size = 5 * 1024 * 1024  # 5MB

    if file.content_type not in allowed_types:
        return {"error": "Only PDF and DOCX files are allowed"}

    file_size = len(file.file.read())  # Read and calculate file size
    file.file.seek(0)  # Reset file pointer after reading

    if file_size > max_size:
        return {"error": "File size exceeds the 5MB limit"}

    agent = get_agent_by_id(db, agent_id, user_id)
    if not agent:
        return None

    new_doc = Document(agent_id=agent_id, filename=file.filename, content_type=file.content_type, created_at=datetime.utcnow())
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    return {"message": "File uploaded successfully", "document_id": new_doc.id}

def get_agent_documents(db: Session, agent_id: int, user_id: int):
    agent = get_agent_by_id(db, agent_id, user_id)
    if not agent:
        return None

    return db.query(Document).filter(Document.agent_id == agent_id).all()

def delete_agent(db: Session, agent_id: int, user_id: int):
    agent = get_agent_by_id(db, agent_id, user_id)
    if not agent:
        return None
    db.delete(agent)
    db.commit()
    return True

def delete_document(db: Session, agent_id: int, document_id: int, user_id: int):
    agent = get_agent_by_id(db, agent_id, user_id)
    if not agent:
        return None

    document = db.query(Document).filter(Document.id == document_id, Document.agent_id == agent_id).first()
    if not document:
        return None

    db.delete(document)
    db.commit()
    return True

def update_agent_prompt(db: Session, agent_id: int, user_id: int, new_prompt: str):
    agent = get_agent_by_id(db, agent_id, user_id)
    if not agent:
        return None

    agent.prompt = new_prompt
    db.commit()
    return True
