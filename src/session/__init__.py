"""세션 + 쿼리 리라이터. 멀티턴 대화에서 "그거 뭐야?" 같은 질문을 독립적인 질문으로 변환."""
import json
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from src.config import MAX_HISTORY_TURNS, SESSION_TTL_SECONDS
from src.llm import LLMClient

_REDIS_KEY_PREFIX = "ocp-rag:session:"


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

    def to_dict(self) -> dict:
        """Redis 저장용 직렬화"""
        return {
            "session_id": self.session_id,
            "messages": [
                {"role": m.role, "content": m.content, "timestamp": m.timestamp}
                for m in self.messages
            ],
            "created_at": self.created_at,
            "last_active": self.last_active,
            "topics": self.topics,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Redis에서 읽어온 데이터로 복원"""
        session = cls(
            session_id=data["session_id"],
            created_at=data.get("created_at", time.time()),
            last_active=data.get("last_active", time.time()),
            topics=data.get("topics", []),
        )
        session.messages = [
            Message(role=m["role"], content=m["content"], timestamp=m.get("timestamp", 0.0))
            for m in data.get("messages", [])
        ]
        return session


class _PersistentSession(Session):
    """Redis가 있을 때 add_message 시 자동 저장하는 Session 서브클래스.

    공개 API는 Session과 동일 — 호출 코드 변경 불필요.
    """

    def __init__(self, *args, redis_client=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._redis = redis_client

    def add_message(self, role: str, content: str):
        super().add_message(role, content)
        self._sync_to_redis()

    def _sync_to_redis(self):
        if not self._redis:
            return
        try:
            key = f"{_REDIS_KEY_PREFIX}{self.session_id}"
            payload = json.dumps(self.to_dict(), ensure_ascii=False).encode("utf-8")
            self._redis.set(key, payload, ex=SESSION_TTL_SECONDS)
        except Exception:
            pass  # Redis 장애 시 무시 — 인메모리 세션은 정상 유지


class SessionManager:
    """세션 관리자 - 생성, 조회, 만료 정리.

    set_redis(client)로 Redis를 연결하면 세션을 영속화한다.
    Redis 없이도 기존과 동일하게 인메모리 dict로 동작한다.
    """

    def __init__(self):
        self._sessions: dict[str, Session] = {}
        self._redis = None

    def set_redis(self, redis_client) -> None:
        """Redis 클라이언트 주입 + 기존 세션 복원"""
        self._redis = redis_client
        self._load_from_redis()

    def _load_from_redis(self):
        """Redis에 저장된 세션을 인메모리 dict로 복원"""
        if not self._redis:
            return
        try:
            pattern = f"{_REDIS_KEY_PREFIX}*"
            keys = self._redis.keys(pattern)
            loaded = 0
            for key in keys:
                raw = self._redis.get(key)
                if not raw:
                    continue
                data = json.loads(raw.decode("utf-8"))
                session = _PersistentSession.from_dict(data) if self._redis else Session.from_dict(data)
                if isinstance(session, Session) and self._redis:
                    # from_dict가 기본 Session을 반환하므로 _PersistentSession으로 래핑
                    ps = _PersistentSession(
                        session_id=session.session_id,
                        redis_client=self._redis,
                    )
                    ps.messages = session.messages
                    ps.created_at = session.created_at
                    ps.last_active = session.last_active
                    ps.topics = session.topics
                    session = ps
                if not session.is_expired():
                    self._sessions[session.session_id] = session
                    loaded += 1
            if loaded:
                import logging
                logging.getLogger(__name__).info("Redis에서 세션 %d개 복원", loaded)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning("Redis 세션 복원 실패: %s", e)

    def _make_session(self, session_id: str) -> Session:
        """Redis 여부에 따라 적절한 Session 객체 생성"""
        if self._redis:
            return _PersistentSession(session_id=session_id, redis_client=self._redis)
        return Session(session_id=session_id)

    def create_session(self) -> Session:
        session_id = str(uuid.uuid4())[:8]
        session = self._make_session(session_id)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        session = self._sessions.get(session_id)
        if session:
            if session.is_expired():
                del self._sessions[session_id]
                self._delete_from_redis(session_id)
                return None
            return session

        # 인메모리에 없으면 Redis에서 복원 시도 (재시작 후 세션 유지)
        if self._redis:
            session = self._restore_from_redis(session_id)
            if session:
                self._sessions[session_id] = session
        return session

    def _restore_from_redis(self, session_id: str) -> Optional[Session]:
        try:
            key = f"{_REDIS_KEY_PREFIX}{session_id}"
            raw = self._redis.get(key)
            if not raw:
                return None
            data = json.loads(raw.decode("utf-8"))
            ps = _PersistentSession(session_id=session_id, redis_client=self._redis)
            base = Session.from_dict(data)
            ps.messages = base.messages
            ps.created_at = base.created_at
            ps.last_active = base.last_active
            ps.topics = base.topics
            return None if ps.is_expired() else ps
        except Exception:
            return None

    def _delete_from_redis(self, session_id: str):
        if not self._redis:
            return
        try:
            self._redis.delete(f"{_REDIS_KEY_PREFIX}{session_id}")
        except Exception:
            pass

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
            self._delete_from_redis(sid)

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

    REWRITE_PROMPT = """대화 이력을 보고 최신 질문의 대명사를 구체적 단어로 바꿔라.

예시:
- 이력: "OCP에서 Pod 생성 방법" → 최신: "그거 삭제하려면?" → 출력: "OCP에서 Pod를 삭제하려면?"
- 이력: "Deployment 설명" → 최신: "더 자세히" → 출력: "Deployment에 대해 더 자세히 설명해줘"
- 이력: "PVC 생성" → 최신: "그거 모니터링 어떻게 해?" → 출력: "PVC 모니터링 어떻게 해?"

규칙:
- 대명사(그거, 이거, 그것)를 이력의 구체적 대상으로 교체
- 최신 질문의 동사(삭제, 수정, 조회 등)는 절대 바꾸지 마라
- 재작성된 질문만 출력 (설명 없이)

대화 이력:
{history}

최신 질문: {query}

출력:"""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    _DIRECT_OVERVIEW_PATTERNS = (
        (r"^(오픈시프트|openshift|ocp)(?:이란|란|은|는|이|가)?(?:뭐야|뭐임|무엇(?:이야|인가)?|설명해줘|설명해봐)?$", "오픈시프트 개요 설명해봐"),
        (r"^(쿠버네티스|kubernetes|k8s)(?:이란|란|은|는|이|가)?(?:뭐야|뭐임|무엇(?:이야|인가)?|설명해줘|설명해봐)?$", "쿠버네티스 개요 설명해봐"),
    )

    def _normalize_direct_query(self, query: str) -> str:
        compact = re.sub(r"[\s?!.,]+", "", query.lower())
        for pattern, normalized in self._DIRECT_OVERVIEW_PATTERNS:
            if re.fullmatch(pattern, compact):
                return normalized
        return query

    async def rewrite(self, query: str, session: Session) -> str:
        """맥락 기반 쿼리 재작성"""
        normalized_query = self._normalize_direct_query(query)
        if normalized_query != query:
            return normalized_query

        # 대화 이력이 없으면 원본 반환
        if len(session.messages) < 2:
            return query

        # 맥락 의존적 키워드 체크 — 전부 LLM 태우면 느리니까 간단한 필터로 거름
        # 향후 개선: "왜", "어떻게"는 독립 질문에서도 등장하여 오탐 가능성 있음 (현재까지 문제 없음)
        context_dependent_patterns = [
            "그것", "그건", "이것", "이건", "거기", "여기",
            "그거", "이거", "위에", "아까", "그러면",
            "더 알려", "자세히", "예시", "다른",
            "왜", "어떻게",  # 단독 사용 시
        ]
        needs_rewrite = any(p in query for p in context_dependent_patterns)

        # 짧은 질문도 맥락 의존 가능성 높음 (5자였는데 "더 알려줘"(6자) 못 잡아서 8로 올림)
        if len(query.strip()) < 8:
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
