from __future__ import annotations

import copy
import json
import re
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

import requests

from ocp_doc_to_book.service import evaluate_canonical_book_quality
from ocp_rag_part1.embedding import EmbeddingClient
from ocp_rag_part1.settings import Settings

from .bm25 import BM25Index
from .models import RetrievalHit, RetrievalResult, SessionContext
from .query import (
    CRASH_LOOP_RE,
    OC_LOGIN_RE,
    contains_hangul,
    decompose_retrieval_queries,
    detect_unsupported_product,
    has_backup_restore_intent,
    has_certificate_monitor_intent,
    has_cluster_node_usage_intent,
    has_doc_locator_intent,
    has_follow_up_reference,
    has_hosted_control_plane_signal,
    has_mco_concept_intent,
    has_node_drain_intent,
    has_openshift_kubernetes_compare_intent,
    has_operator_concept_intent,
    has_project_finalizer_intent,
    has_project_terminating_intent,
    has_project_scoped_rbac_intent,
    has_rbac_assignment_intent,
    has_rbac_intent,
    has_crash_loop_troubleshooting_intent,
    has_pod_pending_troubleshooting_intent,
    has_pod_lifecycle_concept_intent,
    is_generic_intro_query,
    normalize_query,
    query_book_adjustments,
    rewrite_query,
)


NOISE_SECTION_RE = re.compile(r"^Legal Notice$", re.IGNORECASE)
STRUCTURED_KEY_RE = re.compile(r"[a-z0-9_.-]+/[a-z0-9_.-]+(?:=[a-z0-9_.-]+)?", re.IGNORECASE)


def _duration_ms(started_at: float) -> float:
    return round((time.perf_counter() - started_at) * 1000, 1)


def _emit_trace_event(
    trace_callback,
    *,
    step: str,
    label: str,
    status: str,
    detail: str = "",
    duration_ms: float | None = None,
    meta: dict[str, Any] | None = None,
) -> None:
    if trace_callback is None:
        return
    event = {
        "type": "trace",
        "step": step,
        "label": label,
        "status": status,
    }
    if detail:
        event["detail"] = detail
    if duration_ms is not None:
        event["duration_ms"] = duration_ms
    if meta:
        event["meta"] = meta
    trace_callback(event)


def _hit_from_payload(payload: dict, *, source: str, score: float) -> RetrievalHit:
    return RetrievalHit(
        chunk_id=str(payload["chunk_id"]),
        book_slug=str(payload["book_slug"]),
        chapter=str(payload.get("chapter", "")),
        section=str(payload.get("section", "")),
        anchor=str(payload.get("anchor", "")),
        source_url=str(payload.get("source_url", "")),
        viewer_path=str(payload.get("viewer_path", "")),
        text=str(payload.get("text", "")),
        source=source,
        raw_score=float(score),
        fused_score=float(score),
    )


def _is_noise_hit(hit: RetrievalHit) -> bool:
    return bool(NOISE_SECTION_RE.match(hit.section.strip()))


def _round_score(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 4)


def _extract_structured_query_terms(text: str) -> tuple[str, ...]:
    terms = []
    seen: set[str] = set()
    for match in STRUCTURED_KEY_RE.finditer((text or "").lower()):
        term = match.group(0).strip()
        if term and term not in seen:
            seen.add(term)
            terms.append(term)
    return tuple(terms)


def _summarize_hit(hit: RetrievalHit, *, score_key: str = "raw_score") -> dict[str, Any]:
    summary = {
        "chunk_id": hit.chunk_id,
        "book_slug": hit.book_slug,
        "section": hit.section,
        "score": _round_score(getattr(hit, score_key, 0.0)),
    }
    for key in ("bm25_score", "bm25_rank", "vector_score", "vector_rank"):
        if key in hit.component_scores:
            summary[key] = _round_score(hit.component_scores[key])
    return summary


def _summarize_hit_list(
    hits: list[RetrievalHit],
    *,
    score_key: str = "raw_score",
    limit: int = 3,
) -> dict[str, Any]:
    top_hits = [_summarize_hit(hit, score_key=score_key) for hit in hits[:limit]]
    return {
        "count": len(hits),
        "top_score": _round_score(getattr(hits[0], score_key, 0.0)) if hits else None,
        "top_hits": top_hits,
    }


def _doc_to_book_books_fingerprint(books_dir: Path) -> tuple[tuple[str, int], ...]:
    if not books_dir.exists():
        return ()
    return tuple(
        sorted(
            (path.name, path.stat().st_mtime_ns)
            for path in books_dir.glob("*.json")
            if path.is_file()
        )
    )


