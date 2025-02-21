from typing import Dict, Any
from app.llm.providers.openai import OpenAIProvider
from app.llm.providers.llama import LlamaProvider
from app.llm.providers.vllm import VLLMProvider
from app.llm.providers.deepseek import DeepSeekProvider
from app.llm.providers.groq import GroqProvider
from app.core.llm_provider import BaseLLMProvider

class LLMManager:
    providers: Dict[str, BaseLLMProvider] = {
        "openai": OpenAIProvider(),
        "llama": LlamaProvider(),
        "vllm": VLLMProvider(),
        "deepseek": DeepSeekProvider(),
        "groq": GroqProvider(),
    }

    @classmethod
    def get_provider(cls, provider_name: str) -> BaseLLMProvider:
        provider = cls.providers.get(provider_name.lower())
        if not provider:
            raise ValueError(f"LLM provider '{provider_name}' is not supported.")
        return provider

    @classmethod
    def configure_provider(cls, provider_name: str, config: Dict[str, Any]) -> None:
        provider = cls.get_provider(provider_name)
        provider.configure(config)
