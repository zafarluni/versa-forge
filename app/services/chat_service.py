# from app.llm.llm_manager import LLMManager

# class ChatService:
#     @staticmethod
#     def process_chat(agent_id: int, message: str, user_id: int) -> str:
#         # For demonstration, retrieve provider configuration based on agent_id (placeholder logic)
#         provider_config = {"provider": "openai"}  # This should be retrieved from the agent configuration
#         provider = LLMManager.get_provider(provider_config["provider"])
#         response = provider.generate(prompt=message)
#         return response
