from __future__ import annotations

import copy
import time
from typing import Any

from play_book_studio.app.wiki_user_overlay import build_wiki_overlay_signal_payload

from .followups import has_follow_up_reference
from .models import RetrievalHit, SessionContext
from .query import (
    has_backup_restore_intent,
    has_cluster_node_usage_intent,
    has_mco_concept_intent,
    is_generic_intro_query,
)
from .ranking import summarize_hit_list as _summarize_hit_list
from .trace import duration_ms as _duration_ms, emit_trace_event as _emit_trace_event


def _has_registry_storage_ops_intent(query: str) -> bool:
    lowered_query = query.lower()
    has_registry_signal = (
        "image registry" in lowered_query
        or "imageregistry" in lowered_query
        or "registry" in lowered_query
        or "레지스트리" in query
    )
    has_image_signal = "image" in lowered_query or "이미지" in query
    has_storage_signal = (
        "storage" in lowered_query
        or "mirror" in lowered_query
        or "미러" in query
        or "스토리지" in query
        or "저장소" in query
    )
    has_configuration_signal = (
        "config" in lowered_query
        or "configure" in lowered_query
        or "구성" in query
        or "설정" in query
        or "준비" in query
    )
    has_install_scope_signal = (
        "install" in lowered_query
        or "설치" in query
        or "platform" in lowered_query
        or "플랫폼" in query
        or "manual" in lowered_query
        or "수동" in query
        or "bare metal" in lowered_query
        or "베어 메탈" in query
    )
    return (
        has_registry_signal
        and has_image_signal
        and (has_storage_signal or has_configuration_signal)
        and not has_install_scope_signal
    )


def _is_customer_pack_explicit_query(query: str) -> bool:
    lowered = (query or "").lower()
    return any(
        token in lowered
        for token in (
            "업로드 문서",
            "업로드한 문서",
            "고객 문서",
            "고객문서",
            "우리 문서",
            "our document",
            "customer pack",
            "customer-pack",
        )
    )


def _rebalance_uploaded_customer_pack_hits(
    query: str,
    *,
    hybrid_hits: list[RetrievalHit],
    reranked_hits: list[RetrievalHit],
) -> list[RetrievalHit]:
    if not _is_customer_pack_explicit_query(query):
        return reranked_hits
    if not any(str(hit.source_collection or "").strip() == "uploaded" for hit in hybrid_hits):
        return reranked_hits
    if reranked_hits and str(reranked_hits[0].source_collection or "").strip() == "uploaded":
        return reranked_hits

    hybrid_rank = {hit.chunk_id: index for index, hit in enumerate(hybrid_hits)}
    reordered = list(reranked_hits)
    existing_ids = {hit.chunk_id for hit in reordered}
    uploaded_sources: list[tuple[str, int, RetrievalHit]] = [
        ("reranked", index, hit)
        for index, hit in enumerate(reordered)
        if str(hit.source_collection or "").strip() == "uploaded"
    ]
    uploaded_sources.extend(
        ("hybrid", -1, hit)
        for hit in hybrid_hits
        if str(hit.source_collection or "").strip() == "uploaded" and hit.chunk_id not in existing_ids
    )
    if not uploaded_sources:
        return reranked_hits

    def _uploaded_sort_key(item: tuple[str, int, RetrievalHit]) -> tuple[int, float, float, str, str]:
        hit = item[2]
        return (
            hybrid_rank.get(hit.chunk_id, 999),
            -hit.component_scores.get("pre_rerank_fused_score", hit.fused_score),
            -hit.component_scores.get("reranker_score", hit.fused_score),
            hit.book_slug,
            hit.chunk_id,
        )

    uploaded_sources.sort(key=_uploaded_sort_key)
    source_name, source_index, source_hit = uploaded_sources[0]
    if source_name == "reranked":
        uploaded_hit = reordered.pop(source_index)
    else:
        uploaded_hit = copy.deepcopy(source_hit)
        uploaded_hit.source = "hybrid_uploaded_rescued"
        uploaded_hit.component_scores.setdefault(
            "pre_rerank_fused_score",
            float(uploaded_hit.fused_score),
        )
        uploaded_hit.component_scores.setdefault(
            "reranker_score",
            float(uploaded_hit.component_scores["pre_rerank_fused_score"]),
        )
    reordered.insert(0, uploaded_hit)
    return reordered


