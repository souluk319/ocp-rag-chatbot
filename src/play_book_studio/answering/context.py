"""답변 단계에서 최종 context chunk와 citation을 고른다.

retriever는 많은 후보를 반환할 수 있고, 그중 무엇을 LLM에 보여도 안전한지,
언제 clarification이 더 안전한지를 이 파일이 결정한다.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict

from play_book_studio.retrieval.models import RetrievalHit
from play_book_studio.retrieval.query import (
    has_backup_restore_intent,
    has_cluster_node_usage_intent,
    has_crash_loop_troubleshooting_intent,
    has_deployment_scaling_intent,
    has_follow_up_reference,
    has_mco_concept_intent,
    has_node_drain_intent,
    has_openshift_kubernetes_compare_intent,
    has_operator_concept_intent,
    has_pod_lifecycle_concept_intent,
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
    if hit.source == "hybrid_reranked":
        pre_rerank_fused = hit.component_scores.get("pre_rerank_fused_score")
        if pre_rerank_fused is not None:
            return float(pre_rerank_fused)
    if hit.fused_score > 0:
        return float(hit.fused_score)
    return float(hit.raw_score)


def _crash_loop_priority(hit: RetrievalHit) -> int:
    lowered_section = (hit.section or "").lower()
    lowered_text = (hit.text or "").lower()
    if (
        "애플리케이션 오류 조사" in hit.section
        or "애플리케이션 진단 데이터 수집" in hit.section
        or "oc describe pod/" in lowered_text
        or "oc logs -f pod/" in lowered_text
        or "애플리케이션 pod와 관련된 이벤트" in hit.text
    ):
        return 0
    if (
        "이벤트 목록" in hit.section
        or ("이벤트" in hit.section and "backoff" in lowered_text)
        or "back-off restarting failed container" in lowered_text
    ):
        return 1
    if (
        "상태 점검 이해" in hit.section
        or "상태 점검 구성" in hit.section
        or "livenessprobe" in lowered_text
        or "readinessprobe" in lowered_text
    ):
        return 2
    if (
        "oom 종료 정책" in hit.section
        or "oomkilled" in lowered_text
        or "restartcount" in lowered_text
    ):
        return 3
    if (
        "operator 문제 해결" in hit.section
        or "카탈로그 소스 상태 보기" in hit.section
        or "실패한 서브스크립션 새로 고침" in hit.section
        or (
            ("imagepullbackoff" in lowered_text or "errimagepull" in lowered_text)
            and "crashloopbackoff" not in lowered_text
            and "애플리케이션" not in hit.text
        )
    ):
        return 9
    return 5


def _hit_identity(hit: RetrievalHit) -> tuple[str, str, str]:
    return (
        hit.book_slug,
        _section_core(hit.section),
        _anchor_root(hit.anchor),
    )


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
    if has_follow_up_reference(normalized):
        return False
    if any(
        [
            has_openshift_kubernetes_compare_intent(normalized),
            is_generic_intro_query(normalized),
            has_operator_concept_intent(normalized),
            has_mco_concept_intent(normalized),
            has_pod_lifecycle_concept_intent(normalized),
            has_rbac_intent(normalized),
            has_backup_restore_intent(normalized),
            has_crash_loop_troubleshooting_intent(normalized),
            has_project_terminating_intent(normalized),
            has_project_finalizer_intent(normalized),
            has_node_drain_intent(normalized),
            has_cluster_node_usage_intent(normalized),
            has_deployment_scaling_intent(normalized),
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
    # context 조립은 raw retrieval보다 의도적으로 더 보수적이다.
    # 근거가 약하면 노이즈 hit 하나에 과적합하기보다 clarification을 택한다.
    if not hits:
        return []

    ranked_hits = list(hits)
    if _should_force_clarification(ranked_hits, query=query):
        return []

    normalized = query or ""
    is_concept_query = any(
        [
            has_openshift_kubernetes_compare_intent(normalized),
            is_generic_intro_query(normalized),
            has_operator_concept_intent(normalized),
            has_mco_concept_intent(normalized),
            has_pod_lifecycle_concept_intent(normalized),
        ]
    )
    is_procedure_query = any(
        [
            has_backup_restore_intent(normalized),
            has_crash_loop_troubleshooting_intent(normalized),
            has_rbac_intent(normalized),
            has_project_terminating_intent(normalized),
            has_project_finalizer_intent(normalized),
            has_node_drain_intent(normalized),
            has_cluster_node_usage_intent(normalized),
            has_deployment_scaling_intent(normalized),
        ]
    )

    max_chunks = min(max_chunks, 5 if is_procedure_query else 4)
    support_window = ranked_hits[: max(max_chunks * 2, 6)]
    top_score = _hit_score(support_window[0])
    top_book = support_window[0].book_slug

    if has_operator_concept_intent(normalized):
        preferred_order = {
            "extensions": 0,
            "overview": 1,
            "architecture": 2,
            "operators": 3,
        }
        ranked_hits = sorted(
            ranked_hits,
            key=lambda hit: (
                preferred_order.get(hit.book_slug, 9),
                -_hit_score(hit),
                hit.book_slug,
                hit.chunk_id,
            ),
        )
        support_window = ranked_hits[: max(max_chunks * 2, 6)]
        top_score = _hit_score(support_window[0])
        top_book = support_window[0].book_slug
    elif has_pod_lifecycle_concept_intent(normalized):
        preferred_books = {"nodes", "overview", "architecture", "building_applications"}
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
    elif has_crash_loop_troubleshooting_intent(normalized):
        preferred_order = {
            "support": 0,
            "validation_and_troubleshooting": 1,
            "building_applications": 2,
            "nodes": 3,
        }
        ranked_hits = sorted(
            ranked_hits,
            key=lambda hit: (
                _crash_loop_priority(hit),
                preferred_order.get(hit.book_slug, 9),
                -_hit_score(hit),
                hit.book_slug,
                hit.chunk_id,
            ),
        )
        support_window = ranked_hits[: max(max_chunks * 2, 8)]
        top_score = _hit_score(support_window[0])
        top_book = support_window[0].book_slug
    elif has_mco_concept_intent(normalized):
        preferred_order = {
            "architecture": 0,
            "overview": 1,
            "machine_management": 2,
            "images": 3,
            "operators": 4,
            "machine_configuration": 5,
        }
        ranked_hits = sorted(
            ranked_hits,
            key=lambda hit: (
                preferred_order.get(hit.book_slug, 9),
                -_hit_score(hit),
                hit.book_slug,
                hit.chunk_id,
            ),
        )
        support_window = ranked_hits[: max(max_chunks * 2, 6)]
        top_score = _hit_score(support_window[0])
        top_book = support_window[0].book_slug
    elif has_rbac_intent(normalized):
        preferred_order = {
            "authentication_and_authorization": 0,
            "cli_tools": 1,
            "postinstallation_configuration": 2,
        }
        ranked_hits = sorted(
            ranked_hits,
            key=lambda hit: (
                preferred_order.get(hit.book_slug, 9),
                -_hit_score(hit),
                hit.book_slug,
                hit.chunk_id,
            ),
        )
        support_window = ranked_hits[: max(max_chunks * 2, 8)]
        top_score = _hit_score(support_window[0])
        top_book = support_window[0].book_slug
    elif has_project_terminating_intent(normalized):
        preferred_order = {
            "support": 0,
            "building_applications": 1,
            "project_apis": 2,
            "config_apis": 3,
        }
        ranked_hits = sorted(
            ranked_hits,
            key=lambda hit: (
                preferred_order.get(hit.book_slug, 9),
                -_hit_score(hit),
                hit.book_slug,
                hit.chunk_id,
            ),
        )
        support_window = ranked_hits[: max(max_chunks * 2, 8)]
        top_score = _hit_score(support_window[0])
        top_book = support_window[0].book_slug
    elif has_project_finalizer_intent(normalized):
        preferred_order = {
            "support": 0,
            "project_apis": 1,
            "config_apis": 2,
            "building_applications": 3,
        }
        ranked_hits = sorted(
            ranked_hits,
            key=lambda hit: (
                preferred_order.get(hit.book_slug, 9),
                -_hit_score(hit),
                hit.book_slug,
                hit.chunk_id,
            ),
        )
        support_window = ranked_hits[: max(max_chunks * 2, 8)]
        top_score = _hit_score(support_window[0])
        top_book = support_window[0].book_slug
    elif has_deployment_scaling_intent(normalized):
        preferred_order = {
            "cli_tools": 0,
            "building_applications": 1,
        }
        ranked_hits = sorted(
            ranked_hits,
            key=lambda hit: (
                preferred_order.get(hit.book_slug, 9),
                -_hit_score(hit),
                hit.book_slug,
                hit.chunk_id,
            ),
        )
        support_window = ranked_hits[: max(max_chunks * 2, 8)]
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
    if has_pod_lifecycle_concept_intent(normalized):
        for book_slug in ("nodes", "overview", "architecture", "building_applications"):
            if best_book_scores.get(book_slug, 0.0) >= top_score * 0.58:
                allowed_books.add(book_slug)
    if has_crash_loop_troubleshooting_intent(normalized):
        for book_slug in ("support", "validation_and_troubleshooting", "building_applications", "nodes"):
            if best_book_scores.get(book_slug, 0.0) >= top_score * 0.55:
                allowed_books.add(book_slug)
    if has_mco_concept_intent(normalized):
        for book_slug in ("architecture", "overview", "machine_management", "images"):
            if best_book_scores.get(book_slug, 0.0) >= top_score * 0.62:
                allowed_books.add(book_slug)
    if has_rbac_intent(normalized):
        for book_slug in ("authentication_and_authorization", "cli_tools", "postinstallation_configuration"):
            if best_book_scores.get(book_slug, 0.0) >= top_score * 0.58:
                allowed_books.add(book_slug)
    if has_project_terminating_intent(normalized):
        for book_slug in ("support", "building_applications", "project_apis", "config_apis"):
            if best_book_scores.get(book_slug, 0.0) >= top_score * 0.46:
                allowed_books.add(book_slug)
    if has_project_finalizer_intent(normalized):
        for book_slug in ("support", "project_apis", "config_apis", "building_applications"):
            if best_book_scores.get(book_slug, 0.0) >= top_score * 0.44:
                allowed_books.add(book_slug)
    if has_deployment_scaling_intent(normalized):
        for book_slug in ("cli_tools", "building_applications"):
            if best_book_scores.get(book_slug, 0.0) >= top_score * 0.52:
                allowed_books.add(book_slug)
    for book_slug, count in book_counts.items():
        if book_slug == top_book:
            continue
        threshold = 0.92
        if is_concept_query:
            threshold = 0.72
        elif is_procedure_query:
            threshold = 0.84
        if has_project_terminating_intent(normalized) or has_project_finalizer_intent(normalized):
            threshold = 0.52
        if has_deployment_scaling_intent(normalized):
            threshold = 0.58
        if count >= 2 and best_book_scores[book_slug] >= top_score * threshold:
            allowed_books.add(book_slug)

    if top_score > 0:
        score_cutoff = top_score * (0.68 if is_concept_query else 0.74 if is_procedure_query else 0.82)
    else:
        score_cutoff = 0.0
    if (has_project_terminating_intent(normalized) or has_project_finalizer_intent(normalized)) and top_score > 0:
        score_cutoff = top_score * 0.44
    if has_deployment_scaling_intent(normalized) and top_score > 0:
        score_cutoff = top_score * 0.5
    selected: list[RetrievalHit] = []
    per_book_counts: Counter[str] = Counter()
    per_book_limit = 2 if has_crash_loop_troubleshooting_intent(normalized) else 3 if is_procedure_query else 2
    seen_sections: set[tuple[str, str]] = set()
    skip_crash_loop_noise = has_crash_loop_troubleshooting_intent(normalized) and any(
        _crash_loop_priority(hit) < 9 for hit in ranked_hits
    )

    for hit in ranked_hits:
        if len(selected) >= max_chunks:
            break
        if hit.book_slug not in allowed_books:
            continue
        if _hit_score(hit) < score_cutoff:
            continue
        if skip_crash_loop_noise and _crash_loop_priority(hit) >= 9:
            continue
        if per_book_counts[hit.book_slug] >= per_book_limit:
            continue
        section_signature = (hit.book_slug, _section_core(hit.section))
        if has_crash_loop_troubleshooting_intent(normalized) and section_signature in seen_sections:
            continue
        selected.append(hit)
        per_book_counts[hit.book_slug] += 1
        seen_sections.add(section_signature)

    if (
        has_project_terminating_intent(normalized) or has_project_finalizer_intent(normalized)
    ) and len(selected) < min(2, max_chunks):
        preferred_books = (
            ("support", "building_applications", "project_apis", "config_apis")
            if has_project_terminating_intent(normalized)
            else ("support", "project_apis", "config_apis", "building_applications")
        )
        for book_slug in preferred_books:
            for hit in ranked_hits:
                if len(selected) >= min(2, max_chunks):
                    break
                if hit in selected:
                    continue
                if hit.book_slug != book_slug:
                    continue
                section_signature = (hit.book_slug, _section_core(hit.section))
                if section_signature in seen_sections:
                    continue
                selected.append(hit)
                per_book_counts[hit.book_slug] += 1
                seen_sections.add(section_signature)

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
