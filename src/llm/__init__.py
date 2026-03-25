"""Qwen3.5-9B 호출용 클라이언트. vLLM의 OpenAI-compatible API 사용."""
import json
import logging
from typing import AsyncGenerator, Optional
import httpx

from src.config import LLM_ENDPOINT, LLM_MODEL, LLM_MAX_TOKENS, LLM_TEMPERATURE, LLM_ENDPOINTS

logger = logging.getLogger(__name__)


class LLMClient:
    """OpenAI-compatible API를 통한 LLM 호출 클라이언트"""

    def __init__(self):
        # vLLM은 /v1 까지만 주는 경우도 있고 /v1/chat/completions 전체 주는 경우도 있어서
        # 어떤 형태로 들어오든 처리되게 함
        self._set_endpoint(LLM_ENDPOINT)
        self.model = LLM_MODEL
        self.max_tokens = LLM_MAX_TOKENS
        self.temperature = LLM_TEMPERATURE
        self.current_endpoint_key = self._detect_initial_key()
        self._resolved_models: dict[str, str] = {self.current_endpoint_key: self.model}
        # 커넥션 풀 재사용 — 매 요청마다 TCP 핸드셰이크 방지
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0))

    def _set_endpoint(self, url: str):
        """엔드포인트 URL 정규화"""
        endpoint, base_url = self._normalize_endpoint(url)
        self.endpoint = endpoint
        self._base_url = base_url

    @staticmethod
    def _normalize_endpoint(url: str) -> tuple[str, str]:
        """엔드포인트 URL 정규화"""
        base = url.rstrip("/")
        if not base.endswith("/chat/completions"):
            base = base + "/chat/completions"
        return base, base.replace("/chat/completions", "")

    def _resolve_target(self, endpoint_key: Optional[str] = None) -> dict:
        """요청 단위 endpoint/model 결정"""
        if endpoint_key:
            if endpoint_key not in LLM_ENDPOINTS:
                raise ValueError(f"알 수 없는 엔드포인트: {endpoint_key}")
            ep = LLM_ENDPOINTS[endpoint_key]
            endpoint, base_url = self._normalize_endpoint(ep["url"])
            return {
                "key": endpoint_key,
                "name": ep["name"],
                "endpoint": endpoint,
                "base_url": base_url,
                "model": self._resolved_models.get(endpoint_key, ep["model"]),
            }
        current = LLM_ENDPOINTS.get(self.current_endpoint_key, {})
        return {
            "key": self.current_endpoint_key,
            "name": current.get("name", self.current_endpoint_key),
            "endpoint": self.endpoint,
            "base_url": self._base_url,
            "model": self.model,
        }

    def _detect_initial_key(self) -> str:
        """현재 endpoint가 어떤 key에 해당하는지 역추적"""
        for key, ep in LLM_ENDPOINTS.items():
            if ep["url"].rstrip("/") in self.endpoint:
                return key
        return "company"

    def switch_endpoint(self, key: str) -> dict:
        """런타임에 LLM 엔드포인트 전환"""
        if key not in LLM_ENDPOINTS:
            raise ValueError(f"알 수 없는 엔드포인트: {key}")
        ep = LLM_ENDPOINTS[key]
        self._set_endpoint(ep["url"])
        self.model = ep["model"]
        self.current_endpoint_key = key
        self._resolved_models[key] = ep["model"]
        logger.info("LLM 엔드포인트 전환: %s → %s", key, ep["url"])
        return ep

    async def auto_detect_model(self, endpoint_key: Optional[str] = None) -> str | None:
        """서버에서 실제 사용 가능한 모델명을 가져와서 자동 설정"""
        target = self._resolve_target(endpoint_key)
        try:
            resp = await self._client.get(f"{target['base_url']}/models", timeout=5.0)
            resp.raise_for_status()
            data = resp.json()
            models = data.get("data", [])
            if models:
                actual_model = models[0]["id"]
                resolved_key = endpoint_key or self.current_endpoint_key
                self._resolved_models[resolved_key] = actual_model
                if endpoint_key and endpoint_key != self.current_endpoint_key:
                    return actual_model
                if actual_model != self.model:
                    logger.info("모델명 자동 감지: %s → %s", self.model, actual_model)
                    self.model = actual_model
                return actual_model
        except Exception as e:
            logger.warning("모델 자동 감지 실패: %s", e)
        return None

    async def health_check(self, endpoint_key: Optional[str] = None) -> dict:
        """현재 엔드포인트 연결 상태 확인"""
        target = self._resolve_target(endpoint_key)
        try:
            resp = await self._client.get(f"{target['base_url']}/models", timeout=5.0)
            resp.raise_for_status()
            return {"status": "connected", "models": resp.json(), "key": target["key"], "name": target["name"]}
        except Exception as e:
            return {"status": "disconnected", "error": str(e), "key": target["key"], "name": target["name"]}

    def _is_ollama(self, target: dict) -> bool:
        """Ollama 서버인지 판별 (포트 11434)"""
        return ":11434" in target.get("endpoint", "")

    def _build_messages(
        self,
        system_prompt: str,
        user_message: str,
        history: Optional[list[dict]] = None,
        disable_thinking: bool = False,
    ) -> list[dict]:
        """LLM에 보낼 messages 배열 구성"""
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        # Ollama Qwen3.5: /no_think 토큰으로 thinking 모드 비활성화
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
        """비스트리밍 응답 생성"""
        target = self._resolve_target(endpoint_key)
        if endpoint_key and endpoint_key not in self._resolved_models:
            detected = await self.auto_detect_model(endpoint_key)
            if detected:
                target = self._resolve_target(endpoint_key)
        is_ollama = self._is_ollama(target)
        messages = self._build_messages(system_prompt, user_message, history, disable_thinking=is_ollama)
        payload = {
            "model": target["model"],
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False,
        }
        # vLLM 전용: chat_template_kwargs로 thinking 비활성화
        if not is_ollama:
            payload["chat_template_kwargs"] = {"enable_thinking": False}
        try:
            resp = await self._client.post(target["endpoint"], json=payload)
            resp.raise_for_status()
            data = resp.json()
            message = data["choices"][0]["message"]
            content = message.get("content", "")
            # Ollama Qwen3.5 thinking 모드 fallback: reasoning 필드 확인
            if not content and message.get("reasoning"):
                content = message["reasoning"]
            return content
        except httpx.ConnectError:
            logger.error("LLM 서버 연결 실패: %s", target["endpoint"])
            raise
        except httpx.TimeoutException:
            logger.error("LLM 응답 타임아웃: %s", target["endpoint"])
            raise

    async def generate_stream(
        self,
        system_prompt: str,
        user_message: str,
        history: Optional[list[dict]] = None,
        endpoint_key: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """스트리밍 응답 생성 - 토큰 단위로 yield"""
        target = self._resolve_target(endpoint_key)
        if endpoint_key and endpoint_key not in self._resolved_models:
            detected = await self.auto_detect_model(endpoint_key)
            if detected:
                target = self._resolve_target(endpoint_key)
        is_ollama = self._is_ollama(target)
        messages = self._build_messages(system_prompt, user_message, history, disable_thinking=is_ollama)
        payload = {
            "model": target["model"],
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": True,
        }
        # vLLM 전용: chat_template_kwargs로 thinking 비활성화
        if not is_ollama:
            payload["chat_template_kwargs"] = {"enable_thinking": False}
        try:
            async with self._client.stream("POST", target["endpoint"], json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]  # "data: " 제거
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        # Ollama Qwen3.5 thinking 모드: content가 비고 reasoning에 토큰이 옴
                        if not content:
                            content = delta.get("reasoning", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
        except httpx.ConnectError:
            logger.error("LLM 서버 연결 실패 (스트리밍): %s", target["endpoint"])
            raise
        except httpx.TimeoutException:
            logger.error("LLM 스트리밍 타임아웃: %s", target["endpoint"])
            raise