def _rebalance_registry_storage_hits(
    query: str,
    *,
    hybrid_hits: list[RetrievalHit],
    reranked_hits: list[RetrievalHit],
) -> list[RetrievalHit]:
    if not _has_registry_storage_ops_intent(query):
        return reranked_hits

    preferred_books = {"registry", "images"}
    install_books = {"installation_overview", "installing_on_any_platform"}
    if not hybrid_hits or hybrid_hits[0].book_slug not in preferred_books:
        return reranked_hits
    if not reranked_hits or reranked_hits[0].book_slug not in install_books:
        return reranked_hits
    if not any(hit.book_slug in preferred_books for hit in reranked_hits):
        return reranked_hits

    hybrid_rank = {hit.chunk_id: index for index, hit in enumerate(hybrid_hits)}
    reordered = list(reranked_hits)
    reordered.sort(
        key=lambda hit: (
            0 if hit.book_slug in preferred_books else 1,
            1 if hit.book_slug in install_books else 0,
            hybrid_rank.get(hit.chunk_id, 999),
            -hit.component_scores.get("pre_rerank_fused_score", 0.0),
            -hit.component_scores.get("reranker_score", hit.fused_score),
            hit.book_slug,
            hit.chunk_id,
        )
    )
    return reordered


def _rebalance_registry_follow_up_hits(
    query: str,
    *,
    hybrid_hits: list[RetrievalHit],
    reranked_hits: list[RetrievalHit],
) -> list[RetrievalHit]:
    lowered_query = query.lower()
    if not has_follow_up_reference(query):
        return reranked_hits
    if not (
        ("image registry" in lowered_query or "registry" in lowered_query or "레지스트리" in query)
        and ("image" in lowered_query or "이미지" in query or "저장소" in query)
    ):
        return reranked_hits
    if not hybrid_hits or hybrid_hits[0].book_slug not in {"registry", "images"}:
        return reranked_hits
    if not reranked_hits or reranked_hits[0].book_slug in {"registry", "images"}:
        return reranked_hits

    preferred_books = {"registry", "images"}
    if not any(hit.book_slug in preferred_books for hit in reranked_hits):
        return reranked_hits

    hybrid_rank = {hit.chunk_id: index for index, hit in enumerate(hybrid_hits)}
    reordered = list(reranked_hits)
    reordered.sort(
        key=lambda hit: (
            0 if hit.book_slug in preferred_books else 1,
            1 if hit.book_slug == "installation_overview" else 0,
            hybrid_rank.get(hit.chunk_id, 999),
            -hit.component_scores.get("reranker_score", hit.fused_score),
            hit.book_slug,
            hit.chunk_id,
        )
    )
    return reordered


def _rebalance_mco_concept_hits(
    query: str,
    *,
    hybrid_hits: list[RetrievalHit],
    reranked_hits: list[RetrievalHit],
) -> list[RetrievalHit]:
    if not has_mco_concept_intent(query):
        return reranked_hits
    preferred_books = {"machine_configuration", "operators"}
    if not hybrid_hits or not any(hit.book_slug in preferred_books for hit in hybrid_hits[:5]):
        return reranked_hits
    if not reranked_hits or reranked_hits[0].book_slug in preferred_books:
        return reranked_hits

    hybrid_rank = {hit.chunk_id: index for index, hit in enumerate(hybrid_hits)}
    reordered = list(reranked_hits)
    reordered.sort(
        key=lambda hit: (
            0 if hit.book_slug in preferred_books else 1,
            1
            if (
                hit.book_slug == "updating_clusters"
                or "일반 용어" in hit.section
                or "glossary" in hit.section.lower()
            )
            else 0,
            hybrid_rank.get(hit.chunk_id, 999),
            -hit.component_scores.get("pre_rerank_fused_score", 0.0),
            -hit.component_scores.get("reranker_score", hit.fused_score),
            hit.book_slug,
            hit.chunk_id,
        )
    )
    return reordered


