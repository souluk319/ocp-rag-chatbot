# 세션 기록, 최근 대화 snapshot, 디버그용 turn 모델을 관리한다.
from __future__ import annotations

import threading
from dataclasses import dataclass, field

from play_book_studio.config.packs import default_core_pack
from play_book_studio.retrieval.models import SessionContext

RUNTIME_CHAT_MODE = "chat"
DEFAULT_CORE_VERSION = default_core_pack().version


@dataclass(slots=True)
class Turn:
    query: str
    mode: str
    answer: str
    rewritten_query: str = ""
    response_kind: str = ""
    warnings: list[str] = field(default_factory=list)
    stages: list[dict[str, object]] = field(default_factory=list)
    diagnosis: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class ChatSession:
    session_id: str
    mode: str = RUNTIME_CHAT_MODE
    context: SessionContext = field(
        default_factory=lambda: SessionContext(mode=RUNTIME_CHAT_MODE, ocp_version=DEFAULT_CORE_VERSION)
    )
    history: list[Turn] = field(default_factory=list)

    @property
    def last_query(self) -> str:
        if not self.history:
            return ""
        return self.history[-1].query


class SessionStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: dict[str, ChatSession] = {}
        self._latest_session_id: str | None = None

    def get(self, session_id: str) -> ChatSession:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                session = ChatSession(session_id=session_id)
                self._sessions[session_id] = session
            self._latest_session_id = session_id
            return session

    def reset(self, session_id: str) -> ChatSession:
        with self._lock:
            session = ChatSession(session_id=session_id)
            self._sessions[session_id] = session
            self._latest_session_id = session_id
            return session

    def update(self, session: ChatSession) -> None:
        with self._lock:
            self._sessions[session.session_id] = session
            self._latest_session_id = session.session_id

    def peek(self, session_id: str) -> ChatSession | None:
        with self._lock:
            return self._sessions.get(session_id)

    def latest(self) -> ChatSession | None:
        with self._lock:
            if not self._latest_session_id:
                return None
            return self._sessions.get(self._latest_session_id)

