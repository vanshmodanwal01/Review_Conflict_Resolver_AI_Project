"""Google Gemini Provider Implementation (Official Google GenAI SDK)"""
import time
import json
import re
from typing import Optional, Dict, Any
from backend.ai.providers.base_provider import BaseLLMProvider, LLMResponse
from backend.core.config import settings
from backend.core.logging import logger
from backend.core.exceptions import LLMProviderError


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini Provider utilizing the modern Google GenAI SDK.
    Primary default provider for Review Conflict Resolver.
    """
    def __init__(self):
        super().__init__(provider_name="gemini", model_name=settings.GEMINI_MODEL)
        self.api_key = settings.GEMINI_API_KEY
        self._client = None

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key != "your_gemini_api_key_here" and len(self.api_key.strip()) > 10)

    def get_client(self):
        if self._client is None and self.is_configured():
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Google GenAI Client: {e}")
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
            raise LLMProviderError("Gemini API key is not configured or client failed to initialize.")

        start_time = time.time()
        try:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
            )
            
            latency = time.time() - start_time
            text_out = response.text or ""
            parsed = self._extract_json(text_out)
            
            return LLMResponse(
                provider=self.provider_name,
                model_name=self.model_name,
                content=text_out,
                parsed_json=parsed,
                tokens_consumed=len(text_out.split()),
                latency_seconds=round(latency, 2)
            )
        except Exception as e:
            logger.error(f"Gemini API invocation error: {e}")
            raise LLMProviderError(f"Gemini API error: {str(e)}")

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        try:
            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```(?:json)?", "", cleaned).rstrip("`").strip()
            return json.loads(cleaned)
        except Exception:
            return None
