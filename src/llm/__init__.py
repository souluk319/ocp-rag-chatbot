"""Qwen3.5-9B 호출용 클라이언트. vLLM의 OpenAI-compatible API 사용."""
import json
import logging
from typing import AsyncGenerator, Optional
import httpx

from src.config import LLM_ENDPOINT, LLM_MODEL, LLM_MAX_TOKENS, LLM_TEMPERATURE

logger = logging.getLogger(__name__)


class LLMClient:
    """OpenAI-compatible API를 통한 LLM 호출 클라이언트"""

    def __init__(self):
        # vLLM은 /v1 까지만 주는 경우도 있고 /v1/chat/completions 전체 주는 경우도 있어서
        # 어떤 형태로 들어오든 처리되게 함
        base = LLM_ENDPOINT.rstrip("/")
        if not base.endswith("/chat/completions"):
            base = base + "/chat/completions"
        self.endpoint = base
        self.model = LLM_MODEL
        self.max_tokens = LLM_MAX_TOKENS
        self.temperature = LLM_TEMPERATURE
        # 커넥션 풀 재사용 — 매 요청마다 TCP 핸드셰이크 방지
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0))

    def _build_messages(
        self,
        system_prompt: str,
        user_message: str,
        history: Optional[list[dict]] = None,
    ) -> list[dict]:
        """LLM에 보낼 messages 배열 구성"""
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        return messages

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        history: Optional[list[dict]] = None,
    ) -> str:
        """비스트리밍 응답 생성"""
        messages = self._build_messages(system_prompt, user_message, history)
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False,
            # Qwen3.5 thinking 모드 비활성화 (빠른 응답)
            "chat_template_kwargs": {"enable_thinking": False},
        }
        try:
            resp = await self._client.post(self.endpoint, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except httpx.ConnectError:
            logger.error("LLM 서버 연결 실패: %s", self.endpoint)
            raise
        except httpx.TimeoutException:
            logger.error("LLM 응답 타임아웃: %s", self.endpoint)
            raise

    async def generate_stream(
        self,
        system_prompt: str,
        user_message: str,
        history: Optional[list[dict]] = None,
    ) -> AsyncGenerator[str, None]:
        """스트리밍 응답 생성 - 토큰 단위로 yield"""
        messages = self._build_messages(system_prompt, user_message, history)
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": True,
            # Qwen3.5 thinking 모드 비활성화 (빠른 응답)
            "chat_template_kwargs": {"enable_thinking": False},
        }
        try:
            async with self._client.stream("POST", self.endpoint, json=payload) as resp:
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
                        # Qwen3.5는 thinking 모드일 때 reasoning_content 필드로 내부 추론을 보내는데
                        # 사용자한테 보여줄 필요 없으니 content만 취함
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
        except httpx.ConnectError:
            logger.error("LLM 서버 연결 실패 (스트리밍): %s", self.endpoint)
            raise
        except httpx.TimeoutException:
            logger.error("LLM 스트리밍 타임아웃: %s", self.endpoint)
            raise