def _rebalance_cluster_node_usage_hits(
    query: str,
    *,
    hybrid_hits: list[RetrievalHit],
    reranked_hits: list[RetrievalHit],
) -> list[RetrievalHit]:
    if not has_cluster_node_usage_intent(query):
        return reranked_hits
    if not hybrid_hits or hybrid_hits[0].book_slug != "support":
        return reranked_hits
    if not reranked_hits or reranked_hits[0].book_slug != "nodes":
        return reranked_hits
    if not any(hit.book_slug == "support" for hit in reranked_hits):
        return reranked_hits

    hybrid_rank = {hit.chunk_id: index for index, hit in enumerate(hybrid_hits)}
    reordered = list(reranked_hits)
    reordered.sort(
        key=lambda hit: (
            0 if hit.book_slug == "support" else 1 if hit.book_slug == "nodes" else 2,
            hybrid_rank.get(hit.chunk_id, 999),
            -hit.component_scores.get("pre_rerank_fused_score", 0.0),
            -hit.component_scores.get("reranker_score", hit.fused_score),
            hit.book_slug,
            hit.chunk_id,
        )
    )
    return reordered


def _classify_etcd_backup_restore_query(query: str, hybrid_hits: list[RetrievalHit]) -> str | None:
    lowered = (query or "").lower()
    backup_signal = "백업" in query or "backup" in lowered
    restore_signal = any(token in lowered for token in ("복원", "복구", "restore", "recovery"))
    has_etcd_signal = "etcd" in lowered or any(
        hit.book_slug in {"etcd", "postinstallation_configuration"}
        for hit in hybrid_hits[:8]
    )
    if not has_etcd_signal or not has_backup_restore_intent(query):
        return None
    if backup_signal and not restore_signal:
        return "backup"
    if restore_signal:
        return "restore"
    if has_follow_up_reference(query):
        return "restore"
    return None


def _etcd_backup_priority(hit: RetrievalHit) -> int:
    lowered_section = (hit.section or "").lower()
    lowered_text = (hit.text or "").lower()
    if (
        "cluster-backup.sh" in lowered_text
        or "oc debug --as-root node" in lowered_text
        or "chroot /host" in lowered_text
    ):
        return 0
    if "etcd 데이터 백업" in lowered_section:
        return 1
    if "자동화된 etcd 백업" in lowered_section:
        return 2
    if "cluster-restore.sh" in lowered_text or "복원" in lowered_section or "restore" in lowered_text:
        return 8
    return 5


def _etcd_restore_priority(hit: RetrievalHit) -> int:
    lowered_section = (hit.section or "").lower()
    lowered_text = (hit.text or "").lower()
    if (
        "cluster-restore.sh" in lowered_text
        or "수동으로 클러스터 복원" in lowered_section
        or "이전 클러스터 상태로 복원" in lowered_section
    ):
        return 0
    if "복원 절차 테스트" in lowered_section:
        return 2
    if "cluster-backup.sh" in lowered_text or "etcd 데이터 백업" in lowered_section:
        return 5
    return 3


