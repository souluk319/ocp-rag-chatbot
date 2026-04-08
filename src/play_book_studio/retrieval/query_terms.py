from __future__ import annotations

# 질문 본문에 retrieval 보조 용어를 주입하는 façade다.
# 실제 규칙은 공통 개념/운영형/etcd 특수 규칙으로 나눠 관리한다.

from .text_utils import append_terms as _append_terms, collapse_spaces as _collapse_spaces
from .query_terms_core import append_core_query_terms
from .query_terms_etcd import append_etcd_query_terms
from .query_terms_operations import append_operation_query_terms


def normalize_query(query: str) -> str:
    normalized = _collapse_spaces(query)
    if not normalized:
        return normalized

    terms: list[str] = []
    append_core_query_terms(normalized, terms)
    append_operation_query_terms(normalized, terms)
    append_etcd_query_terms(normalized, terms)

    return _append_terms(normalized, terms)
