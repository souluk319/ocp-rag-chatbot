from __future__ import annotations

# etcd처럼 질문 의도에 따라 설명/절차 용어가 크게 달라지는 특수 규칙을 따로 모은 helper다.

from .intents import *  # noqa: F403


def append_etcd_query_terms(normalized: str, terms: list[str]) -> None:
    if ETCD_RE.search(normalized):
        terms.append("etcd")
        if has_backup_restore_intent(normalized):
            terms.extend(["backup", "restore", "disaster", "recovery", "snapshot"])
        elif is_explainer_query(normalized) or "중요" in normalized or "역할" in normalized:
            terms.extend(["quorum", "control", "plane", "cluster", "state", "key-value", "store"])