def _rebalance_etcd_backup_restore_hits(
    query: str,
    *,
    hybrid_hits: list[RetrievalHit],
    reranked_hits: list[RetrievalHit],
) -> list[RetrievalHit]:
    if _is_customer_pack_explicit_query(query) and any(
        str(hit.source_collection or "").strip() == "uploaded"
        for hit in (*reranked_hits, *hybrid_hits)
    ):
        return reranked_hits
    classification = _classify_etcd_backup_restore_query(query, hybrid_hits)
    if classification is None:
        return reranked_hits
    hybrid_rank = {hit.chunk_id: index for index, hit in enumerate(hybrid_hits)}
    priority_fn = _etcd_backup_priority if classification == "backup" else _etcd_restore_priority
    if classification == "backup":
        preferred_books = {
            "backup_and_restore": 0,
            "etcd": 1,
            "postinstallation_configuration": 2,
            "hosted_control_planes": 3,
            "updating_clusters": 4,
        }
        companion_books = {"etcd", "postinstallation_configuration"}
    else:
        preferred_books = {
            "postinstallation_configuration": 0,
            "etcd": 1,
            "backup_and_restore": 2,
            "hosted_control_planes": 3,
            "updating_clusters": 4,
        }
        companion_books = {"etcd", "backup_and_restore"}
    reordered = list(reranked_hits)
    reordered.sort(
        key=lambda hit: (
            priority_fn(hit),
            preferred_books.get(hit.book_slug, 9),
            hybrid_rank.get(hit.chunk_id, 999),
            -hit.component_scores.get("pre_rerank_fused_score", 0.0),
            -hit.component_scores.get("reranker_score", hit.fused_score),
            hit.book_slug,
            hit.chunk_id,
        )
    )

    # etcd backup 절차는 backup_and_restore 를 primary로 유지하되,
    # dedicated etcd 또는 legacy postinstall 문서 하나는 함께 남겨 참조 폭을 유지한다.
    if classification == "backup":
        def _companion_sort_key(hit: RetrievalHit) -> tuple[int, int, int, float, float, str, str]:
            return (
                priority_fn(hit),
                preferred_books.get(hit.book_slug, 9),
                hybrid_rank.get(hit.chunk_id, 999),
                -hit.component_scores.get("pre_rerank_fused_score", hit.fused_score),
                -hit.component_scores.get("reranker_score", hit.fused_score),
                hit.book_slug,
                hit.chunk_id,
            )

        companion_sources: list[tuple[str, int, RetrievalHit]] = [
            ("reranked", index, hit)
            for index, hit in enumerate(reordered)
            if hit.book_slug in companion_books
        ]
        existing_ids = {hit.chunk_id for hit in reordered}
        companion_sources.extend(
            ("hybrid", -1, hit)
            for hit in hybrid_hits
            if hit.book_slug in companion_books and hit.chunk_id not in existing_ids
        )
        companion_sources.sort(key=lambda item: _companion_sort_key(item[2]))

        companion_hit: RetrievalHit | None = None
        if companion_sources:
            source_name, companion_index, source_hit = companion_sources[0]
            if source_name == "reranked":
                companion_hit = reordered.pop(companion_index)
            else:
                companion_hit = copy.deepcopy(source_hit)
                companion_hit.source = "hybrid_companion_rescued"
                companion_hit.component_scores.setdefault(
                    "pre_rerank_fused_score",
                    float(companion_hit.fused_score),
                )
                companion_hit.component_scores.setdefault(
                    "reranker_score",
                    float(companion_hit.component_scores["pre_rerank_fused_score"]),
                )
        if companion_hit is not None:
            insert_at = 1 if reordered and reordered[0].book_slug == "backup_and_restore" else 0
            reordered.insert(insert_at, companion_hit)
    return reordered


def _overlay_recent_preference_scores(
    *,
    root_dir,
    user_id: str,
) -> tuple[dict[str, int], dict[str, int]]:
    normalized_user_id = str(user_id or "").strip()
    if root_dir is None or not normalized_user_id:
        return {}, {}
    try:
        payload = build_wiki_overlay_signal_payload(root_dir, user_id=normalized_user_id)
    except Exception:  # noqa: BLE001
        return {}, {}
    user_focus = payload.get("user_focus") if isinstance(payload, dict) else None
    recent_targets = user_focus.get("recent_targets") if isinstance(user_focus, dict) else None
    if not isinstance(recent_targets, list):
        return {}, {}
    book_scores: dict[str, int] = {}
    entity_scores: dict[str, int] = {}
    for index, item in enumerate(recent_targets[:12]):
        if not isinstance(item, dict):
            continue
        target_ref = str(item.get("target_ref") or "").strip()
        if not target_ref:
            continue
        base_score = max(10, 80 - index * 6)
        if target_ref.startswith("book:"):
            slug = target_ref.split(":", 1)[1].strip()
            if slug:
                book_scores[slug] = max(book_scores.get(slug, 0), base_score)
        elif target_ref.startswith("section:"):
            slug = target_ref.split(":", 1)[1].split("#", 1)[0].strip()
            if slug:
                book_scores[slug] = max(book_scores.get(slug, 0), base_score - 8)
        elif target_ref.startswith("figure:"):
            parts = target_ref.split(":")
            if len(parts) >= 3 and parts[1].strip():
                book_scores[parts[1].strip()] = max(book_scores.get(parts[1].strip(), 0), base_score - 16)
        elif target_ref.startswith("entity:"):
            entity = target_ref.split(":", 1)[1].strip()
            if entity:
                entity_scores[entity] = max(entity_scores.get(entity, 0), base_score)
    return book_scores, entity_scores


