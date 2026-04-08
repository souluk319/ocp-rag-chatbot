"""질문 이해와 rewrite 정책의 공개 허브.

실제 구현은 intents/rewrite/ambiguity/decompose로 분리하고,
바깥 import 경로는 이 파일에서 계속 유지한다.
"""

from __future__ import annotations

from .corpus_scope import detect_out_of_corpus_version, detect_unsupported_product
from .followups import has_corrective_follow_up, has_follow_up_reference
from .intents import *  # noqa: F403
from .text_utils import contains_hangul
from .rewrite import (
    has_explicit_topic_signal,
    needs_rewrite,
    normalize_query,
    query_book_adjustments,
    rewrite_query,
)

# ambiguity / subquery 분해는 별도 모듈 구현을 그대로 재노출한다.
from .ambiguity import (
    has_follow_up_entity_ambiguity,
    has_logging_ambiguity,
    has_multiple_entity_ambiguity,
    has_security_doc_locator_ambiguity,
    has_update_doc_locator_ambiguity,
)
from .decompose import decompose_retrieval_queries
