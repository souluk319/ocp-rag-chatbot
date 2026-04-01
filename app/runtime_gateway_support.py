from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.multiturn_memory import SessionMemoryManager
from app.ocp_policy import OcpPolicyEngine, load_policy_engine
from app.runtime_source_index import SourceCatalog, load_active_source_catalog


def _normalize_text(value: str) -> str:
    return " ".join((value or "").split()).strip().lower()


def _normalize_path(value: str) -> str:
    return value.replace("\\", "/").strip().lower()


def looks_like_definition_query(query: str) -> bool:
    normalized = _normalize_text(query)
    product_terms = (
        "ocp",
        "openshift",
        "open shift",
        "오픈시프트",
        "open shift container platform",
        "openshift container platform",
    )
    definition_cues = (
        "뭐야",
        "무엇",
        "정의",
        "소개",
        "개요",
        "란",
        "what is",
        "overview",
        "introduction",
    )
    if not any(term in normalized for term in product_terms):
        return False
    return any(cue in normalized for cue in definition_cues) or normalized.strip() in {"ocp", "openshift", "오픈시프트"}


def _contains_any(value: str, terms: tuple[str, ...]) -> bool:
    normalized = _normalize_text(value)
    return any(term in normalized for term in terms)


def looks_like_definition_query(query: str) -> bool:
    normalized = _normalize_text(query)
    if not normalized:
        return False
    product_terms = ("ocp", "openshift", "open shift", "오픈시프트")
    definition_cues = ("뭐야", "무엇", "정의", "소개", "개요", "란", "what is", "overview", "introduction")
    return (
        any(term in normalized for term in product_terms)
        and (any(cue in normalized for cue in definition_cues) or normalized in {"ocp", "openshift", "오픈시프트"})
    )


@dataclass(frozen=True)
class RuntimeTurnPlan:
    conversation_id: str
    mode: str
    original_query: str
    rewritten_query: str
    memory_before: dict[str, Any]
    turn_trace: dict[str, Any]


@lru_cache(maxsize=1)
def load_session_manager() -> SessionMemoryManager:
    return SessionMemoryManager()


def snapshot_to_policy_memory(snapshot: dict[str, Any]) -> dict[str, Any]:
    source_dir = str(snapshot.get("source_dir", "")).strip()
    active_category = str(snapshot.get("active_category", "")).strip()
    return {
        "active_source_dirs": [source_dir] if source_dir else [],
        "active_categories": [active_category] if active_category else [],
        "active_version": str(snapshot.get("active_version", "")).strip(),
        "active_document_path": str(snapshot.get("reference_doc_path", "")).strip(),
    }


def prepare_runtime_turn(
    *,
    question_ko: str,
    conversation_id: str,
    mode: str,
    memory_manager: SessionMemoryManager | None = None,
) -> RuntimeTurnPlan:
    manager = memory_manager or load_session_manager()
    snapshot = manager.get_snapshot(conversation_id)
    result = manager.process_turn(
        session_id=conversation_id,
        turn_index=snapshot.turn_count + 1,
        question_ko=question_ko,
        reference_doc_path=snapshot.reference_doc_path,
        reference_source_dir=snapshot.source_dir,
    )
    return RuntimeTurnPlan(
        conversation_id=conversation_id,
        mode=mode,
        original_query=question_ko,
        rewritten_query=str(result["turn"]["rewritten_query"]).strip(),
        memory_before=result["state_before"],
        turn_trace=result,
    )