def _overlay_entity_hit_score(hit: RetrievalHit, entity_scores: dict[str, int]) -> int:
    lowered_section = (hit.section or "").lower()
    lowered_text = (hit.text or "").lower()
    score = 0
    if "etcd" in lowered_section or "etcd" in lowered_text:
        score = max(score, entity_scores.get("etcd", 0))
    if "machine config" in lowered_section or "machine config" in lowered_text or "mco" in lowered_section or "mco" in lowered_text:
        score = max(score, entity_scores.get("machine-config-operator", 0))
    if "prometheus" in lowered_section or "prometheus" in lowered_text:
        score = max(score, entity_scores.get("prometheus", 0))
    if "proxy" in lowered_section or "proxy" in lowered_text:
        score = max(score, entity_scores.get("cluster-wide-proxy", 0))
    if "control plane" in lowered_section or "control plane" in lowered_text:
        score = max(score, entity_scores.get("control-plane-nodes", 0))
    return score


def _rebalance_overlay_preference_hits(
    query: str,
    *,
    hybrid_hits: list[RetrievalHit],
    reranked_hits: list[RetrievalHit],
    context: SessionContext | None,
    root_dir,
) -> list[RetrievalHit]:
    del query
    user_id = str(getattr(context, "user_id", "") or "").strip()
    if not user_id:
        return reranked_hits
    book_scores, entity_scores = _overlay_recent_preference_scores(root_dir=root_dir, user_id=user_id)
    if not book_scores and not entity_scores:
        return reranked_hits
    hybrid_rank = {hit.chunk_id: index for index, hit in enumerate(hybrid_hits)}
    reordered = list(reranked_hits)
    reordered.sort(
        key=lambda hit: (
            -max(
                book_scores.get(hit.book_slug, 0),
                _overlay_entity_hit_score(hit, entity_scores),
            ),
            hybrid_rank.get(hit.chunk_id, 999),
            -hit.component_scores.get("pre_rerank_fused_score", 0.0),
            -hit.component_scores.get("reranker_score", hit.fused_score),
            hit.book_slug,
            hit.chunk_id,
        )
    )
    return reordered


def _is_generic_intro_candidate(hit: RetrievalHit) -> bool:
    book_slug = str(hit.book_slug or "").strip()
    section = str(hit.section or "").strip()
    lowered_section = section.lower()

    if book_slug not in {"architecture", "overview"}:
        return False
    if any(
        token in section
        for token in (
            "라이프사이클",
            "사용자 정의 운영 체제",
            "기타 주요 기능",
            "용어집",
        )
    ):
        return False
    if any(
        token in lowered_section
        for token in (
            "lifecycle",
            "custom os",
            "glossary",
        )
    ):
        return False
    return any(
        token in section
        for token in (
            "개요",
            "소개",
            "정의",
        )
    ) or any(
        token in lowered_section
        for token in (
            "overview",
            "introduction",
            "definition",
        )
    )


