from __future__ import annotations

import requests

from ocp_rag_part1.settings import Settings


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        if not settings.llm_endpoint:
            raise ValueError("LLM_ENDPOINT must be configured")
        if not settings.llm_model:
            raise ValueError("LLM_MODEL must be configured")
        self.endpoint = settings.llm_endpoint
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        self.timeout = max(settings.request_timeout_seconds, 120)

    def generate(self, messages: list[dict[str, str]]) -> str:
        response = requests.post(
            f"{self.endpoint}/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "reasoning": False,
                "chat_template_kwargs": {"enable_thinking": False},
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        choices = payload.get("choices") or []
        if not choices:
            raise ValueError("LLM response is missing choices")
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    parts.append(item["text"])
            content = "\n".join(parts).strip()
        if not isinstance(content, str) or not content.strip():
            raise ValueError("LLM response is missing message content")
        return content.strip()
