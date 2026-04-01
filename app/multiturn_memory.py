from __future__ import annotations

import os
import re
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any


VERSION_RE = re.compile(r"(?<!\d)(4\.\d{1,2})(?!\d)")

FOLLOW_UP_CUES = (
    "그 전에",
    "그럼",
    "그러면",
    "거기서",
    "같은 흐름",
    "이어",
    "이전",
    "추가로",
    "또",
    "도 해야",
    "도 봐야",
)

TOPIC_SHIFT_CUES = (
    "아니",
    "주제 바꿀게",
    "다른 질문",
    "질문 바꿀게",
    "이건 다른",
)

TOPIC_RULES = (
    {
        "topic_id": "definition",
        "source_dir": "architecture",
        "patterns": (
            "ocp가 뭐야",
            "openshift가 뭐야",
            "오픈시프트가 뭐야",
            "what is ocp",
            "what is openshift",
        ),
        "hints": (
            "openshift container platform",
            "architecture overview",
            "introduction",
            "platform capabilities",
            "use cases",
        ),
    },
    {
        "topic_id": "install_firewall",
        "source_dir": "installing",
        "patterns": ("방화벽", "포트", "도메인", "allowlist", "firewall"),
        "hints": ("configuring firewall", "allowlist", "port", "domain"),
    },
    {
        "topic_id": "install_customizing",
        "source_dir": "installing",
        "patterns": ("커스터마이징", "커스텀", "customizing", "customization"),
        "hints": ("install customizing", "node customization", "day 1 customization"),
    },
    {
        "topic_id": "disconnected_mirroring",
        "source_dir": "disconnected",
        "patterns": ("폐쇄망", "disconnected", "oc-mirror", "미러", "mirror registry"),
        "hints": ("disconnected mirroring", "oc-mirror", "mirror registry"),
    },
    {
        "topic_id": "node_health",
        "source_dir": "support",
        "patterns": ("노드 상태", "node health", "kubelet", "notready"),
        "hints": ("verifying node health", "node health", "kubelet"),
    },
    {
        "topic_id": "network_troubleshooting",
        "source_dir": "support",
        "patterns": ("네트워크", "network issue", "network"),
        "hints": ("troubleshooting network issues", "network troubleshooting"),
    },
    {
        "topic_id": "operator_troubleshooting",
        "source_dir": "support",
        "patterns": ("operator", "오퍼레이터"),
        "hints": ("troubleshooting operator issues", "operator"),
    },
    {
        "topic_id": "update_prereq",
        "source_dir": "post_installation_configuration",
        "patterns": ("업데이트", "update", "업그레이드", "etcd", "CNF", "pod 준비"),
        "hints": (
            "OpenShift update",
            "before the update",
            "CNF",
            "etcd backup",
            "application pods",
        ),
    },
    {
        "topic_id": "certificate_maintenance",
        "source_dir": "post_installation_configuration",
        "patterns": ("인증서", "certificate"),
        "hints": ("certificate maintenance", "certificate troubleshooting"),
    },
)


@dataclass
class SessionTurn:
    turn_index: int
    question_ko: str
    classification: str
    rewritten_query: str
    active_topic: str
    source_dir: str
    active_version: str
    reference_doc_path: str
    issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "turn_index": self.turn_index,
            "question_ko": self.question_ko,
            "classification": self.classification,
            "rewritten_query": self.rewritten_query,
            "active_topic": self.active_topic,
            "source_dir": self.source_dir,
            "active_version": self.active_version,
            "reference_doc_path": self.reference_doc_path,
            "issues": list(self.issues),
        }


@dataclass
class SessionSnapshot:
    session_id: str
    active_topic: str = ""
    source_dir: str = ""
    active_category: str = ""
    active_version: str = ""
    reference_doc_path: str = ""
    retrieval_hints: list[str] = field(default_factory=list)
    turn_count: int = 0
    last_updated_epoch: float = 0.0
    recent_turns: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "active_topic": self.active_topic,
            "source_dir": self.source_dir,
            "active_category": self.active_category,
            "active_version": self.active_version,
            "reference_doc_path": self.reference_doc_path,
            "retrieval_hints": list(self.retrieval_hints),
            "turn_count": self.turn_count,
            "last_updated_epoch": self.last_updated_epoch,
            "recent_turns": list(self.recent_turns),
        }


