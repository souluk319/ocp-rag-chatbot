"""세션 + 쿼리 리라이터. 멀티턴 대화에서 "그거 뭐야?" 같은 질문을 독립적인 질문으로 변환."""
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from src.config import MAX_HISTORY_TURNS, SESSION_TTL_SECONDS
from src.llm import LLMClient


@dataclass
class Message:
    """대화 메시지"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class Session:
    """하나의 대화 세션"""
    session_id: str
    messages: list[Message] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)
    # 대화에서 추출된 핵심 주제/엔티티
    topics: list[str] = field(default_factory=list)

    def add_message(self, role: str, content: str):
        self.messages.append(Message(role=role, content=content))
        self.last_active = time.time()

    def get_history(self, max_turns: int = MAX_HISTORY_TURNS) -> list[dict]:
        """최근 N턴의 대화 이력을 LLM 포맷으로 반환"""
        recent = self.messages[-max_turns * 2:]  # user+assistant 쌍
        return [{"role": m.role, "content": m.content} for m in recent]

    def get_summary_context(self) -> str:
        """대화 이력 요약 (Query Rewriting 시 사용)"""
        # 3턴이면 충분. 더 넣으면 rewrite 프롬프트가 길어져서 오히려 결과가 애매해짐
        recent = self.messages[-6:]
        lines = []
        for m in recent:
            prefix = "사용자" if m.role == "user" else "AI"
            lines.append(f"{prefix}: {m.content[:200]}")
        return "\n".join(lines)

    def is_expired(self, ttl: int = SESSION_TTL_SECONDS) -> bool:
        return time.time() - self.last_active > ttl


class SessionManager:
    """세션 관리자 - 생성, 조회, 만료 정리"""

    def __init__(self):
        self._sessions: dict[str, Session] = {}

    def create_session(self) -> Session:
        session_id = str(uuid.uuid4())[:8]
        session = Session(session_id=session_id)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        session = self._sessions.get(session_id)
        if session and session.is_expired():
            del self._sessions[session_id]
            return None
        return session

    def get_or_create(self, session_id: Optional[str] = None) -> Session:
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session
        return self.create_session()

    def cleanup_expired(self):
        """만료된 세션 정리"""
        expired = [sid for sid, s in self._sessions.items() if s.is_expired()]
        for sid in expired:
            del self._sessions[sid]

    def list_sessions(self) -> list[dict]:
        self.cleanup_expired()
        return [
            {
                "session_id": s.session_id,
                "message_count": len(s.messages),
                "last_active": s.last_active,
            }
            for s in self._sessions.values()
        ]


class QueryRewriter:
    """대화 맥락 기반 쿼리 재작성기

    멀티턴 대화에서 "그건 뭐야?", "더 알려줘" 같은 맥락 의존적 질문을
    독립적인(standalone) 질문으로 변환.

    방법:
    - 이전 대화 이력을 분석하여 대명사, 생략된 주어 등을 복원
    - LLM을 사용하여 자연스러운 재작성 수행
    """

    REWRITE_PROMPT = """당신은 대화 맥락을 분석하여 질문을 재작성하는 도우미입니다.

아래 대화 이력을 참고하여, 사용자의 최신 질문을 **독립적으로 이해할 수 있는 질문**으로 재작성하세요.

규칙:
1. 대명사(그것, 이것, 거기 등)를 구체적인 대상으로 대체
2. 생략된 주어나 목적어를 복원
3. 이미 독립적인 질문이면 그대로 반환
4. 재작성된 질문만 출력 (설명 없이)

대화 이력:
{history}

최신 질문: {query}

재작성된 질문:"""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def rewrite(self, query: str, session: Session) -> str:
        """맥락 기반 쿼리 재작성"""
        # 대화 이력이 없으면 원본 반환
        if len(session.messages) < 2:
            return query

        # 맥락 의존적 키워드 체크 — 전부 LLM 태우면 느리니까 간단한 필터로 거름
        # FIXME: "왜", "어떻게"는 독립적 질문에서도 등장하는데 일단 넣어둠. 오탐 생기면 빼야 할 듯
        context_dependent_patterns = [
            "그것", "그건", "이것", "이건", "거기", "여기",
            "그거", "이거", "위에", "아까", "그러면",
            "더 알려", "자세히", "예시", "다른",
            "왜", "어떻게",  # 단독 사용 시
        ]
        needs_rewrite = any(p in query for p in context_dependent_patterns)

        # 짧은 질문(5자 미만)도 맥락 의존 가능성 높음
        if len(query.strip()) < 5:
            needs_rewrite = True

        if not needs_rewrite:
            return query

        # LLM으로 재작성
        history_context = session.get_summary_context()
        prompt = self.REWRITE_PROMPT.format(history=history_context, query=query)

        try:
            rewritten = await self.llm_client.generate(
                system_prompt="질문을 재작성하세요.",
                user_message=prompt,
            )
            rewritten = rewritten.strip().strip('"').strip("'")
            # 결과가 비어있거나 너무 길면 원본 사용
            if not rewritten or len(rewritten) > len(query) * 3:
                return query
            return rewritten
        except Exception:
            return query