def build_policy_overlay(
    *,
    question_ko: str,
    mode: str,
    sources: list[dict[str, Any]],
    memory_before: dict[str, Any],
    policy_engine: OcpPolicyEngine | None = None,
    source_catalog: SourceCatalog | None = None,
) -> dict[str, Any]:
    engine = policy_engine or load_policy_engine()
    catalog = source_catalog or load_active_source_catalog()
    memory_state = snapshot_to_policy_memory(memory_before)
    normalized_sources = [
        catalog.normalize_search_result(source, rank=index)
        for index, source in enumerate(sources, start=1)
    ]
    signals = engine.analyze_query(question_ko, mode=mode, memory_state=memory_state)
    prepared_sources, signals = engine.augment_follow_up_candidates(
        question_ko,
        normalized_sources,
        manifest_index=catalog.by_document_path,
        mode=mode,
        memory_state=memory_state,
        signals=signals,
    )
    reranked_sources, signals = engine.rerank_candidates(
        question_ko,
        prepared_sources,
        mode=mode,
        memory_state=memory_state,
        signals=signals,
    )
    answer_contract = engine.build_answer_contract(
        question_ko,
        reranked_sources,
        mode=mode,
        grounded=bool(reranked_sources),
        memory_state=memory_state,
    )
    return {
        "raw_sources": normalized_sources,
        "policy_sources": reranked_sources,
        "policy_signals": signals.to_dict(),
        "answer_contract": answer_contract,
    }


def commit_runtime_grounding(
    *,
    conversation_id: str,
    sources: list[dict[str, Any]],
    memory_manager: SessionMemoryManager | None = None,
) -> dict[str, Any]:
    manager = memory_manager or load_session_manager()
    top_source = sources[0] if sources else {}
    return manager.apply_grounding(
        conversation_id,
        reference_doc_path=str(top_source.get("document_path", "")).strip(),
        source_dir=str(top_source.get("source_dir", "")).strip(),
        category=str(top_source.get("effective_category", "") or top_source.get("category", "")).strip(),
        version=str(top_source.get("version", "")).strip(),
    )


def build_answer_prefix(answer_contract: dict[str, Any]) -> str:
    if not answer_contract.get("grounded", False):
        return "현재 검색된 공식 근거만으로는 답을 확정하기 어렵습니다. 먼저 출처 문서를 직접 확인해 주세요.\n\n"

    signals = answer_contract.get("signals", {})
    lines: list[str] = []
    version_hint = str(signals.get("version_hint", "")).strip()
    if version_hint:
        lines.append(f"[기준 버전: OpenShift {version_hint}]")
    if bool(signals.get("risk_notice_required")):
        lines.append("[주의: 운영 영향이 있는 작업일 수 있으므로 적용 전에 현재 클러스터 버전과 공식 문서를 다시 확인하세요.]")
    if not lines:
        return ""
    return "\n".join(lines) + "\n\n"


def ensure_citation_block(answer: str, citations: list[dict[str, Any]]) -> str:
    if not citations:
        return answer
    if "[Source:" in answer:
        return answer

    lines = [answer.rstrip(), "", build_citation_appendix(citations).strip()]
    return "\n".join(lines).strip()


def build_citation_appendix(citations: list[dict[str, Any]]) -> str:
    lines = ["출처:"]
    for citation in citations[:3]:
        label = str(citation.get("section_title", "")).strip() or str(citation.get("document_path", "")).strip()
        viewer_url = str(citation.get("viewer_url", "")).strip()
        lines.append(f"- {label} ({viewer_url})")
    return "\n".join(lines)


def _read_definition_excerpt(document: dict[str, Any]) -> str:
    normalized_path = str(document.get("normalized_path", "")).strip()
    if not normalized_path:
        return ""
    path = Path(normalized_path)
    if not path.exists() or not path.is_file():
        return ""

    lines: list[str] = []
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("Title:") or line.startswith("Source Path:") or line.startswith("Viewer URL:"):
            continue
        if line.startswith("[Section]"):
            continue
        lines.append(line)
        if len(lines) >= 3:
            break
    excerpt = " ".join(lines)
    if ". " in excerpt:
        excerpt = excerpt.split(". ", 1)[0].strip() + "."
    return excerpt


def _read_runtime_excerpt(document: dict[str, Any]) -> str:
    normalized_path = str(document.get("normalized_path", "")).strip()
    if not normalized_path:
        return ""
    path = Path(normalized_path)
    if not path.exists() or not path.is_file():
        return ""

    lines: list[str] = []
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("Title:") or line.startswith("Source Path:") or line.startswith("Viewer URL:"):
            continue
        if line.startswith("[Section]"):
            continue
        lines.append(line)
        if len(lines) >= 4:
            break

    excerpt = " ".join(lines)
    if ". " in excerpt:
        excerpt = excerpt.split(". ", 1)[0].strip() + "."
    return excerpt


