"""OpenAI Alternative / Fallback Provider Implementation"""
import time
import json
import re
from typing import Optional, Dict, Any
from backend.ai.providers.base_provider import BaseLLMProvider, LLMResponse
from backend.core.config import settings
from backend.core.logging import logger
from backend.core.exceptions import LLMProviderError


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI Provider (GPT-4o-mini).
    Alternative and secondary fallback provider.
    """
    def __init__(self):
        super().__init__(provider_name="openai", model_name=settings.OPENAI_MODEL)
        self.api_key = settings.OPENAI_API_KEY
        self._client = None

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key != "your_openai_api_key_here" and len(self.api_key.strip()) > 10)

    def get_client(self):
        if self._client is None and self.is_configured():
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI Client: {e}")
                self._client = None
        return self._client

    async def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2
    ) -> LLMResponse:
        client = self.get_client()
        if not client:
            raise LLMProviderError("OpenAI API key is not configured or client failed to initialize.")

        start_time = time.time()
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            latency = time.time() - start_time
            text_out = response.choices[0].message.content or ""
            parsed = json.loads(text_out)

            return LLMResponse(
                provider=self.provider_name,
                model_name=self.model_name,
                content=text_out,
                parsed_json=parsed,
                tokens_consumed=response.usage.total_tokens if response.usage else 0,
                latency_seconds=round(latency, 2)
            )
        except Exception as e:
            logger.error(f"OpenAI API invocation error: {e}")
            raise LLMProviderError(f"OpenAI API error: {str(e)}")
