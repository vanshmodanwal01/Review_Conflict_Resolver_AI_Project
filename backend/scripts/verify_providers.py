"""
Provider Verification Script
Validates Gemini and OpenAI provider configurations independently.
Does NOT print or expose secret API keys.
"""
import asyncio
import os
import sys

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.core.config import settings
from backend.ai.providers.gemini_provider import GeminiProvider
from backend.ai.providers.openai_provider import OpenAIProvider


async def verify_gemini():
    print("\n--- Verifying Google Gemini Integration ---")
    provider = GeminiProvider()
    print(f"Configured Model: {provider.model_name}")
    print(f"Is Configured: {provider.is_configured()}")
    
    if not provider.is_configured():
        print("Result: SKIPPED (API Key not configured)")
        return False
        
    try:
        res = await provider.generate_completion(
            system_prompt="You are a verification assistant. Respond ONLY with valid JSON.",
            user_prompt='Return a JSON object: {"status": "ok", "provider": "gemini"}'
        )
        print("Invocation: SUCCESS")
        print(f"Latency: {res.latency_seconds}s")
        print(f"Parsed JSON: {res.parsed_json}")
        return True
    except Exception as e:
        print(f"Invocation FAILED: {type(e).__name__} - {e}")
        return False


async def verify_openai():
    print("\n--- Verifying OpenAI Integration ---")
    provider = OpenAIProvider()
    print(f"Configured Model: {provider.model_name}")
    print(f"Is Configured: {provider.is_configured()}")
    
    if not provider.is_configured():
        print("Result: SKIPPED (API Key not configured)")
        return False
        
    try:
        res = await provider.generate_completion(
            system_prompt="You are a verification assistant. Respond ONLY with valid JSON.",
            user_prompt='Return a JSON object: {"status": "ok", "provider": "openai"}'
        )
        print("Invocation: SUCCESS")
        print(f"Latency: {res.latency_seconds}s")
        print(f"Parsed JSON: {res.parsed_json}")
        return True
    except Exception as e:
        print(f"Invocation FAILED: {type(e).__name__} - {e}")
        return False


async def main():
    print("========================================")
    print("Review Conflict Resolver - LLM Verification")
    print("========================================")
    gemini_ok = await verify_gemini()
    openai_ok = await verify_openai()
    print("\n========================================")
    print(f"Summary: Gemini={'PASS' if gemini_ok else 'FAIL/SKIP'}, OpenAI={'PASS' if openai_ok else 'FAIL/SKIP'}")
    print("========================================")


if __name__ == "__main__":
    asyncio.run(main())
