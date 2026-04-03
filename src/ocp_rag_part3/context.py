from __future__ import annotations

import re
from collections import Counter, defaultdict

from ocp_rag_part2.models import RetrievalHit
from ocp_rag_part2.query import (
    has_architecture_explainer_intent,
    has_backup_restore_intent,
    has_cluster_node_usage_intent,
    has_kubernetes_compare_follow_up_intent,
    has_mco_concept_intent,
    has_node_drain_intent,
    has_openshift_kubernetes_compare_intent,
    has_operator_concept_intent,
    has_project_finalizer_intent,
    has_project_terminating_intent,
    has_rbac_intent,
    is_generic_intro_query,
)

from .models import Citation, ContextBundle


SPACE_RE = re.compile(r"\s+")
SECTION_PREFIX_RE = re.compile(r"^\d+(?:\.\d+)*\.?\s*")


def _normalize_excerpt(text: str) -> str:
    return SPACE_RE.sub(" ", (text or "").strip())


def _section_core(section: str) -> str:
    normalized = SPACE_RE.sub(" ", (section or "").strip()).lower()
    return SECTION_PREFIX_RE.sub("", normalized)


def _anchor_root(anchor: str) -> str:
    normalized = (anchor or "").strip().lower()
    if not normalized:
        return ""
    return normalized.split("_", 1)[0]


def _hit_score(hit: RetrievalHit) -> float:
    if hit.fused_score > 0:
        return float(hit.fused_score)
    return float(hit.raw_score)


def _hit_identity(hit: RetrievalHit) -> tuple[str, str, str]:
    return (
        hit.book_slug,
        _section_core(hit.section),
        _anchor_root(hit.anchor),
    )


def _hit_text_quality(hit: RetrievalHit) -> tuple[int, float]:
    excerpt = _normalize_excerpt(hit.text)
    quality = len(excerpt)
    if "/TABLE]" in excerpt or "[/TABLE]" in excerpt:
        quality -= 240
    if excerpt.endswith("Expand"):
        quality -= 40
    return quality, _hit_score(hit)


def _collapse_duplicate_identity_hits(hits: list[RetrievalHit]) -> list[RetrievalHit]:
    first_positions: dict[tuple[str, str, str], int] = {}
    best_hits: dict[tuple[str, str, str], RetrievalHit] = {}

    for index, hit in enumerate(hits):
        identity = _hit_identity(hit)
        first_positions.setdefault(identity, index)
        incumbent = best_hits.get(identity)
        if incumbent is None or _hit_text_quality(hit) > _hit_text_quality(incumbent):
            best_hits[identity] = hit

    ordered_identities = sorted(first_positions, key=first_positions.__getitem__)
    return [best_hits[identity] for identity in ordered_identities]


def _unique_top_hits(hits: list[RetrievalHit], *, limit: int) -> list[RetrievalHit]:
    unique: list[RetrievalHit] = []
    seen: set[tuple[str, str, str]] = set()
    for hit in hits:
        identity = _hit_identity(hit)
        if identity in seen:
            continue
        seen.add(identity)
        unique.append(hit)
        if len(unique) >= limit:
            break
    return unique


def _should_force_clarification(
    hits: list[RetrievalHit],
    *,
    query: str = "",
) -> bool:
    normalized = query or ""
    if any(
        [
            has_openshift_kubernetes_compare_intent(normalized),
            has_kubernetes_compare_follow_up_intent(normalized),
            is_generic_intro_query(normalized),
            has_architecture_explainer_intent(normalized),
            has_operator_concept_intent(normalized),
            has_mco_concept_intent(normalized),
            has_rbac_intent(normalized),
            has_backup_restore_intent(normalized),
            has_project_terminating_intent(normalized),
            has_project_finalizer_intent(normalized),
            has_node_drain_intent(normalized),
            has_cluster_node_usage_intent(normalized),
        ]
    ):
        return False

    top_hits = _unique_top_hits(hits, limit=4)
    if len(top_hits) < 2:
        return False

    top_score = _hit_score(top_hits[0])
    second_score = _hit_score(top_hits[1])
    top_books = {hit.book_slug for hit in top_hits}
    top_book = top_hits[0].book_slug
    top_book_count = sum(int(hit.book_slug == top_book) for hit in hits[:4])
    close_competitor = second_score >= top_score * 0.94 if top_score > 0 else False
    weak_support = top_book_count == 1 or (top_book_count == 2 and len(top_books) >= 3)

    # Use a very conservative absolute floor only when support is weak.
    low_top_score = top_score < 0.018
    low_margin = (top_score - second_score) < 0.0025 if top_score > 0 else True

    return (weak_support and close_competitor) or (
        low_top_score and (weak_support or low_margin)
    )


