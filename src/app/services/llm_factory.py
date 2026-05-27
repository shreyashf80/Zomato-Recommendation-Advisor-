from __future__ import annotations

from ..config import Settings
from .llm_client import GroqLLMClient, LLMClient, LLMClientError, MockLLMClient


def resolve_api_key(settings: Settings) -> str:
    key = (settings.groq_api_key or settings.llm_api_key or "").strip()
    if not key:
        raise LLMClientError(
            "Missing API key. Set GROQ_API_KEY or LLM_API_KEY in your .env file."
        )
    return key


def create_llm_client(settings: Settings) -> LLMClient:
    provider = (settings.llm_provider or "groq").strip().lower()

    if provider == "mock":
        return MockLLMClient('{"summary": "mock", "recommendations": []}')

    if provider == "groq":
        return GroqLLMClient(
            api_key=resolve_api_key(settings),
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            max_retries=settings.llm_max_retries,
            timeout=settings.llm_timeout_seconds,
            use_json_mode=settings.llm_json_mode,
        )

    raise LLMClientError(
        f"Unsupported LLM_PROVIDER '{settings.llm_provider}'. Supported: groq, mock."
    )
