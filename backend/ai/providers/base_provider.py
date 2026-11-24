"""Abstract Base Class for Large Language Model Providers"""
import abc
from typing import Dict, Any, Optional
from pydantic import BaseModel


class LLMResponse(BaseModel):
    provider: str
    model_name: str
    content: str
    parsed_json: Optional[Dict[str, Any]] = None
    tokens_consumed: int = 0
    latency_seconds: float = 0.0


class BaseLLMProvider(abc.ABC):
    """
    Unified abstract interface for LLM providers (Google Gemini, OpenAI).
    Enforces standardized execution, timeout, and structured JSON parsing.
    """
    def __init__(self, provider_name: str, model_name: str):
        self.provider_name = provider_name
        self.model_name = model_name

    @abc.abstractmethod
    def is_configured(self) -> bool:
        """Returns True if required API credentials are set."""
        pass

    @abc.abstractmethod
    async def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2
    ) -> LLMResponse:
        """Executes completion request and returns standardized LLMResponse."""
        pass
