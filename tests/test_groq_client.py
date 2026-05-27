from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from app.services.llm_client import GroqLLMClient, LLMClientError
from app.services.llm_factory import create_llm_client, resolve_api_key
from app.services.prompt_builder import Prompt
from app.config import Settings


def _prompt() -> Prompt:
    return Prompt(system="sys", user="user")


def _mock_completion(content: str) -> MagicMock:
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    response = MagicMock()
    response.choices = [choice]
    return response


@patch("groq.Groq")
def test_groq_complete_success(MockGroq: MagicMock) -> None:
    payload = json.dumps({"summary": "ok", "recommendations": []})
    client_instance = MagicMock()
    client_instance.chat.completions.create.return_value = _mock_completion(payload)
    MockGroq.return_value = client_instance

    client = GroqLLMClient(api_key="test-key", model="llama-3.3-70b-versatile")
    result = client.complete(_prompt())

    assert json.loads(result)["summary"] == "ok"
    MockGroq.assert_called_once_with(api_key="test-key", timeout=60.0)
    call_kwargs = client_instance.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "llama-3.3-70b-versatile"
    assert call_kwargs["response_format"] == {"type": "json_object"}


@patch("groq.Groq")
def test_groq_retries_then_succeeds(MockGroq: MagicMock) -> None:
    client_instance = MagicMock()
    client_instance.chat.completions.create.side_effect = [
        TimeoutError("timeout"),
        _mock_completion('{"summary": "retry ok", "recommendations": []}'),
    ]
    MockGroq.return_value = client_instance

    client = GroqLLMClient(api_key="test-key", model="llama-3.3-70b-versatile", max_retries=1)
    result = client.complete(_prompt())
    assert json.loads(result)["summary"] == "retry ok"
    assert client_instance.chat.completions.create.call_count == 2


@patch("groq.Groq")
def test_groq_raises_llm_client_error_after_retries(MockGroq: MagicMock) -> None:
    client_instance = MagicMock()
    client_instance.chat.completions.create.side_effect = RuntimeError("upstream down")
    MockGroq.return_value = client_instance

    client = GroqLLMClient(api_key="test-key", model="llama-3.3-70b-versatile", max_retries=1)
    with pytest.raises(LLMClientError, match="Groq API failed"):
        client.complete(_prompt())


def test_groq_requires_api_key() -> None:
    with pytest.raises(ValueError, match="API key"):
        GroqLLMClient(api_key="", model="llama-3.3-70b-versatile")


def test_resolve_api_key_prefers_groq_key() -> None:
    settings = Settings(GROQ_API_KEY="groq-key", LLM_API_KEY="other")
    assert resolve_api_key(settings) == "groq-key"


def test_create_llm_client_groq() -> None:
    settings = Settings(
        LLM_PROVIDER="groq",
        GROQ_API_KEY="test-key",
        LLM_MODEL="llama-3.3-70b-versatile",
    )
    with patch("groq.Groq"):
        client = create_llm_client(settings)
    assert isinstance(client, GroqLLMClient)


def test_create_llm_client_mock_provider() -> None:
    settings = Settings(LLM_PROVIDER="mock")
    client = create_llm_client(settings)
    from app.services.llm_client import MockLLMClient

    assert isinstance(client, MockLLMClient)
