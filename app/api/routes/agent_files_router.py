# ruff: noqa: B008
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.core.exceptions import PermissionDeniedError, UnsupportedFileTypeError
from app.schemas.agent_files_schema import AgentFileResponse
from app.schemas.user_schemas import UserResponse
from app.services.agent_file_service import AgentFileService

router = APIRouter(
    prefix="/files",
    tags=["Files"],
)


@router.post(
    "/upload",
    response_model=AgentFileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file for an agent",
)
async def upload_file(
    agent_id: int = Query(..., description="ID of the agent to attach the file to"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> AgentFileResponse:
    """
    Upload a document (PDF or DOCX) for RAG ingestion.
    Ensures the user owns the agent before saving.
    """
    try:
        return await AgentFileService.save_file(
            db_session=db,
            agent_id=agent_id,
            file=file,
            user_id=current_user.id,
        )
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
    except UnsupportedFileTypeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed",
        ) from e


@router.get(
    "/",
    response_model=List[AgentFileResponse],
    summary="List all files for an agent",
)
async def list_files(
    agent_id: int = Query(..., description="ID of the agent"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> List[AgentFileResponse]:
    """
    Retrieve metadata for all files attached to the specified agent.
    Ensures the user owns the agent before listing.
    """
    try:
        files = await AgentFileService.get_files(
            db_session=db,
            agent_id=agent_id,
            user_id=current_user.id,
        )
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e

    if not files:
        # Empty list is acceptable; no 404
        return []

    return files
