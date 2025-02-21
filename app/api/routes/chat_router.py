from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.chat_service import ChatService
from app.api.dependencies import get_current_user
from app.db.schemas.user_schemas import UserBase as User

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    agent_id: int
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, user: User = Depends(get_current_user)):
    result = ChatService.process_chat(request.agent_id, request.message, user.id)
    if not result:
        raise HTTPException(status_code=500, detail="Chat processing failed")
    return ChatResponse(response=result)