def _rebalance_generic_intro_hits(
    query: str,
    *,
    hybrid_hits: list[RetrievalHit],
    reranked_hits: list[RetrievalHit],
) -> list[RetrievalHit]:
    if not is_generic_intro_query(query):
        return reranked_hits
    if not hybrid_hits or not reranked_hits:
        return reranked_hits
    if _is_generic_intro_candidate(reranked_hits[0]):
        return reranked_hits

    hybrid_rank = {hit.chunk_id: index for index, hit in enumerate(hybrid_hits)}
    reordered = list(reranked_hits)
    existing_ids = {hit.chunk_id for hit in reordered}
    candidate_sources: list[tuple[str, int, RetrievalHit]] = [
        ("reranked", index, hit)
        for index, hit in enumerate(reordered)
        if _is_generic_intro_candidate(hit)
    ]
    candidate_sources.extend(
        ("hybrid", -1, hit)
        for hit in hybrid_hits
        if _is_generic_intro_candidate(hit) and hit.chunk_id not in existing_ids
    )
    if not candidate_sources:
        return reranked_hits

    def _candidate_sort_key(item: tuple[str, int, RetrievalHit]) -> tuple[int, int, float, float, str, str]:
        hit = item[2]
        book_priority = 0 if hit.book_slug == "overview" else 1
        return (
            book_priority,
            hybrid_rank.get(hit.chunk_id, 999),
            -hit.component_scores.get("pre_rerank_fused_score", hit.fused_score),
            -hit.component_scores.get("reranker_score", hit.fused_score),
            str(hit.book_slug or ""),
            str(hit.chunk_id or ""),
        )

    candidate_sources.sort(key=_candidate_sort_key)
    source_name, source_index, source_hit = candidate_sources[0]
    if source_name == "reranked":
        preferred_hit = reordered.pop(source_index)
    else:
        preferred_hit = copy.deepcopy(source_hit)
        preferred_hit.source = "hybrid_intro_rescued"
        preferred_hit.component_scores.setdefault(
            "pre_rerank_fused_score",
            float(preferred_hit.fused_score),
        )
        preferred_hit.component_scores.setdefault(
            "reranker_score",
            float(preferred_hit.component_scores["pre_rerank_fused_score"]),
        )
    reordered.insert(0, preferred_hit)
    return reordered


def _top_book_slug(hits: list[RetrievalHit]) -> str:
    if not hits:
        return ""
    return str(hits[0].book_slug or "")


def _apply_rebalance_rule(
    *,
    rule_name: str,
    query: str,
    hybrid_hits: list[RetrievalHit],
    reranked_hits: list[RetrievalHit],
    rule_fn,
    rebalance_reasons: list[str],
) -> list[RetrievalHit]:
    before_ids = [hit.chunk_id for hit in reranked_hits]
    rebalanced_hits = rule_fn(
        query,
        hybrid_hits=hybrid_hits,
        reranked_hits=reranked_hits,
    )
    after_ids = [hit.chunk_id for hit in rebalanced_hits]
    if after_ids != before_ids and rule_name not in rebalance_reasons:
        rebalance_reasons.append(rule_name)
    return rebalanced_hits


