from pathlib import Path
from typing import List

import aiofiles
from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PermissionDeniedError, UnsupportedFileTypeError
from app.db.models.database_models import AgentFile
from app.schemas.agent_files_schema import AgentFileResponse
from app.services.agent_service import AgentService

# Ensure upload directory exists once at startup
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class AgentFileService:
    @staticmethod
    async def save_file(
        db_session: AsyncSession,
        agent_id: int,
        file: UploadFile,
        user_id: int,
    ) -> AgentFileResponse:
        """
        Verify ownership, validate file type, write asynchronously to disk,
        and persist metadata in its own transaction. If metadata fails, remove file.
        """
        # 1. Verify agent ownership
        agent = await AgentService.get_agent_by_id(db_session, agent_id=agent_id, user_id=user_id)
        if agent.owner_id != user_id:
            raise PermissionDeniedError("Not authorized to upload to this agent.")

        # 2. Validate MIME type
        allowed_types = {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        if file.content_type not in allowed_types:
            raise UnsupportedFileTypeError(file.content_type)

        # 3. Save file asynchronously
        safe_name = f"{agent_id}_{file.filename.replace('/', '_')}"
        destination = UPLOAD_DIR / safe_name

        content = await file.read()
        try:
            async with aiofiles.open(destination, "wb") as out_file:
                await out_file.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to write file") from e

        # 4. Persist metadata in its own transaction
        try:
            async with db_session.begin():
                new_file = AgentFile(
                    agent_id=agent_id,
                    filename=file.filename,
                    content_type=file.content_type,
                )
                db_session.add(new_file)
            return AgentFileResponse.model_validate(new_file)
        except Exception as e:
            # Clean up the file if metadata insertion failed
            if destination.exists():
                destination.unlink(missing_ok=True)
            raise

    @staticmethod
    async def get_files(
        db_session: AsyncSession,
        agent_id: int,
        user_id: int,
    ) -> List[AgentFileResponse]:
        """
        Verify ownership, then return all file metadata for the agent.
        """
        # 1. Verify agent ownership
        agent = await AgentService.get_agent_by_id(db_session, agent_id=agent_id, user_id=user_id)
        if agent.owner_id != user_id:
            raise PermissionDeniedError("Not authorized to list files for this agent.")

        # 2. Query metadata (read-only)
        result = await db_session.scalars(select(AgentFile).where(AgentFile.agent_id == agent_id))
        return [AgentFileResponse.model_validate(f) for f in result.all()]