def build_manifest_backed_definition_answer(
    question_ko: str,
    citations: list[dict[str, Any]],
    *,
    source_catalog: SourceCatalog | None = None,
) -> str:
    catalog = source_catalog or load_active_source_catalog()
    normalized_question = _normalize_text(question_ko)
    top_citation = citations[0] if citations else {}
    document = catalog.by_document_path.get(_normalize_path(str(top_citation.get("document_path", ""))), {})
    excerpt = _read_definition_excerpt(document)

    lines: list[str] = []
    if "ocp" in normalized_question:
        lines.append("OCP는 OpenShift Container Platform의 약자입니다.")
    lines.append("OpenShift Container Platform(OCP)는 Red Hat이 제공하는 엔터프라이즈 Kubernetes 플랫폼입니다.")
    lines.append("애플리케이션 배포뿐 아니라 클러스터 설치, 업데이트, 네트워킹, 보안, 모니터링 같은 운영 기능을 공식적으로 제공합니다.")
    if excerpt:
        lines.append(f'공식 문서에서는 "{excerpt}" 라고 설명합니다.')
    return "\n".join(lines)


def looks_like_reference_seeking_query(query: str) -> bool:
    cues = (
        "어떤 문서",
        "무슨 문서",
        "어느 문서",
        "문서를 봐",
        "문서를 먼저",
        "참고해야",
        "참고할 문서",
        "찾아야",
        "무엇을 봐야",
    )
    return _contains_any(query, cues)


def classify_local_rescue_topic(query: str) -> str:
    normalized = _normalize_text(query)
    if looks_like_definition_query(normalized):
        return "definition"
    if (
        ("operatorhub" in normalized or "operator lifecycle manager" in normalized or "olm" in normalized)
        and any(cue in normalized for cue in ("무엇", "뭐야", "역할", "개요", "소개", "what is", "overview"))
    ):
        return "operator_definition"
    if "oc-mirror" in normalized or "미러링" in normalized or "폐쇄망" in normalized:
        return "disconnected"
    if "방화벽" in normalized or "firewall" in normalized:
        return "firewall"
    if "업데이트" in normalized or "update" in normalized:
        return "update"
    return ""


def pick_manifest_backed_reference_sources(
    question_ko: str,
    *,
    source_catalog: SourceCatalog | None = None,
    limit: int = 2,
) -> list[dict[str, Any]]:
    catalog = source_catalog or load_active_source_catalog()
    topic = classify_local_rescue_topic(question_ko)
    if topic == "definition":
        return pick_manifest_backed_definition_sources(source_catalog=catalog, limit=limit)

    preferred_paths_by_topic = {
        "firewall": (
            "installing/install_config/configuring-firewall.adoc",
        ),
        "operator_definition": (
            "operators/index.adoc",
            "operators/olm_v1/index.adoc",
            "operators/understanding/olm-what-operators-are.adoc",
            "operators/understanding/olm/olm-arch.adoc",
        ),
        "update": (
            "updating/index.adoc",
            "updating/preparing_for_updates/updating-cluster-prepare.adoc",
            "updating/preparing_for_updates/preparing-manual-creds-update.adoc",
            "post_installation_configuration/day_2_core_cnf_clusters/updating/update-before-the-update.adoc",
        ),
        "disconnected": (
            "disconnected/about-installing-oc-mirror-v2.adoc",
            "disconnected/updating/index.adoc",
        ),
    }
    preferred_paths = preferred_paths_by_topic.get(topic, ())
    results: list[dict[str, Any]] = []

    for document_path in preferred_paths:
        manifest_doc = catalog.by_document_path.get(document_path)
        if not manifest_doc:
            continue
        sections = manifest_doc.get("sections", []) or []
        top_section = sections[0] if sections else {}
        results.append(
            {
                "rank": len(results) + 1,
                "source_dir": manifest_doc.get("top_level_dir", ""),
                "top_level_dir": manifest_doc.get("top_level_dir", ""),
                "document_path": document_path,
                "viewer_url": manifest_doc.get("viewer_url", ""),
                "section_title": top_section.get("section_title", "") or manifest_doc.get("title", ""),
                "title": manifest_doc.get("title", ""),
                "product": manifest_doc.get("product", ""),
                "version": manifest_doc.get("version", ""),
                "category": manifest_doc.get("category", ""),
                "effective_category": manifest_doc.get("category", ""),
                "trust_level": manifest_doc.get("trust_level", ""),
                "retrieval_origin": "manifest_runtime_rescue",
            }
        )
        if len(results) >= limit:
            break

    return results


