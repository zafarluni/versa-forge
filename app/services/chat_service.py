from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PermissionDeniedError, ResourceNotFoundError
from app.llm.llm_manager import LLMManager
from app.services.agent_service import AgentService


class ChatService:
    @staticmethod
    async def process_chat(
        db_session: AsyncSession,
        agent_id: int,
        message: str,
        user_id: int,
    ) -> str:
        """
        Orchestrates a chat turn:
        1. Fetch agent with access control.
        2. Build the prompt (system + user).
        3. Call the async LLM provider.
        """
        # 1. Validate agent exists and user has permission
        try:
            agent = await AgentService.get_agent_by_id(db_session, agent_id=agent_id, user_id=user_id)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
        except PermissionDeniedError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e

        # 2. Build the combined prompt
        system_prompt = agent.prompt
        full_prompt = f"{system_prompt}\n\nUser: {message}\nAssistant:"

        # 3. Select and call LLM provider
        #    (make sure each provider.generate is async)
        provider_name = getattr(agent, "provider_name", "openai")
        provider = LLMManager.get_provider(provider_name)

        try:
            response = await provider.generate(full_prompt)
        except Exception as e:
            # You could implement failover here
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="LLM provider error",
            ) from e

        return response