class SessionMemoryManager:
    def __init__(
        self,
        *,
        max_history_turns: int | None = None,
        session_ttl_seconds: int | None = None,
        default_version: str | None = None,
    ) -> None:
        self.max_history_turns = max_history_turns or int(
            os.getenv("MAX_HISTORY_TURNS", "5")
        )
        self.session_ttl_seconds = session_ttl_seconds or int(
            os.getenv("SESSION_TTL_SECONDS", "3600")
        )
        self.default_version = default_version or os.getenv("DEFAULT_VERSION", "4.x")
        self._sessions: dict[str, SessionSnapshot] = {}

    def get_snapshot(self, session_id: str) -> SessionSnapshot:
        snapshot = self._sessions.get(session_id)
        if snapshot is None:
            snapshot = SessionSnapshot(
                session_id=session_id, active_version=self.default_version
            )
            self._sessions[session_id] = snapshot
            return snapshot

        if (
            snapshot.last_updated_epoch
            and (time.time() - snapshot.last_updated_epoch) > self.session_ttl_seconds
        ):
            snapshot = SessionSnapshot(
                session_id=session_id, active_version=self.default_version
            )
            self._sessions[session_id] = snapshot
        return snapshot

    def process_turn(
        self,
        *,
        session_id: str,
        turn_index: int,
        question_ko: str,
        reference_doc_path: str = "",
        reference_source_dir: str = "",
    ) -> dict[str, Any]:
        snapshot = self.get_snapshot(session_id)
        state_before = snapshot.to_dict()
        classification = classify_turn(question_ko, snapshot)
        inferred_topic = infer_topic(question_ko)
        inferred_source_dir = infer_source_dir(question_ko, snapshot)
        explicit_version = extract_version(question_ko)
        issues: list[str] = []

        if (
            classification == "follow_up"
            and not snapshot.active_topic
            and not inferred_topic
        ):
            issues.append("follow_up_without_topic_anchor")

        if (
            explicit_version
            and snapshot.active_version
            and explicit_version != snapshot.active_version
        ):
            issues.append("version_switch")

        if (
            classification == "topic_shift"
            and inferred_topic
            and snapshot.active_topic
            and inferred_topic != snapshot.active_topic
        ):
            issues.append("topic_reset")

        active_topic = inferred_topic or snapshot.active_topic
        if classification == "topic_shift":
            source_dir = inferred_source_dir or ""
            active_version = explicit_version or self.default_version
            reference_doc_for_turn = ""
        else:
            source_dir = (
                inferred_source_dir or reference_source_dir or snapshot.source_dir
            )
            active_version = (
                explicit_version or snapshot.active_version or self.default_version
            )
            reference_doc_for_turn = reference_doc_path or snapshot.reference_doc_path
        hints = build_hints(
            classification=classification,
            topic_id=active_topic,
            existing_hints=snapshot.retrieval_hints,
            question_ko=question_ko,
        )
        rewritten_query = rewrite_query(
            question_ko=question_ko,
            classification=classification,
            active_topic=active_topic,
            source_dir=source_dir,
            active_version=active_version,
            retrieval_hints=hints,
            reference_doc_path=reference_doc_for_turn,
        )

        turn_record = SessionTurn(
            turn_index=turn_index,
            question_ko=question_ko,
            classification=classification,
            rewritten_query=rewritten_query,
            active_topic=active_topic,
            source_dir=source_dir,
            active_version=active_version,
            reference_doc_path=reference_doc_for_turn,
            issues=issues,
        )

        self._apply_turn(snapshot, turn_record, reference_doc_path)
        state_after = snapshot.to_dict()
        return {
            "state_before": state_before,
            "turn": turn_record.to_dict(),
            "state_after": state_after,
        }

    def _apply_turn(
        self,
        snapshot: SessionSnapshot,
        turn_record: SessionTurn,
        reference_doc_path: str,
    ) -> None:
        snapshot.active_topic = turn_record.active_topic
        snapshot.source_dir = turn_record.source_dir
        snapshot.active_version = turn_record.active_version
        snapshot.reference_doc_path = (
            reference_doc_path or turn_record.reference_doc_path
        )
        snapshot.retrieval_hints = extract_topic_hints(turn_record.active_topic)
        snapshot.turn_count += 1
        snapshot.last_updated_epoch = time.time()

        recent_turns = deque(snapshot.recent_turns, maxlen=self.max_history_turns)
        recent_turns.append(turn_record.to_dict())
        snapshot.recent_turns = list(recent_turns)

    def apply_grounding(
        self,
        session_id: str,
        *,
        reference_doc_path: str = "",
        source_dir: str = "",
        category: str = "",
        version: str = "",
    ) -> dict[str, Any]:
        snapshot = self.get_snapshot(session_id)
        if reference_doc_path:
            snapshot.reference_doc_path = reference_doc_path
        if source_dir:
            snapshot.source_dir = source_dir
        if category:
            snapshot.active_category = category
        if version:
            snapshot.active_version = version
        snapshot.last_updated_epoch = time.time()
        return snapshot.to_dict()


