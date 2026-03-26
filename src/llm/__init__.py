"""OpenAI-compatible LLM client with submission-safe model locking."""
import json
import logging
from typing import AsyncGenerator, Optional

import httpx

from src.config import (
    ALLOWED_LLM_MODELS,
    EXPOSE_LLM_ENDPOINT_SWITCHER,
    LOCKED_LLM_MODEL,
    LLM_ENDPOINT,
    LLM_ENDPOINTS,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    PRIMARY_LLM_ENDPOINT_KEY,
    SUBMISSION_MODE,
)

logger = logging.getLogger(__name__)


class LLMClient:
    """OpenAI-compatible API client."""

    def __init__(self):
        self._set_endpoint(LLM_ENDPOINT)
        self.model = LOCKED_LLM_MODEL
        self.max_tokens = LLM_MAX_TOKENS
        self.temperature = LLM_TEMPERATURE
        self.current_endpoint_key = self._detect_initial_key()
        if SUBMISSION_MODE and PRIMARY_LLM_ENDPOINT_KEY in LLM_ENDPOINTS:
            self.current_endpoint_key = PRIMARY_LLM_ENDPOINT_KEY
        self._resolved_models: dict[str, str] = {self.current_endpoint_key: self.model}
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0))

    def _set_endpoint(self, url: str):
        endpoint, base_url = self._normalize_endpoint(url)
        self.endpoint = endpoint
        self._base_url = base_url

    @staticmethod
    def _normalize_endpoint(url: str) -> tuple[str, str]:
        base = url.rstrip("/")
        if not base.endswith("/chat/completions"):
            base = base + "/chat/completions"
        return base, base.replace("/chat/completions", "")

    def _endpoint_switching_enabled(self) -> bool:
        return (not SUBMISSION_MODE) and EXPOSE_LLM_ENDPOINT_SWITCHER

    def _resolve_target(self, endpoint_key: Optional[str] = None) -> dict:
        key = self.current_endpoint_key
        if endpoint_key and self._endpoint_switching_enabled():
            if endpoint_key not in LLM_ENDPOINTS:
                raise ValueError(f"Unknown LLM endpoint: {endpoint_key}")
            key = endpoint_key

        ep = LLM_ENDPOINTS.get(key, LLM_ENDPOINTS[PRIMARY_LLM_ENDPOINT_KEY])
        endpoint, base_url = self._normalize_endpoint(ep["url"])
        return {
            "key": key,
            "name": ep["name"],
            "endpoint": endpoint,
            "base_url": base_url,
            "model": LOCKED_LLM_MODEL,
        }

    def _detect_initial_key(self) -> str:
        for key, ep in LLM_ENDPOINTS.items():
            if ep["url"].rstrip("/") in self.endpoint:
                return key
        return PRIMARY_LLM_ENDPOINT_KEY if PRIMARY_LLM_ENDPOINT_KEY in LLM_ENDPOINTS else "company"

    def switch_endpoint(self, key: str) -> dict:
        if not self._endpoint_switching_enabled():
            raise ValueError("LLM endpoint switching is disabled in submission mode.")
        if key not in LLM_ENDPOINTS:
            raise ValueError(f"Unknown LLM endpoint: {key}")
        ep = LLM_ENDPOINTS[key]
        self._set_endpoint(ep["url"])
        self.model = LOCKED_LLM_MODEL
        self.current_endpoint_key = key
        self._resolved_models[key] = self.model
        logger.info("LLM endpoint switched: %s -> %s", key, ep["url"])
        return {**ep, "model": LOCKED_LLM_MODEL}

    async def auto_detect_model(self, endpoint_key: Optional[str] = None) -> str | None:
        target = self._resolve_target(endpoint_key)
        try:
            resp = await self._client.get(f"{target['base_url']}/models", timeout=5.0)
            resp.raise_for_status()
            data = resp.json()
            model_ids = {
                item.get("id")
                for item in data.get("data", [])
                if isinstance(item, dict)
            }
            if LOCKED_LLM_MODEL not in model_ids:
                raise ValueError(f"Locked model not available on {target['key']}")
            self._resolved_models[target["key"]] = LOCKED_LLM_MODEL
            return LOCKED_LLM_MODEL if LOCKED_LLM_MODEL in ALLOWED_LLM_MODELS else None
        except Exception as e:
            logger.warning("LLM model probe failed: %s", e)
            return None

    async def health_check(self, endpoint_key: Optional[str] = None) -> dict:
        target = self._resolve_target(endpoint_key)
        try:
            resp = await self._client.get(f"{target['base_url']}/models", timeout=5.0)
            resp.raise_for_status()
            data = resp.json()
            model_ids = {
                item.get("id")
                for item in data.get("data", [])
                if isinstance(item, dict)
            }
            if LOCKED_LLM_MODEL not in model_ids:
                raise ValueError(f"Locked model not available on {target['key']}")
            return {
                "status": "connected",
                "models": {
                    "object": "list",
                    "data": [
                        {
                            "id": LOCKED_LLM_MODEL,
                            "object": "model",
                            "locked": True,
                        }
                    ],
                },
                "key": target["key"],
                "name": target["name"],
                "model": LOCKED_LLM_MODEL,
                "submission_mode": SUBMISSION_MODE,
                "endpoint_switching": self._endpoint_switching_enabled(),
            }
        except Exception as e:
            return {
                "status": "disconnected",
                "error": str(e),
                "key": target["key"],
                "name": target["name"],
                "model": LOCKED_LLM_MODEL,
                "submission_mode": SUBMISSION_MODE,
                "endpoint_switching": self._endpoint_switching_enabled(),
            }

    def _is_ollama(self, target: dict) -> bool:
        return ":11434" in target.get("endpoint", "")

    def _build_messages(
        self,
        system_prompt: str,
        user_message: str,
        history: Optional[list[dict]] = None,
        disable_thinking: bool = False,
    ) -> list[dict]:
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        content = f"/no_think\n{user_message}" if disable_thinking else user_message
        messages.append({"role": "user", "content": content})
        return messages

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        history: Optional[list[dict]] = None,
        endpoint_key: Optional[str] = None,
    ) -> str:
        target = self._resolve_target(endpoint_key)
        if endpoint_key and self._endpoint_switching_enabled() and endpoint_key not in self._resolved_models:
            await self.auto_detect_model(endpoint_key)
        is_ollama = self._is_ollama(target)
        messages = self._build_messages(system_prompt, user_message, history, disable_thinking=is_ollama)
        payload = {
            "model": LOCKED_LLM_MODEL,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False,
        }
        if not is_ollama:
            payload["chat_template_kwargs"] = {"enable_thinking": False}
        try:
            resp = await self._client.post(target["endpoint"], json=payload)
            resp.raise_for_status()
            data = resp.json()
            message = data["choices"][0]["message"]
            content = message.get("content", "")
            if not content and message.get("reasoning"):
                content = message["reasoning"]
            return content
        except httpx.ConnectError:
            logger.error("LLM server connection failed: %s", target["endpoint"])
            raise
        except httpx.TimeoutException:
            logger.error("LLM request timed out: %s", target["endpoint"])
            raise

    async def generate_stream(
        self,
        system_prompt: str,
        user_message: str,
        history: Optional[list[dict]] = None,
        endpoint_key: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        target = self._resolve_target(endpoint_key)
        if endpoint_key and self._endpoint_switching_enabled() and endpoint_key not in self._resolved_models:
            await self.auto_detect_model(endpoint_key)
        is_ollama = self._is_ollama(target)
        messages = self._build_messages(system_prompt, user_message, history, disable_thinking=is_ollama)
        payload = {
            "model": LOCKED_LLM_MODEL,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": True,
        }
        if not is_ollama:
            payload["chat_template_kwargs"] = {"enable_thinking": False}
        try:
            async with self._client.stream("POST", target["endpoint"], json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "") or delta.get("reasoning", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
        except httpx.ConnectError:
            logger.error("LLM streaming connection failed: %s", target["endpoint"])
            raise
        except httpx.TimeoutException:
            logger.error("LLM streaming timed out: %s", target["endpoint"])
            raise
