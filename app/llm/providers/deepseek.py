from app.core.llm_provider import BaseLLMProvider
from typing import Any, Dict

class DeepSeekProvider(BaseLLMProvider):
    def __init__(self):
        self.config = {}

    def configure(self, config: Dict[str, Any]) -> None:
        self.config = config

    def generate(self, prompt: str, **kwargs) -> str:
        # Placeholder for DeepSeek generation
        return f"[DeepSeek] Response to: {prompt}"