def extract_version(text: str) -> str:
    match = VERSION_RE.search(text)
    return match.group(0) if match else ""


def infer_topic(text: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in ("ocp", "openshift", "오픈시프트")) and any(
        cue in lowered
        for cue in (
            "뭐야",
            "무엇",
            "정의",
            "소개",
            "개요",
            "란",
            "what is",
            "overview",
            "introduction",
        )
    ):
        return "definition"
    for rule in TOPIC_RULES:
        if any(pattern.lower() in lowered for pattern in rule["patterns"]):
            return rule["topic_id"]
    return ""


def infer_source_dir(text: str, snapshot: SessionSnapshot) -> str:
    topic_id = infer_topic(text)
    if topic_id:
        for rule in TOPIC_RULES:
            if rule["topic_id"] == topic_id:
                return rule["source_dir"]
    return snapshot.source_dir


def extract_topic_hints(topic_id: str) -> list[str]:
    if not topic_id:
        return []
    for rule in TOPIC_RULES:
        if rule["topic_id"] == topic_id:
            return list(rule["hints"])
    return []


def build_hints(
    *,
    classification: str,
    topic_id: str,
    existing_hints: list[str],
    question_ko: str,
) -> list[str]:
    hints: list[str] = []
    if classification != "topic_shift":
        for hint in existing_hints:
            if hint not in hints:
                hints.append(hint)
    for hint in extract_topic_hints(topic_id):
        if hint not in hints:
            hints.append(hint)

    if "etcd" in question_ko.lower() and "etcd backup" not in hints:
        hints.append("etcd backup")
    if "pod" in question_ko.lower() and "application pods" not in hints:
        hints.append("application pods")
    if "4." in question_ko and "version specific guidance" not in hints:
        hints.append("version specific guidance")
    return hints


def classify_turn(question_ko: str, snapshot: SessionSnapshot) -> str:
    if snapshot.turn_count == 0:
        return "standalone"

    lowered = question_ko.lower()
    if any(cue in lowered for cue in TOPIC_SHIFT_CUES):
        return "topic_shift"

    explicit_topic = infer_topic(question_ko)
    if (
        explicit_topic
        and snapshot.active_topic
        and explicit_topic != snapshot.active_topic
    ):
        return "topic_shift"

    if any(cue in question_ko for cue in FOLLOW_UP_CUES):
        return "follow_up"

    if len(question_ko) <= 40 and snapshot.active_topic:
        return "follow_up"

    if explicit_topic and explicit_topic == snapshot.active_topic:
        return "follow_up"

    return "standalone"


def rewrite_query(
    *,
    question_ko: str,
    classification: str,
    active_topic: str,
    source_dir: str,
    active_version: str,
    retrieval_hints: list[str],
    reference_doc_path: str,
) -> str:
    parts = [question_ko.strip()]
    if source_dir:
        parts.append(f"source {source_dir}")
    if active_topic:
        parts.append(f"topic {active_topic}")
    if active_version:
        parts.append(f"OpenShift {active_version}")
    if classification == "follow_up" and reference_doc_path:
        parts.append(f"last_document {reference_doc_path}")
    if retrieval_hints:
        parts.append("hints " + ", ".join(retrieval_hints))
    return " ; ".join(part for part in parts if part)
