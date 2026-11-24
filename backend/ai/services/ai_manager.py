"""AI Provider Manager for Model Selection and Resilient Fallback"""
from typing import Dict, Any, Optional
from backend.ai.providers.base_provider import BaseLLMProvider, LLMResponse
from backend.ai.providers.gemini_provider import GeminiProvider
from backend.ai.providers.openai_provider import OpenAIProvider
from backend.core.config import settings
from backend.core.logging import logger
from backend.core.exceptions import LLMProviderError


class AIManager:
    """
    Coordinates external LLM providers (Google Gemini default, OpenAI fallback).
    Enforces automatic fallback, structured validation, and token logging.
    """
    def __init__(self):
        self.gemini_provider = GeminiProvider()
        self.openai_provider = OpenAIProvider()
        self.default_provider_name = settings.DEFAULT_LLM_PROVIDER.lower()

    def get_preferred_provider(self, override: Optional[str] = None) -> BaseLLMProvider:
        provider_name = (override or self.default_provider_name).lower()
        
        # Primary selection
        if provider_name == "gemini" and self.gemini_provider.is_configured():
            return self.gemini_provider
        if provider_name == "openai" and self.openai_provider.is_configured():
            return self.openai_provider

        # Fallbacks
        if self.gemini_provider.is_configured():
            return self.gemini_provider
        if self.openai_provider.is_configured():
            return self.openai_provider

        # Neither is configured with active keys
        return self.gemini_provider

    async def execute_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        provider_preference: Optional[str] = None
    ) -> LLMResponse:
        """
        Executes completion with automatic fallback between Gemini and OpenAI.
        """
        primary = self.get_preferred_provider(provider_preference)
        secondary = (
            self.openai_provider if primary.provider_name == "gemini"
            else self.gemini_provider
        )

        try:
            if primary.is_configured():
                return await primary.generate_completion(system_prompt, user_prompt, temperature)
        except Exception as e:
            logger.warning(f"Primary LLM ({primary.provider_name}) failed: {e}. Attempting fallback...")
            if secondary.is_configured():
                return await secondary.generate_completion(system_prompt, user_prompt, temperature)
            raise e

        raise LLMProviderError("No LLM provider is currently configured with active credentials.")

ai_manager = AIManager()