def build_manifest_backed_reference_answer(
    question_ko: str,
    citations: list[dict[str, Any]],
    *,
    source_catalog: SourceCatalog | None = None,
) -> str:
    topic = classify_local_rescue_topic(question_ko)
    if topic == "definition":
        return build_manifest_backed_definition_answer(question_ko, citations, source_catalog=source_catalog)

    if topic == "firewall":
        return (
            "공식 문서 기준으로 설치 전 방화벽에서는 OpenShift가 접근해야 하는 외부 레지스트리와 사이트를 먼저 허용해야 합니다.\n"
            "특히 registry.redhat.io, access.redhat.com, registry.access.redhat.com, quay.io 계열은 443 포트 기준 허용이 핵심입니다.\n"
            "정확한 전체 allowlist와 예외는 아래 출처 문서를 바로 확인하세요."
        )

    if topic == "operator_definition":
        return (
            "OperatorHub는 클러스터에 설치할 수 있는 Operator를 찾고 배포하는 진입점이고, "
            "Operator Lifecycle Manager(OLM)는 그 Operator의 설치, 업그레이드, 의존성, 수명주기를 관리하는 구성요소입니다.\n"
            "즉 OperatorHub가 카탈로그와 선택의 화면이라면, OLM은 실제 설치와 운영 흐름을 담당한다고 보면 됩니다."
        )

    if topic == "update":
        return (
            "업데이트 전에는 현재 버전과 업그레이드 경로, 자격 증명 관리 방식, 그리고 사전 준비 항목을 먼저 확인해야 합니다.\n"
            "아래 공식 문서를 먼저 확인하면 업데이트 개요와 사전 준비 문서를 바로 따라갈 수 있습니다."
        )

    if topic == "disconnected":
        return (
            "폐쇄망 설치에서 oc-mirror 플러그인으로 이미지를 미러링하려면 먼저 oc-mirror v2 공식 문서를 확인하는 것이 맞습니다.\n"
            "아래 출처 문서가 워크플로, 전제 조건, 그리고 mirror-to-disk / disk-to-mirror 흐름을 직접 설명합니다."
        )

    return ""


def should_use_local_runtime_rescue(question_ko: str) -> bool:
    topic = classify_local_rescue_topic(question_ko)
    if topic == "definition":
        return True
    if topic in {"firewall", "update", "disconnected", "operator_definition"}:
        return True
    return looks_like_reference_seeking_query(question_ko)


def answer_needs_source_backed_rescue(answer: str, citations: list[dict[str, Any]]) -> bool:
    if not citations:
        return False
    normalized = _normalize_text(answer)
    if not normalized:
        return True

    weak_markers = (
        "[unverified]",
        "no relevant documentation found",
        "provided context does not contain enough information",
        "cannot provide specific",
        "cannot answer",
        "missing information",
        "관련 문맥을 찾지 못했습니다",
        "검색된 공식 근거만으로는 답을 확정하기 어렵습니다",
    )
    if any(marker in normalized for marker in weak_markers):
        return True

    has_hangul = any("\uac00" <= char <= "\ud7a3" for char in answer)
    has_source_summary = "질문과 가장 가까운 공식 문서" in answer
    if not has_hangul and not has_source_summary:
        return True
    return False


