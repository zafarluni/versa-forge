from pathlib import Path
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.schemas.agent_file_schema import AgentFileResponse
from app.db.models.database_models import AgentFile, Agent
from app.services.agent_service import AgentService

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class AgentFileService:
    @staticmethod
    def save_file(db: Session, agent_id: int, file, user_id: int) -> dict:
        # Verify ownership using AgentService
        agent = AgentService.get_agent_by_id_and_owner(db, agent_id, owner_id=user_id)
        if not agent:
            raise HTTPException(status_code=403, detail="Not authorized to upload files for this agent.")
        allowed_types = {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type")
        safe_filename = f"{agent_id}_{file.filename.replace('/', '_')}"
        file_path = UPLOAD_DIR / safe_filename
        try:
            with file_path.open("wb") as f:
                f.write(file.file.read())
        except OSError as e:
            raise HTTPException(status_code=500, detail="File upload failed") from e
        doc = AgentService.upload_document(db, agent_id, file.filename, file.content_type)
        if not doc:
            raise HTTPException(status_code=500, detail="Failed to save file metadata")
        return {"message": "File uploaded successfully", "file_id": doc.id}

    @staticmethod
    def get_files(db: Session, agent_id: int, user_id: int):
        agent = AgentService.get_agent_by_id_and_owner(db, agent_id, owner_id=user_id)
        if not agent:
            return None
        stmt = AgentService.get_agent_files(db, agent_id)
        return [AgentFileResponse.model_validate(file) for file in stmt]