def _doc_to_book_row_from_section(
    payload: dict[str, Any],
    section: dict[str, Any],
    *,
    draft_id: str,
) -> dict[str, Any]:
    anchor = str(section.get("anchor") or "").strip()
    viewer_path = str(section.get("viewer_path") or "").strip()
    if not viewer_path:
        viewer_path = f"/docs/intake/{draft_id}/index.html"
        if anchor:
            viewer_path = f"{viewer_path}#{anchor}"
    section_path = [str(item).strip() for item in (section.get("section_path") or []) if str(item).strip()]
    title = str(payload.get("title") or payload.get("book_slug") or draft_id).strip()
    return {
        "chunk_id": f"{draft_id}:{str(section.get('section_key') or anchor or section.get('ordinal') or 'section').strip()}",
        "book_slug": str(payload.get("book_slug") or draft_id).strip(),
        "chapter": section_path[0] if section_path else title,
        "section": str(section.get("heading") or section.get("section_path_label") or title).strip(),
        "anchor": anchor,
        "source_url": str(section.get("source_url") or payload.get("source_uri") or "").strip(),
        "viewer_path": viewer_path,
        "text": str(section.get("text") or "").strip(),
    }


@lru_cache(maxsize=4)
def _load_doc_to_book_overlay_index(
    books_dir_str: str,
    fingerprint: tuple[tuple[str, int], ...],
) -> BM25Index | None:
    del fingerprint
    books_dir = Path(books_dir_str)
    rows: list[dict[str, Any]] = []
    for path in sorted(books_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if str(evaluate_canonical_book_quality(payload).get("quality_status") or "review") != "ready":
            continue
        sections = [dict(section) for section in (payload.get("sections") or []) if isinstance(section, dict)]
        draft_id = path.stem
        for section in sections:
            row = _doc_to_book_row_from_section(payload, section, draft_id=draft_id)
            if row["text"]:
                rows.append(row)
    if not rows:
        return None
    return BM25Index.from_rows(rows)


def _rrf_merge_hit_lists(
    hit_lists: list[list[RetrievalHit]],
    *,
    source_name: str,
    top_k: int,
    rrf_k: int = 60,
) -> list[RetrievalHit]:
    if not hit_lists:
        return []

    merged_by_id: dict[str, RetrievalHit] = {}
    for hits in hit_lists:
        for rank, hit in enumerate(hits, start=1):
            if _is_noise_hit(hit):
                continue
            if hit.chunk_id not in merged_by_id:
                merged = copy.deepcopy(hit)
                merged.source = source_name
                merged.raw_score = 0.0
                merged.fused_score = 0.0
                merged.component_scores = {}
                merged_by_id[hit.chunk_id] = merged
            merged_hit = merged_by_id[hit.chunk_id]
            merged_hit.raw_score += 1.0 / (rrf_k + rank)

    merged_hits = list(merged_by_id.values())
    merged_hits.sort(
        key=lambda item: (
            -item.raw_score,
            item.book_slug,
            item.chunk_id,
        )
    )
    return merged_hits[:top_k]


def fuse_ranked_hits(
    query: str,
    ranked_lists: dict[str, list[RetrievalHit]],
    *,
    context: SessionContext | None = None,
    top_k: int,
    rrf_k: int = 60,
    weights: dict[str, float] | None = None,
) -> list[RetrievalHit]:
    # Give semantic hits a small edge during ties while keeping fusion explainable.
    weights = weights or {"bm25": 1.0, "doc_to_book_bm25": 1.35, "vector": 1.1}
    context = context or SessionContext()
    fused_by_id: dict[str, RetrievalHit] = {}
    book_sources: dict[str, set[str]] = {}
    query_has_hangul = contains_hangul(query)
    structured_query_terms = _extract_structured_query_terms(query)
    book_boosts, book_penalties = query_book_adjustments(query, context=context)
    doc_locator_intent = has_doc_locator_intent(query)
    backup_restore_intent = has_backup_restore_intent(query)
    certificate_monitor_intent = has_certificate_monitor_intent(query)
    cluster_node_usage_intent = has_cluster_node_usage_intent(query)
    compare_intent = has_openshift_kubernetes_compare_intent(query)
    operator_concept_intent = has_operator_concept_intent(query)
    mco_concept_intent = has_mco_concept_intent(query)
    node_drain_intent = has_node_drain_intent(query)
    project_terminating_intent = has_project_terminating_intent(query)
    project_finalizer_intent = has_project_finalizer_intent(query)
    rbac_intent = has_rbac_intent(query)
    project_scoped_rbac = has_project_scoped_rbac_intent(query)
    rbac_assignment = has_rbac_assignment_intent(query)
    hosted_signal = has_hosted_control_plane_signal(query)
    pod_pending_intent = has_pod_pending_troubleshooting_intent(query)
    crash_loop_intent = has_crash_loop_troubleshooting_intent(query)
    pod_lifecycle_intent = has_pod_lifecycle_concept_intent(query)
    oc_login_intent = bool(OC_LOGIN_RE.search(query))
    context_text = " ".join(
        [
            context.current_topic or "",
            *context.open_entities,
            context.unresolved_question or "",
        ]
    ).lower()

    for source_name, hits in ranked_lists.items():
        weight = weights.get(source_name, 1.0)
        for rank, hit in enumerate(hits, start=1):
            if _is_noise_hit(hit):
                continue
            if rank <= 10:
                book_sources.setdefault(hit.book_slug, set()).add(source_name)
            if hit.chunk_id not in fused_by_id:
                fused_hit = copy.deepcopy(hit)
                fused_hit.source = "hybrid"
                fused_hit.fused_score = 0.0
                fused_hit.component_scores = {}
                fused_by_id[hit.chunk_id] = fused_hit
            fused = fused_by_id[hit.chunk_id]
            fused.component_scores[f"{source_name}_score"] = float(hit.raw_score)
            fused.component_scores[f"{source_name}_rank"] = float(rank)
            fused.fused_score += weight / (rrf_k + rank)

    fused_hits = list(fused_by_id.values())
    for hit in fused_hits:
        is_intake_doc = hit.viewer_path.startswith("/docs/intake/")
        lowered_text = hit.text.lower()
        if len(book_sources.get(hit.book_slug, set())) >= 2:
            hit.fused_score *= 1.1
        elif query_has_hangul and "vector_score" in hit.component_scores and "bm25_score" not in hit.component_scores:
            hit.fused_score *= 0.95
        if (
            is_intake_doc
            and structured_query_terms
            and "doc_to_book_bm25_score" in hit.component_scores
            and any(term in lowered_text for term in structured_query_terms)
        ):
            # Uploaded runbooks often contain operational keys such as
            # annotations, flags, or config names that must beat generic OCP
            # overview sections when the user asks for that exact token.
            hit.fused_score *= 1.42
        if query_has_hangul:
            if contains_hangul(hit.text):
                hit.fused_score *= 1.05
            else:
                hit.fused_score *= 0.85
        if is_generic_intro_query(query):
            lowered_section = hit.section.lower()
            if hit.book_slug == "architecture":
                hit.fused_score *= 1.22
                if "아키텍처 개요" in hit.section or "architecture overview" in lowered_section:
                    hit.fused_score *= 1.18
                if hit.section.startswith("1장. 아키텍처 개요"):
                    hit.fused_score *= 1.16
                if "정의" in hit.section or "소개" in hit.section:
                    hit.fused_score *= 1.1
                if "라이프사이클" in hit.section or "lifecycle" in lowered_section:
                    hit.fused_score *= 0.58
                if "기타 주요 기능" in hit.section:
                    hit.fused_score *= 0.62
                if "용어집" in hit.section or "glossary" in lowered_section:
                    hit.fused_score *= 0.74
            elif hit.book_slug == "overview":
                hit.fused_score *= 1.16
            elif hit.book_slug.endswith("_overview"):
                hit.fused_score *= 0.84
            elif hit.book_slug in {"api_overview", "networking_overview", "project_apis"}:
                hit.fused_score *= 0.88
        if compare_intent:
            lowered_section = hit.section.lower()
            lowered_text = hit.text.lower()
            if hit.book_slug in {"architecture", "overview", "security_and_compliance"}:
                hit.fused_score *= 1.08
            if "유사점 및 차이점" in hit.section or "difference" in lowered_section or "comparison" in lowered_section:
                hit.fused_score *= 1.16
            if "쿠버네티스" in hit.text or "kubernetes" in lowered_text:
                hit.fused_score *= 1.08
            if hit.book_slug in {"tutorials", "support", "cli_tools"}:
                hit.fused_score *= 0.75
        if operator_concept_intent:
            lowered_section = hit.section.lower()
            lowered_text = hit.text.lower()
            if hit.book_slug in {"architecture", "extensions", "operators", "overview"}:
                hit.fused_score *= 1.14
            if (
                "operator" in lowered_section
                and (
                    "개요" in hit.section
                    or "overview" in lowered_section
                    or "용어집" in hit.section
                    or "glossary" in lowered_section
                )
            ):
                hit.fused_score *= 1.18
            if "operator는" in hit.text or "운영 지식" in hit.text:
                hit.fused_score *= 1.08
            if (
                hit.book_slug in {"support", "web_console", "release_notes", "edge_computing"}
                or "문제 해결" in hit.section
                or "troubleshooting" in lowered_section
            ):
                hit.fused_score *= 0.55
            if "console." in lowered_text or "api" in lowered_section:
                hit.fused_score *= 0.78
        if mco_concept_intent or "machine config operator" in context_text:
            lowered_section = hit.section.lower()
            lowered_text = hit.text.lower()
            if hit.book_slug in {"architecture", "machine_configuration", "operators", "extensions"}:
                hit.fused_score *= 1.18
            if "machine config operator" in lowered_text or "machine config operator" in lowered_section:
                hit.fused_score *= 1.22
            if "machine config daemon" in lowered_text or "machineconfigdaemon" in lowered_text:
                hit.fused_score *= 1.08
            if "machine config pool" in lowered_text or "mcp" in hit.text:
                hit.fused_score *= 1.08
            if (
                "노드" in hit.text
                or "RHCOS" in hit.text
                or "kubelet" in hit.text
                or "CRI-O" in hit.text
                or "ignition" in lowered_text
            ):
                hit.fused_score *= 1.1
            if "용어집" in hit.section or "glossary" in lowered_section:
                hit.fused_score *= 1.14
            if (
                hit.book_slug in {"support", "release_notes", "edge_computing", "security_and_compliance"}
                or "비활성화" in hit.section
                or "자동으로 재부팅되지 않도록" in hit.section
                or "bug" in lowered_section
                or "troubleshooting" in lowered_section
            ):
                hit.fused_score *= 0.48
        if doc_locator_intent and hit.book_slug.endswith("_apis"):
            hit.fused_score *= 0.82
        if certificate_monitor_intent:
            lowered_text = hit.text.lower()
            lowered_section = hit.section.lower()
            if hit.book_slug == "cli_tools":
                hit.fused_score *= 1.22
            if (
                "monitor-certificates" in lowered_text
                or "oc adm ocp-certificates" in lowered_text
                or "monitor-certificates" in lowered_section
            ):
                hit.fused_score *= 1.4
            if "csr" in lowered_text:
                hit.fused_score *= 0.72
            if hit.book_slug == "security_and_compliance" and "만료" in hit.section:
                hit.fused_score *= 0.82
        if hit.book_slug in book_boosts:
            hit.fused_score *= book_boosts[hit.book_slug]
        if hit.book_slug in book_penalties:
            hit.fused_score *= book_penalties[hit.book_slug]
        if backup_restore_intent:
            lowered_text = hit.text.lower()
            lowered_section = hit.section.lower()
            if "cluster-backup.sh" in lowered_text:
                hit.fused_score *= 1.26
            if "oc debug --as-root node" in lowered_text or "chroot /host" in lowered_text:
                hit.fused_score *= 1.12
            if "snapshot save" in lowered_text:
                hit.fused_score *= 1.05
            if "cluster-restore.sh" in lowered_text or "restore.sh" in lowered_text:
                hit.fused_score *= 1.18
            if (
                not hosted_signal
                and "etcd" in context_text
                and hit.book_slug == "hosted_control_planes"
            ):
                hit.fused_score *= 0.24
            if (
                hit.book_slug == "postinstallation_configuration"
                and ("etcd 작업" in hit.chapter or "이전 클러스터 상태로 복원" in hit.section)
            ):
                hit.fused_score *= 1.16
            if hit.book_slug == "updating_clusters" and "업데이트 전 etcd 백업" in hit.section:
                hit.fused_score *= 0.84
            if "velero" in lowered_text or "oadp" in lowered_text or "hosted cluster" in lowered_text:
                hit.fused_score *= 0.46 if not hosted_signal else 1.0
        if project_terminating_intent:
            lowered_text = hit.text.lower()
            lowered_section = hit.section.lower()
            if hit.book_slug == "building_applications" and "프로젝트 삭제" in hit.section:
                hit.fused_score *= 1.05
            if hit.book_slug == "support" and "종료 중" in hit.text:
                hit.fused_score *= 1.2
            if "oc adm prune" in lowered_text or "prune" in lowered_section:
                hit.fused_score *= 0.42
        if project_finalizer_intent:
            lowered_text = hit.text.lower()
            if hit.book_slug == "support":
                hit.fused_score *= 1.26
            if (
                "terminating" in lowered_text
                or "error resolving resource" in lowered_text
                or "custom resource" in lowered_text
                or "crd" in lowered_text
            ):
                hit.fused_score *= 1.24
            if "oc adm prune" in lowered_text or hit.book_slug == "cli_tools":
                hit.fused_score *= 0.38
        if node_drain_intent:
            lowered_text = hit.text.lower()
            lowered_section = hit.section.lower()
            if hit.book_slug in {"nodes", "support"}:
                hit.fused_score *= 1.16
            if "oc adm drain" in lowered_text:
                hit.fused_score *= 1.28
            if "ignore-daemonsets" in lowered_text or "delete-emptydir-data" in lowered_text:
                hit.fused_score *= 1.08
            if hit.book_slug in {"updating_clusters", "installation_overview"}:
                hit.fused_score *= 0.54
            if "kubectl drain" in lowered_text and "oc adm drain" not in lowered_text:
                hit.fused_score *= 0.76
            if "cordon" in lowered_text and "drain" not in lowered_text:
                hit.fused_score *= 0.84
        if cluster_node_usage_intent:
            lowered_text = hit.text.lower()
            if hit.book_slug in {"support", "nodes"}:
                hit.fused_score *= 1.14
            if "oc adm top nodes" in lowered_text:
                hit.fused_score *= 1.3
            if "oc adm top node" in lowered_text:
                hit.fused_score *= 1.08
            if "oc top pods" in lowered_text or "kubectl top pods" in lowered_text:
                hit.fused_score *= 0.72
        if pod_pending_intent:
            lowered_text = hit.text.lower()
            lowered_section = hit.section.lower()
            if hit.book_slug == "support":
                hit.fused_score *= 1.14
            if hit.book_slug == "nodes":
                hit.fused_score *= 1.12
            if (
                "pod 문제 조사" in hit.text
                or "pod 오류 상태" in hit.text
                or "pod 상태 검토" in hit.text
                or "failedscheduling" in lowered_text
                or "insufficient cpu" in lowered_text
                or "insufficient memory" in lowered_text
                or "node affinity" in lowered_text
                or "taint" in lowered_text
                or "toleration" in lowered_text
            ):
                hit.fused_score *= 1.28
            if hit.book_slug == "nodes" and "failedscheduling" in lowered_text:
                hit.fused_score *= 1.22
            if "설치 문제 해결" in hit.text:
                hit.fused_score *= 0.64
                if "etcd" in lowered_section or "operator" in lowered_text:
                    hit.fused_score *= 0.7
        if crash_loop_intent:
            lowered_text = hit.text.lower()
            lowered_section = hit.section.lower()
            is_app_diag = (
                "애플리케이션 오류 조사" in hit.section
                or "애플리케이션 진단 데이터 수집" in hit.section
                or "oc describe pod/" in lowered_text
                or "oc logs -f pod/" in lowered_text
                or "애플리케이션 pod와 관련된 이벤트" in hit.text
            )
            is_event_diagnostic = (
                "이벤트 목록" in hit.section
                or ("이벤트" in hit.section and "backoff" in lowered_text)
                or "back-off restarting failed container" in lowered_text
            )
            is_probe_diagnostic = (
                "상태 점검 이해" in hit.section
                or "상태 점검 구성" in hit.section
                or "livenessprobe" in lowered_text
                or "readinessprobe" in lowered_text
            )
            is_oom_diagnostic = (
                "oom 종료 정책" in hit.section
                or "oomkilled" in lowered_text
                or "restartcount" in lowered_text
                or "exitcode: 137" in lowered_text
            )
            is_operator_image_pull_only = (
                (
                    "imagepullbackoff" in lowered_text
                    or "errimagepull" in lowered_text
                    or "back-off pulling image" in lowered_text
                )
                and "crashloopbackoff" not in lowered_text
                and "restartcount" not in lowered_text
                and "oomkilled" not in lowered_text
                and "livenessprobe" not in lowered_text
                and "readinessprobe" not in lowered_text
                and "애플리케이션" not in hit.text
            )
            if hit.book_slug in {"support", "validation_and_troubleshooting"}:
                hit.fused_score *= 1.22
            if hit.book_slug == "nodes":
                hit.fused_score *= 1.08
            if hit.book_slug == "building_applications":
                hit.fused_score *= 1.16
            if is_app_diag:
                hit.fused_score *= 1.42
            if (
                "pod 오류 상태 이해" in hit.section
                or "backoff" in lowered_text
                or "back-off restarting failed container" in lowered_text
                or "imagepullbackoff" in lowered_text
                or "errimagepull" in lowered_text
            ):
                hit.fused_score *= 1.18
            if is_event_diagnostic:
                hit.fused_score *= 1.24
            if is_probe_diagnostic:
                hit.fused_score *= 1.22
            if (
                "crashloopbackoff" in lowered_text
                or "pod 오류 상태" in hit.text
                or "애플리케이션 오류 조사" in hit.text
                or "oomkilled" in lowered_text
                or "imagepullbackoff" in lowered_text
                or "errimagepull" in lowered_text
                or "back-off restarting failed container" in lowered_text
                or "restartcount" in lowered_text
                or "livenessprobe" in lowered_text
                or "readinessprobe" in lowered_text
            ):
                hit.fused_score *= 1.18
            if hit.book_slug == "nodes" and is_oom_diagnostic:
                hit.fused_score *= 1.08
            if is_operator_image_pull_only:
                hit.fused_score *= 0.32
            if (
                "로그 수준 이해" in hit.section
                or "open vswitch" in lowered_text
                or "ovs" in lowered_section
                or "compliance operator" in lowered_text
                or "카탈로그 소스" in hit.text
                or "openshift-marketplace" in lowered_text
                or "example-catalog" in lowered_text
                or "marketplace-operator" in lowered_text
                or "인덱스 이미지" in hit.text
                or "catalog source" in lowered_text
                or "kernel module management operator" in lowered_text
                or "ovnkube-node" in lowered_text
                or ("etcd pod" in lowered_text and "애플리케이션" not in hit.text)
            ):
                hit.fused_score *= 0.54
            if (
                "operator 문제 해결" in hit.section
                or "카탈로그 소스 상태 보기" in hit.section
                or "실패한 서브스크립션 새로 고침" in hit.section
            ) and not is_app_diag and not is_oom_diagnostic:
                hit.fused_score *= 0.34
            if hit.book_slug.endswith("_apis"):
                hit.fused_score *= 0.58
            if hit.book_slug == "monitoring_apis":
                hit.fused_score *= 0.52
            if hit.book_slug == "security_and_compliance" and "oomkilled" not in lowered_text:
                hit.fused_score *= 0.62
            if (
                hit.book_slug == "support"
                and "operator 문제 해결" in hit.text
                and "애플리케이션" not in hit.text
            ):
                hit.fused_score *= 0.66
        if pod_lifecycle_intent:
            lowered_text = hit.text.lower()
            lowered_section = hit.section.lower()
            mentions_pod = (
                "pod" in lowered_text
                or "pod" in lowered_section
                or "파드" in hit.text
                or "파드" in hit.section
            )
            if hit.book_slug == "architecture":
                hit.fused_score *= 1.28
            if hit.book_slug in {"overview", "building_applications"}:
                hit.fused_score *= 1.08
            if mentions_pod:
                hit.fused_score *= 1.16
            else:
                hit.fused_score *= 0.42
            if (
                "라이프사이클" in hit.text
                or "라이프사이클" in hit.section
                or "phase" in lowered_text
                or "pending" in lowered_text
                or "running" in lowered_text
                or "succeeded" in lowered_text
                or "failed" in lowered_text
                or "unknown" in lowered_text
            ):
                hit.fused_score *= 1.18
            if (
                "용어집" in hit.section
                or "glossary" in lowered_section
                or "개요" in hit.section
                or "overview" in lowered_section
            ):
                hit.fused_score *= 1.16
            if (
                "pod는" in hit.text
                or "pod는 kubernetes" in lowered_text
                or "pod는 쿠버네티스" in hit.text
                or "pod status" in lowered_text
                or "pod phase" in lowered_text
                or "정의" in hit.section
            ):
                hit.fused_score *= 1.12
            if "pod 이해" in hit.section or "pod 사용" in hit.section:
                hit.fused_score *= 1.24
            if hit.book_slug.endswith("_apis"):
                hit.fused_score *= 0.52
            if (
                "[code]" in lowered_text
                or "oc get pod" in lowered_text
                or "evicted" in lowered_text
                or "oomkilled" in lowered_text
            ) and "용어집" not in hit.section and "glossary" not in lowered_section:
                hit.fused_score *= 0.72
            if (
                "pod 제거 이해" in hit.section
                or "oom 종료 정책 이해" in hit.section
                or "evicted" in lowered_text
                or "oomkilled" in lowered_text
            ):
                hit.fused_score *= 0.54
            if (
                "fileintegritynodestatuses" in lowered_text
                or "설치 후 노드 상태 확인" in hit.section
                or "node status" in lowered_text
                or "nodestatuses" in lowered_text
                or "status.conditions" in lowered_text
                or "status.phase" in lowered_text
            ):
                hit.fused_score *= 0.46
            if hit.book_slug in {"security_and_compliance", "installation_overview"}:
                hit.fused_score *= 0.52
            if "machine" in lowered_section and "pod" not in lowered_text:
                hit.fused_score *= 0.66
        if oc_login_intent:
            lowered_text = hit.text.lower()
            if hit.book_slug == "cli_tools":
                hit.fused_score *= 1.2
            if "oc login" in lowered_text:
                hit.fused_score *= 1.28
        if rbac_intent:
            lowered_text = hit.text.lower()
            if (
                "rbac" in lowered_text
                or "rolebinding" in lowered_text
                or "역할 바인딩" in hit.text
                or "로컬 바인딩" in hit.text
            ):
                hit.fused_score *= 1.06
            if project_scoped_rbac and (
                "프로젝트" in hit.text
                or "네임스페이스" in hit.text
                or "project" in lowered_text
                or "namespace" in lowered_text
            ):
                hit.fused_score *= 1.05
            if rbac_assignment and (
                "oc adm policy" in lowered_text
                or "add-role-to-user" in lowered_text
                or "rolebinding" in lowered_text
            ):
                hit.fused_score *= 1.08
        hit.raw_score = hit.fused_score

    fused_hits.sort(
        key=lambda item: (
            -item.fused_score,
            -int(contains_hangul(item.text)),
            item.book_slug,
            item.chunk_id,
        )
    )
    return fused_hits[:top_k]


class VectorRetriever:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.embedding_client = EmbeddingClient(settings)

    def search(self, query: str, top_k: int) -> list[RetrievalHit]:
        vector = self.embedding_client.embed_texts([query])[0]
        payloads = [
            (
                f"{self.settings.qdrant_url}/collections/{self.settings.qdrant_collection}/points/search",
                {
                    "vector": vector,
                    "limit": top_k,
                    "with_payload": True,
                    "with_vector": False,
                },
            ),
            (
                f"{self.settings.qdrant_url}/collections/{self.settings.qdrant_collection}/points/query",
                {
                    "query": vector,
                    "limit": top_k,
                    "with_payload": True,
                    "with_vector": False,
                },
            ),
        ]

        last_error = "vector search failed"
        for url, payload in payloads:
            response = requests.post(
                url,
                json=payload,
                timeout=max(self.settings.request_timeout_seconds, 30),
            )
            if not response.ok:
                last_error = response.text[:500]
                continue
            result = response.json()["result"]
            points = result["points"] if isinstance(result, dict) and "points" in result else result
            hits: list[RetrievalHit] = []
            for point in points:
                payload_row = point.get("payload") or {}
                if not payload_row:
                    continue
                hits.append(
                    _hit_from_payload(
                        payload_row,
                        source="vector",
                        score=float(point.get("score", 0.0)),
                    )
                )
            return hits

        raise ValueError(last_error)


class Part2Retriever:
    def __init__(
        self,
        settings: Settings,
        bm25_index: BM25Index,
        *,
        vector_retriever: VectorRetriever | None = None,
    ) -> None:
        self.settings = settings
        self.bm25_index = bm25_index
        self.vector_retriever = vector_retriever

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
        *,
        enable_vector: bool = True,
    ) -> "Part2Retriever":
        bm25_index = BM25Index.from_jsonl(settings.bm25_corpus_path)
        vector_retriever = VectorRetriever(settings) if enable_vector else None
        return cls(settings, bm25_index, vector_retriever=vector_retriever)

    def default_log_path(self) -> Path:
        return self.settings.retrieval_log_path

    def append_log(self, result: RetrievalResult, log_path: Path | None = None) -> Path:
        target = log_path or self.default_log_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")
        return target

    def _doc_to_book_overlay_index(self) -> BM25Index | None:
        books_dir = self.settings.doc_to_book_books_dir
        fingerprint = _doc_to_book_books_fingerprint(books_dir)
        if not fingerprint:
            return None
        return _load_doc_to_book_overlay_index(str(books_dir), fingerprint)

    def retrieve(
        self,
        query: str,
        *,
        context: SessionContext | None = None,
        top_k: int = 8,
        candidate_k: int = 20,
        use_bm25: bool = True,
        use_vector: bool = True,
        trace_callback=None,
    ) -> RetrievalResult:
        retrieve_started_at = time.perf_counter()
        context = context or SessionContext()
        timings_ms: dict[str, float] = {}
        normalize_started_at = time.perf_counter()
        normalized_query = normalize_query(query)
        timings_ms["normalize_query"] = _duration_ms(normalize_started_at)
        _emit_trace_event(
            trace_callback,
            step="normalize_query",
            label="질문 정규화 완료",
            status="done",
            detail=normalized_query[:180],
            duration_ms=timings_ms["normalize_query"],
        )
        warnings: list[str] = []
        unsupported_product = detect_unsupported_product(normalized_query)
        decomposed_queries = decompose_retrieval_queries(query)
        rewrite_started_at = time.perf_counter()
        rewritten_query = rewrite_query(normalized_query, context)
        timings_ms["rewrite_query"] = _duration_ms(rewrite_started_at)
        _emit_trace_event(
            trace_callback,
            step="rewrite_query",
            label="검색 질의 준비 완료",
            status="done",
            detail=rewritten_query[:180],
            duration_ms=timings_ms["rewrite_query"],
        )
        if len(decomposed_queries) > 1:
            _emit_trace_event(
                trace_callback,
                step="decompose_query",
                label="질문 분해 완료",
                status="done",
                detail=" | ".join(decomposed_queries[:3]),
                meta={"subqueries": decomposed_queries},
            )

        if unsupported_product is not None:
            warnings.append(f"query appears outside OCP corpus: {unsupported_product}")
            return RetrievalResult(
                query=query,
                normalized_query=normalized_query,
                rewritten_query=rewritten_query,
                top_k=top_k,
                candidate_k=candidate_k,
                context=context.to_dict(),
                hits=[],
                trace={
                    "warnings": warnings,
                    "bm25": [],
                    "vector": [],
                    "timings_ms": {
                        **timings_ms,
                        "total": _duration_ms(retrieve_started_at),
                    },
                    "decomposed_queries": decomposed_queries,
                },
            )

        effective_candidate_k = candidate_k
        if (
            len(decomposed_queries) > 1
            or has_openshift_kubernetes_compare_intent(normalized_query)
            or has_doc_locator_intent(normalized_query)
            or has_backup_restore_intent(normalized_query)
            or has_certificate_monitor_intent(normalized_query)
            or has_follow_up_reference(query)
        ):
            effective_candidate_k = max(candidate_k, 40)

        rewritten_queries = [
            rewrite_query(normalize_query(subquery), context)
            for subquery in decomposed_queries
        ]

        bm25_hits = []
        intake_bm25_hits: list[RetrievalHit] = []
        if use_bm25:
            _emit_trace_event(
                trace_callback,
                step="bm25_search",
                label="키워드 검색 중",
                status="running",
            )
            bm25_started_at = time.perf_counter()
            bm25_hit_sets = [
                self.bm25_index.search(subquery, top_k=effective_candidate_k)
                for subquery in rewritten_queries
            ]
            bm25_hits = _rrf_merge_hit_lists(
                bm25_hit_sets,
                source_name="bm25",
                top_k=effective_candidate_k,
            )
            overlay_index = self._doc_to_book_overlay_index()
            intake_hit_sets: list[list[RetrievalHit]] = []
            if overlay_index is not None:
                intake_hit_sets = [
                    overlay_index.search(subquery, top_k=effective_candidate_k)
                    for subquery in rewritten_queries
                ]
                intake_bm25_hits = _rrf_merge_hit_lists(
                    intake_hit_sets,
                    source_name="doc_to_book_bm25",
                    top_k=effective_candidate_k,
                )
            timings_ms["bm25_search"] = _duration_ms(bm25_started_at)
            _emit_trace_event(
                trace_callback,
                step="bm25_search",
                label="키워드 검색 완료",
                status="done",
                detail=f"코어 {len(bm25_hits)}개 · intake {len(intake_bm25_hits)}개",
                duration_ms=timings_ms["bm25_search"],
                meta={
                    "candidate_k": effective_candidate_k,
                    "core_hits": len(bm25_hits),
                    "intake_hits": len(intake_bm25_hits),
                    "summary": _summarize_hit_list(bm25_hits),
                },
            )
        vector_hits: list[RetrievalHit] = []
        if use_vector:
            if self.vector_retriever is None:
                warnings.append("vector retriever is not configured")
                _emit_trace_event(
                    trace_callback,
                    step="vector_search",
                    label="벡터 검색 생략",
                    status="warning",
                    detail="vector retriever is not configured",
                )
            else:
                try:
                    _emit_trace_event(
                        trace_callback,
                        step="vector_search",
                        label="의미 검색 중",
                        status="running",
                    )
                    vector_started_at = time.perf_counter()
                    vector_hit_sets = [
                        self.vector_retriever.search(subquery, top_k=effective_candidate_k)
                        for subquery in rewritten_queries
                    ]
                    vector_hits = _rrf_merge_hit_lists(
                        vector_hit_sets,
                        source_name="vector",
                        top_k=effective_candidate_k,
                    )
                    timings_ms["vector_search"] = _duration_ms(vector_started_at)
                    _emit_trace_event(
                        trace_callback,
                        step="vector_search",
                        label="의미 검색 완료",
                        status="done",
                        detail=f"후보 {len(vector_hits)}개",
                        duration_ms=timings_ms["vector_search"],
                        meta={
                            "candidate_k": effective_candidate_k,
                            "summary": _summarize_hit_list(vector_hits),
                        },
                    )
                except Exception as exc:  # noqa: BLE001
                    warnings.append(f"vector search failed: {exc}")
                    _emit_trace_event(
                        trace_callback,
                        step="vector_search",
                        label="의미 검색 실패",
                        status="warning",
                        detail=str(exc),
                    )

        _emit_trace_event(
            trace_callback,
            step="fusion",
            label="검색 결과 결합 중",
            status="running",
        )
        fusion_started_at = time.perf_counter()
        hits = fuse_ranked_hits(
            rewritten_query,
            {
                "bm25": bm25_hits,
                "doc_to_book_bm25": intake_bm25_hits,
                "vector": vector_hits,
            },
            context=context,
            top_k=top_k,
        )
        timings_ms["fusion"] = _duration_ms(fusion_started_at)
        top_hit = hits[0] if hits else None
        top_detail = (
            f"{top_hit.book_slug} · {top_hit.section}"
            if top_hit is not None
            else "상위 근거 없음"
        )
        _emit_trace_event(
            trace_callback,
            step="fusion",
            label="검색 결과 결합 완료",
            status="done",
            detail=top_detail,
            duration_ms=timings_ms["fusion"],
            meta={"summary": _summarize_hit_list(hits, score_key="fused_score")},
        )
        bm25_summary = _summarize_hit_list(bm25_hits)
        vector_summary = _summarize_hit_list(vector_hits)
        hybrid_summary = _summarize_hit_list(hits, score_key="fused_score")
        trace = {
            "warnings": warnings,
            "bm25": [hit.to_dict() for hit in bm25_hits[: min(candidate_k, 10)]],
            "doc_to_book_bm25": [
                hit.to_dict() for hit in intake_bm25_hits[: min(candidate_k, 10)]
            ],
            "vector": [hit.to_dict() for hit in vector_hits[: min(candidate_k, 10)]],
            "hybrid": [hit.to_dict() for hit in hits[: min(top_k, 5)]],
            "metrics": {
                "bm25": bm25_summary,
                "doc_to_book_bm25": _summarize_hit_list(intake_bm25_hits),
                "vector": vector_summary,
                "hybrid": hybrid_summary,
            },
            "decomposed_queries": decomposed_queries,
            "effective_candidate_k": effective_candidate_k,
            "timings_ms": {
                **timings_ms,
                "total": _duration_ms(retrieve_started_at),
            },
        }
        return RetrievalResult(
            query=query,
            normalized_query=normalized_query,
            rewritten_query=rewritten_query,
            top_k=top_k,
            candidate_k=candidate_k,
            context=context.to_dict(),
            hits=hits,
            trace=trace,
        )
