from __future__ import annotations

import re
from collections import Counter, defaultdict

from ocp_rag_part2.models import RetrievalHit

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


def _should_force_clarification(hits: list[RetrievalHit]) -> bool:
    top_hits = hits[:4]
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
    max_chunks: int,
) -> list[RetrievalHit]:
    if not hits:
        return []

    ranked_hits = list(hits)
    if _should_force_clarification(ranked_hits):
        return []

    max_chunks = min(max_chunks, 4)
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
    for book_slug, count in book_counts.items():
        if book_slug == top_book:
            continue
        if count >= 2 and best_book_scores[book_slug] >= top_score * 0.92:
            allowed_books.add(book_slug)

    score_cutoff = top_score * 0.82 if top_score > 0 else 0.0
    selected: list[RetrievalHit] = []
    per_book_counts: Counter[str] = Counter()

    for hit in ranked_hits:
        if len(selected) >= max_chunks:
            break
        if hit.book_slug not in allowed_books:
            continue
        if _hit_score(hit) < score_cutoff:
            continue
        if per_book_counts[hit.book_slug] >= 2:
            continue
        selected.append(hit)
        per_book_counts[hit.book_slug] += 1

    return selected[:max_chunks]


def assemble_context(
    hits: list[RetrievalHit],
    *,
    max_chunks: int = 6,
    max_chars_per_chunk: int = 900,
) -> ContextBundle:
    citations: list[Citation] = []
    seen_chunk_ids: set[str] = set()
    seen_signatures: set[tuple[str, str, str]] = set()
    seen_mirror_sections: dict[tuple[str, str], str] = {}

    for hit in _select_hits(hits, max_chunks=max_chunks):
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
