# ruff: noqa: B008
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.schemas.user_schemas import UserResponse
from app.services.chat_service import ChatService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    agent_id: int
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Send a message to an agent and receive a response",
)
async def chat_endpoint(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> ChatResponse:
    """
    Send a user message to the specified agent.
    Returns the agent’s LLM-generated response.
    """
    try:
        reply = await ChatService.process_chat(
            db_session=db,
            agent_id=request.agent_id,
            message=request.message,
            user_id=current_user.id,
        )
    except HTTPException:
        # Re-raise HTTPExceptions for authorization or not-found
        raise
    except Exception as exc:
        # Catch-all for unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat processing failed",
        ) from exc

    return ChatResponse(response=reply)