def _select_hits(
    hits: list[RetrievalHit],
    *,
    query: str = "",
    max_chunks: int,
) -> list[RetrievalHit]:
    if not hits:
        return []

    ranked_hits = list(hits)
    if _should_force_clarification(ranked_hits, query=query):
        return []

    normalized = query or ""
    is_concept_query = any(
        [
            has_openshift_kubernetes_compare_intent(normalized),
            has_kubernetes_compare_follow_up_intent(normalized),
            is_generic_intro_query(normalized),
            has_architecture_explainer_intent(normalized),
            has_operator_concept_intent(normalized),
            has_mco_concept_intent(normalized),
        ]
    )
    is_procedure_query = any(
        [
            has_backup_restore_intent(normalized),
            has_rbac_intent(normalized),
            has_project_terminating_intent(normalized),
            has_project_finalizer_intent(normalized),
            has_node_drain_intent(normalized),
            has_cluster_node_usage_intent(normalized),
        ]
    )
    if is_concept_query and not is_procedure_query:
        ranked_hits = _collapse_duplicate_identity_hits(ranked_hits)

    max_chunks = min(max_chunks, 5 if is_procedure_query else 4)
    support_window = ranked_hits[: max(max_chunks * 2, 6)]
    top_score = _hit_score(support_window[0])
    top_book = support_window[0].book_slug

    if has_operator_concept_intent(normalized):
        preferred_books = {"overview", "extensions", "operators", "architecture"}
        ranked_hits = sorted(
            ranked_hits,
            key=lambda hit: (
                0 if hit.book_slug in preferred_books else 1,
                -_hit_score(hit),
                hit.book_slug,
                hit.chunk_id,
            ),
        )
        support_window = ranked_hits[: max(max_chunks * 2, 6)]
        top_score = _hit_score(support_window[0])
        top_book = support_window[0].book_slug
    elif has_mco_concept_intent(normalized):
        preferred_books = {"machine_configuration", "operators", "architecture", "extensions"}
        ranked_hits = sorted(
            ranked_hits,
            key=lambda hit: (
                0 if hit.book_slug in preferred_books else 1,
                -_hit_score(hit),
                hit.book_slug,
                hit.chunk_id,
            ),
        )
        support_window = ranked_hits[: max(max_chunks * 2, 6)]
        top_score = _hit_score(support_window[0])
        top_book = support_window[0].book_slug

    book_counts = Counter(hit.book_slug for hit in support_window)
    best_book_scores: dict[str, float] = defaultdict(float)
    for hit in support_window:
        best_book_scores[hit.book_slug] = max(
            best_book_scores[hit.book_slug],
            _hit_score(hit),
        )

    allowed_books = {top_book}
    if has_operator_concept_intent(normalized):
        for book_slug in ("overview", "extensions", "operators", "architecture"):
            if best_book_scores.get(book_slug, 0.0) >= top_score * 0.62:
                allowed_books.add(book_slug)
    if has_mco_concept_intent(normalized):
        for book_slug in ("machine_configuration", "operators", "architecture", "extensions"):
            if best_book_scores.get(book_slug, 0.0) >= top_score * 0.62:
                allowed_books.add(book_slug)
    for book_slug, count in book_counts.items():
        if book_slug == top_book:
            continue
        threshold = 0.92
        if is_concept_query:
            threshold = 0.72
        elif is_procedure_query:
            threshold = 0.84
        if count >= 2 and best_book_scores[book_slug] >= top_score * threshold:
            allowed_books.add(book_slug)

    if top_score > 0:
        score_cutoff = top_score * (0.68 if is_concept_query else 0.74 if is_procedure_query else 0.82)
    else:
        score_cutoff = 0.0
    selected: list[RetrievalHit] = []
    per_book_counts: Counter[str] = Counter()
    per_book_limit = 3 if is_procedure_query else 2

    for hit in ranked_hits:
        if len(selected) >= max_chunks:
            break
        if hit.book_slug not in allowed_books:
            continue
        if _hit_score(hit) < score_cutoff:
            continue
        if per_book_counts[hit.book_slug] >= per_book_limit:
            continue
        selected.append(hit)
        per_book_counts[hit.book_slug] += 1

    return selected[:max_chunks]


def assemble_context(
    hits: list[RetrievalHit],
    *,
    query: str = "",
    max_chunks: int = 6,
    max_chars_per_chunk: int = 900,
) -> ContextBundle:
    citations: list[Citation] = []
    seen_chunk_ids: set[str] = set()
    seen_signatures: set[tuple[str, str, str]] = set()
    seen_mirror_sections: dict[tuple[str, str], str] = {}

    for hit in _select_hits(hits, query=query, max_chunks=max_chunks):
        if hit.chunk_id in seen_chunk_ids:
            continue
        excerpt = _normalize_excerpt(hit.text)
        section_core = _section_core(hit.section)
        anchor_root = _anchor_root(hit.anchor)
        mirror_signature = (section_core, anchor_root)
        prior_book = seen_mirror_sections.get(mirror_signature)
        if (
            prior_book is not None
            and prior_book != hit.book_slug
            and section_core
            and anchor_root
        ):
            continue
        signature = (
            hit.book_slug,
            hit.section.strip(),
            excerpt[:240],
        )
        if signature in seen_signatures:
            continue
        seen_chunk_ids.add(hit.chunk_id)
        seen_signatures.add(signature)
        if section_core and anchor_root:
            seen_mirror_sections.setdefault(mirror_signature, hit.book_slug)
        citations.append(
            Citation(
                index=len(citations) + 1,
                chunk_id=hit.chunk_id,
                book_slug=hit.book_slug,
                section=hit.section,
                anchor=hit.anchor,
                source_url=hit.source_url,
                viewer_path=hit.viewer_path,
                excerpt=excerpt[:max_chars_per_chunk].strip(),
            )
        )

    prompt_lines: list[str] = []
    for citation in citations:
        prompt_lines.append(
            f"[{citation.index}] book={citation.book_slug} | section={citation.section} | viewer={citation.viewer_path}"
        )
        prompt_lines.append(citation.excerpt)
        prompt_lines.append("")

    return ContextBundle(
        prompt_context="\n".join(prompt_lines).strip(),
        citations=citations,
    )