def build_source_backed_runtime_answer(
    question_ko: str,
    citations: list[dict[str, Any]],
    *,
    source_catalog: SourceCatalog | None = None,
) -> str:
    catalog = source_catalog or load_active_source_catalog()
    top_citation = citations[0] if citations else {}
    next_citation = citations[1] if len(citations) > 1 else {}
    document = catalog.by_document_path.get(_normalize_path(str(top_citation.get("document_path", ""))), {})
    excerpt = _read_runtime_excerpt(document)

    top_section = str(top_citation.get("section_title", "")).strip() or str(top_citation.get("title", "")).strip()
    next_section = str(next_citation.get("section_title", "")).strip() or str(next_citation.get("title", "")).strip()

    lines = [
        f'질문과 가장 가까운 공식 문서는 "{top_section or "관련 문서"}" 입니다.',
    ]
    if excerpt:
        lines.append(f'문서 요약: "{excerpt}"')
    else:
        lines.append("현재 검색된 공식 문서를 기준으로 먼저 아래 출처를 확인하는 것이 가장 안전합니다.")
    if next_section:
        lines.append(f'함께 보면 좋은 문서는 "{next_section}" 입니다.')
    lines.append("아래 출처를 눌러 HTML 원문을 바로 확인하세요.")
    return "\n".join(lines)


def pick_manifest_backed_definition_sources(
    *,
    source_catalog: SourceCatalog | None = None,
    limit: int = 2,
) -> list[dict[str, Any]]:
    catalog = source_catalog or load_active_source_catalog()
    preferred_paths = (
        "architecture/index.adoc",
        "architecture/architecture.adoc",
    )
    results: list[dict[str, Any]] = []

    for document_path in preferred_paths:
        manifest_doc = catalog.by_document_path.get(document_path)
        if not manifest_doc:
            continue
        sections = manifest_doc.get("sections", []) or []
        top_section = sections[0] if sections else {}
        results.append(
            {
                "rank": len(results) + 1,
                "source_dir": manifest_doc.get("top_level_dir", ""),
                "top_level_dir": manifest_doc.get("top_level_dir", ""),
                "document_path": document_path,
                "viewer_url": manifest_doc.get("viewer_url", ""),
                "section_title": top_section.get("section_title", "") or manifest_doc.get("title", ""),
                "title": manifest_doc.get("title", ""),
                "product": manifest_doc.get("product", ""),
                "version": manifest_doc.get("version", ""),
                "category": manifest_doc.get("category", ""),
                "effective_category": manifest_doc.get("category", ""),
                "trust_level": manifest_doc.get("trust_level", ""),
                "retrieval_origin": "definition_fallback",
            }
        )
        if len(results) >= limit:
            break

    return results


def shape_answer(answer: str, answer_contract: dict[str, Any], citations: list[dict[str, Any]]) -> str:
    prefix = build_answer_prefix(answer_contract)
    combined = f"{prefix}{answer}".strip()
    return ensure_citation_block(combined, citations)


def answer_requires_prefix(existing_text: str, answer_contract: dict[str, Any]) -> bool:
    prefix = build_answer_prefix(answer_contract).strip()
    if not prefix:
        return False
    return _normalize_text(prefix) not in _normalize_text(existing_text)


def build_done_payload(done_payload: dict[str, Any], *, conversation_id: str, mode: str, rewritten_query: str) -> dict[str, Any]:
    payload = dict(done_payload)
    payload["conversationId"] = conversation_id
    payload["mode"] = mode
    payload["rewrittenQuery"] = rewritten_query
    return payload


def _short_source_label(source: dict[str, Any]) -> str:
    return (
        str(source.get("section_title", "")).strip()
        or str(source.get("title", "")).strip()
        or str(source.get("document_path", "")).strip()
        or "-"
    )


