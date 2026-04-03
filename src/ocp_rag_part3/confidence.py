from __future__ import annotations

import re

from ocp_rag_part2.models import RetrievalHit

from .models import Citation, ConfidenceResult


TOKEN_RE = re.compile(r"[A-Za-z0-9가-힣][A-Za-z0-9가-힣._/-]*")
STOPWORDS = {
    "the",
    "and",
    "for",
    "from",
    "with",
    "what",
    "how",
    "where",
    "when",
    "which",
    "this",
    "that",
    "open",
    "shift",
    "openshift",
    "ocp",
    "설명해줘",
    "알려줘",
    "어떻게",
    "어디서",
    "무엇",
    "뭐야",
    "뭔가요",
    "가이드",
    "문서",
}


def _clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _average(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _normalize_retrieval_score(score: float) -> float:
    # Our fused scores usually land around 0.015~0.025. Keep this conservative.
    return _clip((score - 0.014) / 0.008)


def _extract_keywords(query: str) -> list[str]:
    keywords: list[str] = []
    seen: set[str] = set()
    for match in TOKEN_RE.findall(query or ""):
        token = match.lower().strip()
        if len(token) < 2 or token in STOPWORDS:
            continue
        if token in seen:
            continue
        seen.add(token)
        keywords.append(token)
    return keywords


def calculate_confidence(
    query: str,
    hits: list[RetrievalHit],
    citations: list[Citation],
    warnings: list[str] | None = None,
) -> ConfidenceResult:
    warnings = list(warnings or [])
    if not hits:
        return ConfidenceResult(
            score=0.0,
            level="none",
            reason="관련 문서를 찾지 못했습니다.",
            degraded=True,
        )

    top_hits = hits[:5]
    keywords = _extract_keywords(query)
    top_scores = [_normalize_retrieval_score(hit.fused_score or hit.raw_score) for hit in top_hits]
    avg_retrieval = _average(top_scores[:3] or top_scores)

    citation_factor = _clip(len(citations) / 3.0)
    dominant_book = top_hits[0].book_slug
    dominant_count = sum(1 for hit in top_hits[:3] if hit.book_slug == dominant_book)
    book_agreement = 1.0 if dominant_count >= 2 else 0.45

    haystack = " ".join(hit.text.lower() for hit in top_hits)
    if keywords:
        coverage = sum(1 for keyword in keywords if keyword in haystack) / len(keywords)
    else:
        coverage = 0.0

    score = (
        avg_retrieval * 0.42
        + citation_factor * 0.20
        + book_agreement * 0.20
        + coverage * 0.18
    )

    warning_penalty = 0.0
    if warnings:
        warning_penalty += 0.08
    if len(citations) == 0:
        warning_penalty += 0.20
    if len({hit.book_slug for hit in top_hits[:3]}) >= 3:
        warning_penalty += 0.10
    score = _clip(score - warning_penalty)

    if score >= 0.74:
        return ConfidenceResult(
            score=score,
            level="high",
            reason="여러 근거가 같은 주제를 지지합니다.",
            degraded=False,
        )
    if score >= 0.52:
        return ConfidenceResult(
            score=score,
            level="medium",
            reason="답변은 가능하지만, 세부 절차는 출처를 함께 확인하는 편이 안전합니다.",
            degraded=False,
        )
    if score >= 0.28:
        return ConfidenceResult(
            score=score,
            level="low",
            reason="근거가 약하거나 문서가 갈립니다. 질문을 더 구체화하는 편이 안전합니다.",
            degraded=True,
        )
    return ConfidenceResult(
        score=score,
        level="none",
        reason="현재 근거로는 단정하기 어렵습니다. 질문 범위를 좁혀 다시 묻는 편이 좋습니다.",
        degraded=True,
    )
