from __future__ import annotations

import time
from typing import Any, Optional, Protocol

from .prompt_builder import Prompt


class LLMClient(Protocol):
    def complete(self, prompt: Prompt) -> str:
        ...


class LLMClientError(Exception):
    """Raised when the LLM provider fails after retries."""


class MockLLMClient:
    """Test double that returns a fixed LLM response string."""

    def __init__(self, response: str) -> None:
        self._response = response
        self.last_prompt: Optional[Prompt] = None

    def complete(self, prompt: Prompt) -> str:
        self.last_prompt = prompt
        return self._response


class GroqLLMClient:
    """Groq chat-completions client (OpenAI-compatible API)."""

    def __init__(
        self,
        api_key: str,
        model: str,
        *,
        temperature: float = 0.3,
        max_retries: int = 1,
        timeout: float = 60.0,
        use_json_mode: bool = True,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("Groq API key is required. Set GROQ_API_KEY or LLM_API_KEY in .env")

        from groq import Groq  # lazy import so tests can run without groq installed in some envs

        self._client = Groq(api_key=api_key.strip(), timeout=timeout)
        self._model = model
        self._temperature = temperature
        self._max_retries = max(0, max_retries)
        self._use_json_mode = use_json_mode
        self.last_prompt: Optional[Prompt] = None

    def complete(self, prompt: Prompt) -> str:
        self.last_prompt = prompt
        messages = [
            {"role": "system", "content": prompt.system},
            {"role": "user", "content": prompt.user},
        ]

        last_error: Optional[Exception] = None
        attempts = self._max_retries + 1

        for attempt in range(attempts):
            try:
                content = self._call_api(messages, json_mode=self._use_json_mode)
                if content:
                    return content
                raise LLMClientError("Groq returned an empty response")
            except LLMClientError:
                raise
            except Exception as exc:
                last_error = exc
                if attempt < attempts - 1:
                    time.sleep(1.0 * (attempt + 1))
                    continue

        raise LLMClientError(f"Groq API failed after {attempts} attempt(s): {last_error}") from last_error

    def _call_api(self, messages: list[dict[str, str]], *, json_mode: bool) -> str:
        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": self._temperature,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = self._client.chat.completions.create(**kwargs)
        except Exception as exc:
            # Some models/endpoints may reject response_format; retry without JSON mode.
            if json_mode and _is_json_mode_error(exc):
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    temperature=self._temperature,
                )
            else:
                raise

        return (response.choices[0].message.content or "").strip()


def _is_json_mode_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "response_format" in msg or "json_object" in msg or "unsupported" in msg