def build_pipeline_trace(
    *,
    query: str,
    mode: str,
    route: str,
    rewritten_query: str,
    turn_trace: dict[str, Any],
    raw_sources: list[dict[str, Any]] | None = None,
    policy_sources: list[dict[str, Any]] | None = None,
    policy_signals: dict[str, Any] | None = None,
    local_rescue_topic: str = "",
    upstream_used: bool = False,
    answer_contract: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    raw_sources = raw_sources or []
    policy_sources = policy_sources or []
    policy_signals = policy_signals or {}
    answer_contract = answer_contract or {}
    turn = turn_trace.get("turn", {}) if isinstance(turn_trace, dict) else {}
    state_before = turn_trace.get("state_before", {}) if isinstance(turn_trace, dict) else {}

    matched_rules = [str(item).strip() for item in policy_signals.get("matched_rules", []) if str(item).strip()]
    preferred_dirs = [str(item).strip() for item in policy_signals.get("preferred_source_dirs", []) if str(item).strip()]
    first_policy_viewer = str(policy_sources[0].get("viewer_url", "")).strip() if policy_sources else ""
    first_policy_doc = _short_source_label(policy_sources[0]) if policy_sources else "-"
    prefix_applied = bool(build_answer_prefix(answer_contract).strip())

    trace: list[dict[str, Any]] = [
        {
            "step": 1,
            "title": "질문 수신",
            "summary": "사용자 질문을 수신했습니다.",
            "detail": f"mode={mode} | query={query}",
        },
        {
            "step": 2,
            "title": "세션/멀티턴 메모리",
            "summary": "현재 세션 문맥을 읽고 질문 유형을 분류했습니다.",
            "detail": (
                f"classification={turn.get('classification', '-')} | "
                f"active_topic={turn.get('active_topic', '-') or '-'} | "
                f"prev_source_dir={state_before.get('source_dir', '-') or '-'}"
            ),
        },
        {
            "step": 3,
            "title": "질문 재작성",
            "summary": "검색용 질의를 준비했습니다.",
            "detail": rewritten_query if rewritten_query else query,
        },
        {
            "step": 4,
            "title": "경로 선택",
            "summary": "이번 답변에 사용할 파이프라인 경로를 선택했습니다.",
            "detail": (
                f"route={route}"
                + (f" | rescue_topic={local_rescue_topic}" if local_rescue_topic else "")
                + (f" | upstream_used={str(upstream_used).lower()}")
            ),
        },
    ]

    if upstream_used:
        trace.append(
            {
                "step": len(trace) + 1,
                "title": "OpenDocuments 검색",
                "summary": "OpenDocuments 기준 검색 결과를 수집했습니다.",
                "detail": f"raw_source_count={len(raw_sources)}",
            }
        )

    trace.append(
        {
            "step": len(trace) + 1,
            "title": "정책 정렬",
            "summary": "질문 규칙과 문맥을 반영해 출처 후보를 정렬했습니다.",
            "detail": (
                f"matched_rules={', '.join(matched_rules) if matched_rules else '-'} | "
                f"preferred_dirs={', '.join(preferred_dirs) if preferred_dirs else '-'} | "
                f"policy_source_count={len(policy_sources)}"
            ),
        }
    )

    if route in {"manifest_runtime_rescue", "manifest_definition", "source_backed_runtime_rescue"}:
        trace.append(
            {
                "step": len(trace) + 1,
                "title": "로컬 안전장치 적용",
                "summary": "현재 질문군에 맞는 manifest-backed 경로를 적용했습니다.",
                "detail": (
                    f"route={route}"
                    + (f" | topic={local_rescue_topic}" if local_rescue_topic else "")
                    + f" | selected_source={first_policy_doc}"
                ),
            }
        )

    trace.append(
        {
            "step": len(trace) + 1,
            "title": "답변 조합",
            "summary": "응답 본문, 안내 문구, citation을 결합했습니다.",
            "detail": (
                f"prefix_applied={str(prefix_applied).lower()} | "
                f"citation_count={len(policy_sources)}"
            ),
        }
    )

    trace.append(
        {
            "step": len(trace) + 1,
            "title": "출처 연결",
            "summary": "클릭 가능한 HTML citation을 연결했습니다.",
            "detail": f"viewer={first_policy_viewer or '-'}",
        }
    )
    return trace
