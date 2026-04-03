from __future__ import annotations

import json
import time

import requests

from ocp_rag_part1.settings import Settings


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        if not settings.llm_endpoint:
            raise ValueError("LLM_ENDPOINT must be configured")
        if not settings.llm_model:
            raise ValueError("LLM_MODEL must be configured")
        self.endpoint = settings.llm_endpoint
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        self.timeout = max(settings.request_timeout_seconds, 120)

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            return {}
        if " " in self.api_key.strip():
            return {"Authorization": self.api_key.strip()}
        return {"Authorization": f"Bearer {self.api_key}"}

    def _native_endpoint(self) -> str:
        if self.endpoint.endswith("/v1"):
            return self.endpoint[: -len("/v1")]
        return self.endpoint

    def _prefer_ollama_native(self) -> bool:
        return ":" in self.model and "/" not in self.model

    def _post_openai(
        self,
        messages: list[dict[str, str]],
        *,
        include_reasoning_controls: bool,
    ) -> requests.Response:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if include_reasoning_controls:
            payload["reasoning"] = False
            payload["chat_template_kwargs"] = {"enable_thinking": False}
        return requests.post(
            f"{self.endpoint}/chat/completions",
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )

    def _parse_openai_payload(self, payload: dict) -> str:
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
        if isinstance(content, str) and content.strip():
            return content.strip()
        if payload.get("system_fingerprint") == "fp_ollama" or isinstance(
            message.get("reasoning"),
            str,
        ):
            raise ValueError("Ollama OpenAI payload is missing final content")
        raise ValueError("LLM response is missing message content")

    def _generate_openai(self, messages: list[dict[str, str]]) -> str:
        response = self._post_openai(messages, include_reasoning_controls=True)
        if response.status_code == 400:
            response_text = response.text.lower()
            if "reasoning" in response_text or "chat_template_kwargs" in response_text:
                response = self._post_openai(messages, include_reasoning_controls=False)
        response.raise_for_status()
        try:
            payload = response.json()
        except json.JSONDecodeError as exc:
            raise ValueError("LLM response is not valid JSON") from exc
        return self._parse_openai_payload(payload)

    def _generate_ollama_native(self, messages: list[dict[str, str]]) -> str:
        response = requests.post(
            f"{self._native_endpoint()}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "think": False,
            },
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        message = payload.get("message") or {}
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Ollama native response is missing message content")
        return content.strip()

    def generate(self, messages: list[dict[str, str]], trace_callback=None) -> str:
        def emit(
            *,
            step: str,
            label: str,
            status: str,
            detail: str = "",
            duration_ms: float | None = None,
            meta: dict | None = None,
        ) -> None:
            if trace_callback is None:
                return
            event = {
                "type": "trace",
                "step": step,
                "label": label,
                "status": status,
            }
            if detail:
                event["detail"] = detail
            if duration_ms is not None:
                event["duration_ms"] = round(duration_ms, 1)
            if meta:
                event["meta"] = meta
            trace_callback(event)

        def generate_openai() -> str:
            openai_started_at = time.perf_counter()
            emit(
                step="llm_generate",
                label="LLM 응답 생성 중",
                status="running",
                detail=f"provider=openai-compatible model={self.model}",
            )
            content = self._generate_openai(messages)
            emit(
                step="llm_generate",
                label="LLM 응답 생성 완료",
                status="done",
                detail=f"provider=openai-compatible model={self.model}",
                duration_ms=(time.perf_counter() - openai_started_at) * 1000,
                meta={"provider": "openai-compatible", "model": self.model},
            )
            return content

        def generate_ollama() -> str:
            ollama_started_at = time.perf_counter()
            emit(
                step="llm_generate_fallback",
                label="Ollama 네이티브 호출 중",
                status="running",
                detail=f"provider=ollama-native model={self.model}",
            )
            content = self._generate_ollama_native(messages)
            emit(
                step="llm_generate_fallback",
                label="Ollama 네이티브 호출 완료",
                status="done",
                detail=f"provider=ollama-native model={self.model}",
                duration_ms=(time.perf_counter() - ollama_started_at) * 1000,
                meta={"provider": "ollama-native", "model": self.model},
            )
            return content

        prefer_ollama_native = self._prefer_ollama_native()
        ordered_generators = (
            [("ollama-native", generate_ollama), ("openai-compatible", generate_openai)]
            if prefer_ollama_native
            else [("openai-compatible", generate_openai), ("ollama-native", generate_ollama)]
        )

        original_error: Exception | None = None
        for provider_name, generator in ordered_generators:
            try:
                return generator()
            except Exception as exc:  # noqa: BLE001
                if original_error is None:
                    original_error = exc
                label = (
                    "Ollama 네이티브 호출 실패"
                    if provider_name == "ollama-native"
                    else "OpenAI 호환 호출 실패, 대체 경로 시도"
                )
                step = (
                    "llm_generate_fallback"
                    if provider_name == "ollama-native"
                    else "llm_generate"
                )
                emit(
                    step=step,
                    label=label,
                    status="warning",
                    detail=str(exc),
                    meta={"provider": provider_name, "model": self.model},
                )

        if original_error is not None:
            raise original_error
        raise ValueError("LLM generation failed without a provider error")