def maybe_rerank_hits(
    retriever,
    *,
    query: str,
    hybrid_hits: list[RetrievalHit],
    context: SessionContext | None,
    top_k: int,
    trace_callback,
    timings_ms: dict[str, float],
) -> tuple[list[RetrievalHit], dict[str, Any]]:
    hits = hybrid_hits[:top_k]
    reranker_trace: dict[str, Any] = {
        "enabled": retriever.reranker is not None,
        "applied": False,
        "model": getattr(retriever.reranker, "model_name", ""),
        "top_n": getattr(retriever.reranker, "top_n", 0),
        "top1_before": _top_book_slug(hybrid_hits),
        "top1_after_model": "",
        "top1_after": _top_book_slug(hits),
        "top1_changed": False,
        "rebalance_reasons": [],
    }
    if retriever.reranker is None or not hybrid_hits:
        return hits, reranker_trace
    try:
        _emit_trace_event(
            trace_callback,
            step="rerank",
            label="리랭킹 중",
            status="running",
        )
        rerank_started_at = time.perf_counter()
        reranked_hits = retriever.reranker.rerank(
            query,
            hybrid_hits,
            top_k=top_k,
        )
        reranker_trace["top1_after_model"] = _top_book_slug(reranked_hits)
        rebalance_reasons: list[str] = []
        reranked_hits = _apply_rebalance_rule(
            rule_name="overlay_preference",
            query=query,
            hybrid_hits=hybrid_hits,
            reranked_hits=reranked_hits,
            rule_fn=lambda rebalance_query, *, hybrid_hits, reranked_hits: _rebalance_overlay_preference_hits(
                rebalance_query,
                hybrid_hits=hybrid_hits,
                reranked_hits=reranked_hits,
                context=context,
                root_dir=retriever.settings.root_dir,
            ),
            rebalance_reasons=rebalance_reasons,
        )
        reranked_hits = _apply_rebalance_rule(
            rule_name="registry_storage_intent",
            query=query,
            hybrid_hits=hybrid_hits,
            reranked_hits=reranked_hits,
            rule_fn=_rebalance_registry_storage_hits,
            rebalance_reasons=rebalance_reasons,
        )
        reranked_hits = _apply_rebalance_rule(
            rule_name="registry_follow_up_intent",
            query=query,
            hybrid_hits=hybrid_hits,
            reranked_hits=reranked_hits,
            rule_fn=_rebalance_registry_follow_up_hits,
            rebalance_reasons=rebalance_reasons,
        )
        reranked_hits = _apply_rebalance_rule(
            rule_name="mco_concept_intent",
            query=query,
            hybrid_hits=hybrid_hits,
            reranked_hits=reranked_hits,
            rule_fn=_rebalance_mco_concept_hits,
            rebalance_reasons=rebalance_reasons,
        )
        reranked_hits = _apply_rebalance_rule(
            rule_name="cluster_node_usage_intent",
            query=query,
            hybrid_hits=hybrid_hits,
            reranked_hits=reranked_hits,
            rule_fn=_rebalance_cluster_node_usage_hits,
            rebalance_reasons=rebalance_reasons,
        )
        reranked_hits = _apply_rebalance_rule(
            rule_name="uploaded_customer_pack_priority",
            query=query,
            hybrid_hits=hybrid_hits,
            reranked_hits=reranked_hits,
            rule_fn=_rebalance_uploaded_customer_pack_hits,
            rebalance_reasons=rebalance_reasons,
        )
        reranked_hits = _apply_rebalance_rule(
            rule_name="etcd_backup_restore_intent",
            query=query,
            hybrid_hits=hybrid_hits,
            reranked_hits=reranked_hits,
            rule_fn=_rebalance_etcd_backup_restore_hits,
            rebalance_reasons=rebalance_reasons,
        )
        reranked_hits = _apply_rebalance_rule(
            rule_name="generic_intro_intent",
            query=query,
            hybrid_hits=hybrid_hits,
            reranked_hits=reranked_hits,
            rule_fn=_rebalance_generic_intro_hits,
            rebalance_reasons=rebalance_reasons,
        )
        timings_ms["rerank"] = _duration_ms(rerank_started_at)
        hits = reranked_hits[:top_k]
        reranker_trace["top1_after"] = _top_book_slug(hits)
        reranker_trace["top1_changed"] = reranker_trace["top1_before"] != reranker_trace["top1_after"]
        reranker_trace.update(
            {
                "applied": True,
                "candidate_count": len(hybrid_hits),
                "reranked_count": min(len(hybrid_hits), max(top_k, retriever.reranker.top_n)),
                "rebalance_reasons": rebalance_reasons,
            }
        )
        _emit_trace_event(
            trace_callback,
            step="rerank",
            label="리랭킹 완료",
            status="done",
            detail=(
                f"{hits[0].book_slug} · {hits[0].section}"
                if hits
                else "상위 근거 없음"
            ),
            duration_ms=timings_ms["rerank"],
            meta={
                "summary": _summarize_hit_list(hits, score_key="fused_score"),
                "top1_before": reranker_trace["top1_before"],
                "top1_after": reranker_trace["top1_after"],
                "top1_changed": reranker_trace["top1_changed"],
                "rebalance_reasons": reranker_trace["rebalance_reasons"],
            },
        )
    except Exception as exc:  # noqa: BLE001
        reranker_trace["error"] = str(exc)
        _emit_trace_event(
            trace_callback,
            step="rerank",
            label="리랭킹 실패",
            status="error",
            detail=str(exc),
        )
        raise RuntimeError(f"reranker failed: {exc}") from exc
    return hits, reranker_trace
