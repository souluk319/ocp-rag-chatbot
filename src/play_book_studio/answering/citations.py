# citation 번호 보정, dedupe, fallback 선택을 담당하는 helper 모듈이다.

from __future__ import annotations

import re
from dataclasses import replace


CITATION_RE = re.compile(r"\[(\d+)\]")
ADJACENT_DUPLICATE_CITATION_RE = re.compile(r"(\[\d+\])(?:\s*\1)+")


def citation_identity(citation) -> tuple[str, str]:
    viewer_path = (citation.viewer_path or "").strip().lower()
    if viewer_path:
        return citation.book_slug, viewer_path
    source_url = (citation.source_url or "").strip().lower()
    anchor = (citation.anchor or "").strip().lower()
    return citation.book_slug, f"{source_url}#{anchor}"


def finalize_citations(
    answer_text: str,
    citations,
) -> tuple[str, list, list[int]]:
    referenced_indices: list[int] = []
    for match in CITATION_RE.finditer(answer_text):
        index = int(match.group(1))
        if 1 <= index <= len(citations):
            referenced_indices.append(index)

    if not referenced_indices:
        return answer_text, [], []

    canonical_index_by_source: dict[tuple[str, str], int] = {}
    remapped_index_by_original: dict[int, int] = {}
    final_citations = []

    for original_index in referenced_indices:
        if original_index in remapped_index_by_original:
            continue
        citation = citations[original_index - 1]
        identity = citation_identity(citation)
        canonical_index = canonical_index_by_source.get(identity)
        if canonical_index is None:
            canonical_index = len(final_citations) + 1
            canonical_index_by_source[identity] = canonical_index
            final_citations.append(replace(citation, index=canonical_index))
        remapped_index_by_original[original_index] = canonical_index

    rewritten_answer = CITATION_RE.sub(
        lambda match: (
            f"[{remapped_index_by_original[int(match.group(1))]}]"
            if int(match.group(1)) in remapped_index_by_original
            else ""
        ),
        answer_text,
    )
    rewritten_answer = ADJACENT_DUPLICATE_CITATION_RE.sub(r"\1", rewritten_answer)
    rewritten_answer = re.sub(r"\s+([,.;:])", r"\1", rewritten_answer)
    rewritten_answer = re.sub(r"[ \t]{2,}", " ", rewritten_answer)
    rewritten_answer = re.sub(r"\n[ \t]+", "\n", rewritten_answer).strip()

    cited_indices: list[int] = []
    seen_indices: set[int] = set()
    for match in CITATION_RE.finditer(rewritten_answer):
        index = int(match.group(1))
        if 1 <= index <= len(final_citations) and index not in seen_indices:
            cited_indices.append(index)
            seen_indices.add(index)

    return rewritten_answer, final_citations, cited_indices


def inject_single_citation(answer_text: str, *, citation_index: int = 1) -> str:
    blocks = answer_text.split("\n\n")
    for index, block in enumerate(blocks):
        stripped = block.strip()
        if not stripped or stripped.startswith("```"):
            continue
        if CITATION_RE.search(stripped):
            return answer_text
        blocks[index] = f"{stripped} [{citation_index}]"
        return "\n\n".join(blocks).strip()
    return f"{answer_text.rstrip()} [{citation_index}]".strip()


def summarize_selected_citations(citations, retrieval_hits) -> list[dict[str, str | float | int]]:
    hit_by_chunk_id = {hit.chunk_id: hit for hit in retrieval_hits}
    summaries: list[dict[str, str | float | int]] = []
    for citation in citations:
        hit = hit_by_chunk_id.get(citation.chunk_id)
        summary: dict[str, str | float | int] = {
            "index": citation.index,
            "book_slug": citation.book_slug,
            "section": citation.section,
        }
        if hit is not None:
            summary["fused_score"] = round(float(hit.fused_score), 4)
            for key in ("bm25_score", "bm25_rank", "vector_score", "vector_rank"):
                if key in hit.component_scores:
                    summary[key] = round(float(hit.component_scores[key]), 4)
        summaries.append(summary)
    return summaries


def maybe_autorepair_inline_citations(
    answer_text: str,
    citations,
) -> tuple[str, bool]:
    if CITATION_RE.search(answer_text) or not citations:
        return answer_text, False

    unique_identities = {
        citation_identity(citation)
        for citation in citations
    }
    if len(unique_identities) != 1:
        return answer_text, False
    return inject_single_citation(answer_text, citation_index=1), True


def select_fallback_citations(
    citations,
    *,
    limit: int = 3,
) -> list:
    selected = []
    seen_identities: set[tuple[str, str]] = set()
    for citation in citations:
        identity = citation_identity(citation)
        if identity in seen_identities:
            continue
        seen_identities.add(identity)
        selected.append(replace(citation, index=len(selected) + 1))
        if len(selected) >= limit:
            break
    return selected
