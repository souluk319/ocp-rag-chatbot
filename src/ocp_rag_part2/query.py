from __future__ import annotations

import re

from .models import SessionContext


HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
SPACE_RE = re.compile(r"\s+")
VERSION_RE = re.compile(r"(?<!\d)4\.(\d+)(?!\d)")
OCP_RE = re.compile(r"(?<![a-z0-9])ocp(?![a-z0-9])", re.IGNORECASE)
OPENSHIFT_RE = re.compile(r"(오픈시프트|openshift)", re.IGNORECASE)
KUBERNETES_RE = re.compile(r"(쿠버네티스|kubernetes)", re.IGNORECASE)
COMPARE_RE = re.compile(r"(차이|다른 점|비교|vs|versus|유사점)", re.IGNORECASE)
ARCHITECTURE_RE = re.compile(r"(아키텍처|architecture)", re.IGNORECASE)
LOGGING_RE = re.compile(r"(로그|로깅|logging)", re.IGNORECASE)
AUDIT_RE = re.compile(r"(감사|audit)", re.IGNORECASE)
EVENT_RE = re.compile(r"(이벤트|event)", re.IGNORECASE)
APP_RE = re.compile(r"(애플리케이션|application|pod|컨테이너|container)", re.IGNORECASE)
POD_PENDING_RE = re.compile(r"(pod|파드).*(pending|펜딩)|(pending|펜딩)", re.IGNORECASE)
CRASH_LOOP_RE = re.compile(r"(crashloopbackoff|crash loop backoff|크래시루프백오프)", re.IGNORECASE)
POD_LIFECYCLE_RE = re.compile(
    r"(pod lifecycle|pod 라이프사이클|파드 라이프사이클|pod 생명주기|파드 생명주기|lifecycle)",
    re.IGNORECASE,
)
OC_LOGIN_RE = re.compile(r"\boc\s+login\b|(로그인).*(\boc\b)", re.IGNORECASE)
INFRA_RE = re.compile(r"(인프라|infra|노드|node|컨트롤 플레인|control plane)", re.IGNORECASE)
MONITORING_RE = re.compile(r"(모니터링|monitoring)", re.IGNORECASE)
SECURITY_RE = re.compile(r"(보안|security)", re.IGNORECASE)
AUTH_RE = re.compile(r"(인증|authentication)", re.IGNORECASE)
AUTHZ_RE = re.compile(r"(권한|authorization)", re.IGNORECASE)
UPDATE_RE = re.compile(r"(업데이트|upgrade|update|업그레이드)", re.IGNORECASE)
CERT_RE = re.compile(r"(인증서|certificate|certificates|cert)", re.IGNORECASE)
EXPIRY_RE = re.compile(r"(만료|만료일|만료 상태|expire|expiry|expiration|남았)", re.IGNORECASE)
RBAC_RE = re.compile(
    r"(\brbac\b|역할 기반 액세스 제어|rolebinding|clusterrolebinding|clusterrole|역할 바인딩|role binding)",
    re.IGNORECASE,
)
PROJECT_SCOPE_RE = re.compile(r"(프로젝트|project|네임스페이스|namespace)", re.IGNORECASE)
ROLE_ASSIGN_RE = re.compile(
    r"(주고 싶|주려|부여|할당|추가|설정|바인딩|묶|grant|assign|bind)",
    re.IGNORECASE,
)
ROLE_API_STYLE_RE = re.compile(r"(api|yaml|manifest|json|spec|필드|curl)", re.IGNORECASE)
USER_SUBJECT_RE = re.compile(r"(사용자|유저|작업자|계정|그룹|serviceaccount|서비스 계정)", re.IGNORECASE)
ADMIN_ROLE_RE = re.compile(r"(관리자|\badmin\b)", re.IGNORECASE)
EDIT_ROLE_RE = re.compile(r"(편집|\bedit\b)", re.IGNORECASE)
VIEW_ROLE_RE = re.compile(r"(읽기 전용|보기|\bview\b)", re.IGNORECASE)
CLUSTER_ADMIN_RE = re.compile(r"\bcluster-admin\b", re.IGNORECASE)
MCO_RE = re.compile(
    r"(machine config operator|mco(?:가|는|를|란|와|과)?|머신\s*컨피그\s*오퍼레이터|머신\s*구성\s*오퍼레이터)",
    re.IGNORECASE,
)
DISCONNECTED_RE = re.compile(r"(연결이 없는 환경|분리망|disconnect)", re.IGNORECASE)
ETCD_RE = re.compile(r"etcd", re.IGNORECASE)
BACKUP_RE = re.compile(r"(백업|backup)", re.IGNORECASE)
RESTORE_RE = re.compile(r"(복구|복원|restore)", re.IGNORECASE)
NODE_RE = re.compile(r"(노드|node|worker)", re.IGNORECASE)
DRAIN_RE = re.compile(r"(drain|비워|비우|evacuate|점검 때문에 비워)", re.IGNORECASE)
TOP_RE = re.compile(r"(\btop\b|사용량|cpu|메모리|memory)", re.IGNORECASE)
HOSTED_CONTROL_PLANE_RE = re.compile(
    r"(hosted control plane|hosted cluster|호스팅된 컨트롤 플레인|호스트된 컨트롤 플레인|hypershift|oadp|velero)",
    re.IGNORECASE,
)
PROJECT_TERMINATING_RE = re.compile(
    r"(프로젝트|project|namespace|네임스페이스).*(삭제|지웠|지우|terminating|종료 중|안 없어|안 없어지|안 지워|안 지워지)",
    re.IGNORECASE,
)
FINALIZER_RE = re.compile(
    r"(finalizer|finalizers|metadata\.finalizers|강제 제거|강제로 제거|finalizer 제거)",
    re.IGNORECASE,
)
REMAINING_RESOURCE_RE = re.compile(
    r"(걸려 있는 리소스|남아 있는 리소스|remaining resource|resource resolving|error resolving resource|crd|custom resource|리소스 에러)",
    re.IGNORECASE,
)
OPERATOR_RE = re.compile(
    r"(오퍼레이터|operator(?:가|는|를|란|와|과)?|\boperator\b)",
    re.IGNORECASE,
)
DOC_LOCATOR_RE = re.compile(
    r"(문서|가이드|어디서|어디 있어|어디를|찾아|찾을|봐야|보려면|보고 싶|참고할)",
    re.IGNORECASE,
)
EXPLAINER_RE = re.compile(
    r"(설명해줘|설명해 줘|처음 설명|개념 설명|뭐야\??|무엇인가\??|무슨 역할|왜 중요|차이가 뭐야\??|역할이 뭐야\??|요약해줘|요약해 줘|요약해봐|요약해 봐|정리해줘|정리해 줘|세줄|3줄|한줄|짧게)",
    re.IGNORECASE,
)
GENERIC_INTRO_RE = re.compile(
    r"(오픈시프트|openshift).*(뭐야|무엇|소개|개요|아키텍처|architecture)|"
    r"(오픈시프트|openshift).*(요약|정리|세줄|3줄|한줄|짧게)|"
    r"(쿠버네티스|kubernetes).*(오픈시프트|openshift).*(차이|다른 점)",
    re.IGNORECASE,
)
COMPARE_DECOMPOSE_RE = re.compile(
    r"(?P<left>.+?)(?:\s*(?:vs\.?|versus|와|과|랑)\s*)(?P<right>.+?)(?:\s*(?:의)?\s*(?:차이|차이점|비교|다른 점).*)$",
    re.IGNORECASE,
)
CONJUNCTION_SPLIT_RE = re.compile(r"\s*(?:그리고|또한|및|and then|and also|and)\s*", re.IGNORECASE)
FOLLOW_UP_HINTS = (
    "그거",
    "그걸",
    "그건",
    "그게",
    "저거",
    "그 설정",
    "그 문서",
    "그 내용",
    "거기서",
    "그 상태에서",
    "안 되는데",
    "안되는데",
    "걸려",
    "남아",
    "아까",
    "이전",
    "해당",
    "1번",
    "2번",
    "3번",
)
UNSUPPORTED_PRODUCTS = (
    "argo cd",
    "argocd",
    "harbor",
    "eks",
    "aks",
    "gke",
    "anthos",
    "rancher",
)
UNSUPPORTED_INTENT_RE = re.compile(
    r"(설치|install|비교|compare|가격|요금|cost|비용|방법|어떻게)",
    re.IGNORECASE,
)


def contains_hangul(text: str) -> bool:
    return bool(HANGUL_RE.search(text or ""))


def _collapse_spaces(text: str) -> str:
    return SPACE_RE.sub(" ", (text or "")).strip()


def _append_terms(base_query: str, terms: list[str]) -> str:
    seen: set[str] = set()
    ordered: list[str] = []

    for token in _collapse_spaces(base_query).split():
        lowered = token.lower()
        if lowered not in seen:
            seen.add(lowered)
            ordered.append(token)

    for term in terms:
        for token in _collapse_spaces(term).split():
            lowered = token.lower()
            if lowered not in seen:
                seen.add(lowered)
                ordered.append(token)

    return " ".join(ordered).strip()


def _dedupe_queries(queries: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for query in queries:
        cleaned = _collapse_spaces(query)
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(cleaned)
    return unique


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = (text or "").lower()
    return any(keyword in lowered for keyword in keywords)


def has_doc_locator_intent(query: str) -> bool:
    return bool(DOC_LOCATOR_RE.search(query or ""))


def has_pod_pending_troubleshooting_intent(query: str) -> bool:
    return bool(POD_PENDING_RE.search(query or ""))


def has_backup_restore_intent(query: str) -> bool:
    return bool(BACKUP_RE.search(query or "") or RESTORE_RE.search(query or ""))


def has_hosted_control_plane_signal(query: str) -> bool:
    return bool(HOSTED_CONTROL_PLANE_RE.search(query or ""))


def has_certificate_monitor_intent(query: str) -> bool:
    normalized = query or ""
    return bool(CERT_RE.search(normalized)) and bool(
        EXPIRY_RE.search(normalized)
        or "확인" in normalized
        or "조회" in normalized
        or "모니터" in normalized
        or "monitor" in normalized.lower()
    )


def has_rbac_intent(query: str) -> bool:
    normalized = query or ""
    if RBAC_RE.search(normalized):
        return True
    return bool(AUTHZ_RE.search(normalized)) and bool(
        PROJECT_SCOPE_RE.search(normalized)
        or ROLE_ASSIGN_RE.search(normalized)
        or ADMIN_ROLE_RE.search(normalized)
        or EDIT_ROLE_RE.search(normalized)
        or VIEW_ROLE_RE.search(normalized)
        or CLUSTER_ADMIN_RE.search(normalized)
    )


def has_project_scoped_rbac_intent(query: str) -> bool:
    normalized = query or ""
    return has_rbac_intent(normalized) and bool(PROJECT_SCOPE_RE.search(normalized))


def has_rbac_assignment_intent(query: str) -> bool:
    normalized = query or ""
    return has_rbac_intent(normalized) and bool(
        ROLE_ASSIGN_RE.search(normalized)
        or USER_SUBJECT_RE.search(normalized)
        or ADMIN_ROLE_RE.search(normalized)
        or EDIT_ROLE_RE.search(normalized)
        or VIEW_ROLE_RE.search(normalized)
        or CLUSTER_ADMIN_RE.search(normalized)
    )


def is_generic_intro_query(query: str) -> bool:
    lowered = (query or "").lower()
    if GENERIC_INTRO_RE.search(query or ""):
        return True
    has_ocp_topic = "openshift" in lowered or bool(OCP_RE.search(query or ""))
    return has_ocp_topic and bool(
        ARCHITECTURE_RE.search(query or "") or EXPLAINER_RE.search(query or "")
    )


def has_openshift_kubernetes_compare_intent(query: str) -> bool:
    normalized = query or ""
    return bool(OPENSHIFT_RE.search(normalized)) and bool(KUBERNETES_RE.search(normalized)) and bool(
        COMPARE_RE.search(normalized) or "차이를" in normalized or "차이점" in normalized
    )


def is_explainer_query(query: str) -> bool:
    return bool(EXPLAINER_RE.search(query or ""))


def has_pod_lifecycle_concept_intent(query: str) -> bool:
    normalized = query or ""
    return bool(POD_LIFECYCLE_RE.search(normalized)) and bool(is_explainer_query(normalized))


def has_crash_loop_troubleshooting_intent(query: str) -> bool:
    return bool(CRASH_LOOP_RE.search(query or ""))


def has_operator_concept_intent(query: str) -> bool:
    normalized = query or ""
    return (
        bool(OPERATOR_RE.search(normalized))
        and not bool(MCO_RE.search(normalized))
        and bool(
            is_explainer_query(normalized)
            or "뭐 하는" in normalized
            or "하는 거야" in normalized
            or "어떤 역할" in normalized
            or "왜 필요" in normalized
            or "왜 중요한" in normalized
            or "예시" in normalized
            or "누가 관리" in normalized
        )
    )


def has_mco_concept_intent(query: str) -> bool:
    normalized = query or ""
    return bool(MCO_RE.search(normalized)) and bool(
        is_explainer_query(normalized)
        or "뭐 하는" in normalized
        or "하는 거야" in normalized
        or "어떤 역할" in normalized
        or "누가 관리" in normalized
        or "건드리면" in normalized
        or "관리해" in normalized
    )


def has_project_terminating_intent(query: str) -> bool:
    normalized = query or ""
    return bool(PROJECT_TERMINATING_RE.search(normalized))


def has_project_finalizer_intent(query: str) -> bool:
    normalized = query or ""
    return bool(FINALIZER_RE.search(normalized)) or (
        has_project_terminating_intent(normalized)
        and bool(REMAINING_RESOURCE_RE.search(normalized))
    )


def has_logging_ambiguity(query: str) -> bool:
    normalized = query or ""
    if not LOGGING_RE.search(normalized):
        return False
    if AUDIT_RE.search(normalized) or EVENT_RE.search(normalized):
        return False
    if APP_RE.search(normalized) or INFRA_RE.search(normalized):
        return False
    return "어디서" in normalized or "보" in normalized


def has_update_doc_locator_ambiguity(query: str) -> bool:
    normalized = query or ""
    if not UPDATE_RE.search(normalized):
        return False
    if not has_doc_locator_intent(normalized):
        return False
    has_scope = any(
        token in normalized.lower()
        for token in ("4.20", "4.21", "eus", "단일", "단일 노드", "hypershift", "rosa", "microshift")
    )
    return not has_scope


def has_node_drain_intent(query: str) -> bool:
    normalized = query or ""
    return bool(NODE_RE.search(normalized)) and bool(DRAIN_RE.search(normalized))


def has_cluster_node_usage_intent(query: str) -> bool:
    normalized = query or ""
    return bool(NODE_RE.search(normalized)) and bool(TOP_RE.search(normalized))


def decompose_retrieval_queries(query: str) -> list[str]:
    normalized = _collapse_spaces(query)
    if not normalized:
        return []

    if POD_LIFECYCLE_RE.search(normalized) and is_explainer_query(normalized):
        return _dedupe_queries(
            [
                normalized,
                "Pod 정의와 Pod phase 개념",
                "Pod status와 phase 차이",
                "파드 생명주기 개념",
            ]
        )

    compare_match = COMPARE_DECOMPOSE_RE.match(normalized)
    if compare_match:
        left = _collapse_spaces(compare_match.group("left"))
        right = _collapse_spaces(compare_match.group("right"))
        return _dedupe_queries(
            [
                normalized,
                f"{left} 개요",
                f"{right} 개요",
            ]
        )

    question_parts = [
        _collapse_spaces(part)
        for part in re.split(r"\?\s*", normalized)
        if _collapse_spaces(part)
    ]
    if len(question_parts) > 1:
        return _dedupe_queries([normalized, *question_parts])

    if "그리고" in normalized or re.search(r"\band\b", normalized, re.IGNORECASE):
        parts = [
            _collapse_spaces(part)
            for part in CONJUNCTION_SPLIT_RE.split(normalized)
            if _collapse_spaces(part)
        ]
        substantial_parts = [part for part in parts if len(part) >= 6]
        if len(substantial_parts) >= 2:
            return _dedupe_queries([normalized, *substantial_parts[:2]])

    return [normalized]


def detect_unsupported_product(query: str) -> str | None:
    lowered = (query or "").lower()
    if OPENSHIFT_RE.search(query or "") or OCP_RE.search(lowered):
        return None
    if not UNSUPPORTED_INTENT_RE.search(query or ""):
        return None
    for product in UNSUPPORTED_PRODUCTS:
        if product in lowered:
            return product
    return None


def detect_out_of_corpus_version(query: str, *, corpus_version: str = "4.20") -> str | None:
    normalized = query or ""
    if not (OPENSHIFT_RE.search(normalized) or OCP_RE.search(normalized)):
        return None
    corpus_match = VERSION_RE.search(corpus_version)
    corpus_minor = corpus_match.group(1) if corpus_match else "20"
    for match in VERSION_RE.finditer(normalized):
        if match.group(1) != corpus_minor:
            return f"4.{match.group(1)}"
    return None


def query_book_adjustments(
    query: str,
    *,
    context: SessionContext | None = None,
) -> tuple[dict[str, float], dict[str, float]]:
    normalized = _collapse_spaces(query)
    boosts: dict[str, float] = {}
    penalties: dict[str, float] = {}
    context = context or SessionContext()
    context_text = _collapse_spaces(
        " ".join(
            [
                context.current_topic or "",
                *context.open_entities,
                context.unresolved_question or "",
            ]
        )
    )
    rbac_intent = has_rbac_intent(normalized)
    project_scoped_rbac = has_project_scoped_rbac_intent(normalized)
    rbac_assignment = has_rbac_assignment_intent(normalized)
    prefers_rbac_api_docs = bool(ROLE_API_STYLE_RE.search(normalized))

    if is_generic_intro_query(normalized):
        boosts["architecture"] = 1.35
        boosts["overview"] = 1.18
        penalties["tutorials"] = 0.62
        penalties["cli_tools"] = 0.64
        penalties["support"] = 0.72
        penalties["networking_overview"] = 0.68
        penalties["observability_overview"] = 0.8
        penalties["api_overview"] = 0.78
        penalties["project_apis"] = 0.82

    if has_openshift_kubernetes_compare_intent(normalized):
        boosts["architecture"] = max(boosts.get("architecture", 1.0), 1.28)
        boosts["overview"] = max(boosts.get("overview", 1.0), 1.24)
        boosts["security_and_compliance"] = max(
            boosts.get("security_and_compliance", 1.0),
            1.2,
        )
        penalties["tutorials"] = min(penalties.get("tutorials", 1.0), 0.65)
        penalties["cli_tools"] = min(penalties.get("cli_tools", 1.0), 0.7)
        penalties["support"] = min(penalties.get("support", 1.0), 0.72)
        penalties["postinstallation_configuration"] = min(
            penalties.get("postinstallation_configuration", 1.0),
            0.72,
        )

    if has_doc_locator_intent(normalized):
        boosts["web_console"] = 1.35 if "콘솔" in normalized else boosts.get("web_console", 1.0)
        if "문제 해결" in normalized or "트러블슈팅" in normalized:
            boosts["validation_and_troubleshooting"] = 1.35
            boosts["support"] = 1.2
        if "보안" in normalized or "컴플라이언스" in normalized:
            boosts["security_and_compliance"] = 1.35
            penalties["security_apis"] = 0.78
        if has_backup_restore_intent(normalized):
            boosts["backup_and_restore"] = 1.55
            boosts["etcd"] = max(boosts.get("etcd", 1.0), 1.1)
            boosts["postinstallation_configuration"] = max(
                boosts.get("postinstallation_configuration", 1.0),
                1.2,
            )
            if not has_hosted_control_plane_signal(normalized):
                penalties["hosted_control_planes"] = min(
                    penalties.get("hosted_control_planes", 1.0),
                    0.35,
                )

    if ETCD_RE.search(normalized):
        if has_backup_restore_intent(normalized):
            boosts["etcd"] = max(boosts.get("etcd", 1.0), 1.25)
            boosts["backup_and_restore"] = max(boosts.get("backup_and_restore", 1.0), 1.12)
            boosts["postinstallation_configuration"] = max(
                boosts.get("postinstallation_configuration", 1.0),
                1.75,
            )
            if not has_hosted_control_plane_signal(normalized):
                penalties["hosted_control_planes"] = min(
                    penalties.get("hosted_control_planes", 1.0),
                    0.28,
                )
                penalties["edge_computing"] = min(
                    penalties.get("edge_computing", 1.0),
                    0.72,
                )
        elif is_explainer_query(normalized) or "중요" in normalized or "역할" in normalized:
            boosts["etcd"] = max(boosts.get("etcd", 1.0), 1.4)
            boosts["architecture"] = max(boosts.get("architecture", 1.0), 1.08)
            penalties["backup_and_restore"] = 0.62

    if "machine config operator" in normalized.lower():
        boosts["machine_configuration"] = max(boosts.get("machine_configuration", 1.0), 1.3)
        boosts["operators"] = max(boosts.get("operators", 1.0), 1.15)
        penalties["machine_apis"] = 0.76

    if has_operator_concept_intent(normalized):
        boosts["architecture"] = max(boosts.get("architecture", 1.0), 1.32)
        boosts["extensions"] = max(boosts.get("extensions", 1.0), 1.28)
        boosts["operators"] = max(boosts.get("operators", 1.0), 1.22)
        boosts["overview"] = max(boosts.get("overview", 1.0), 1.08)
        penalties["support"] = min(penalties.get("support", 1.0), 0.58)
        penalties["web_console"] = min(penalties.get("web_console", 1.0), 0.62)
        penalties["release_notes"] = min(penalties.get("release_notes", 1.0), 0.7)
        penalties["edge_computing"] = min(penalties.get("edge_computing", 1.0), 0.78)

    if has_mco_concept_intent(normalized) or MCO_RE.search(context_text):
        boosts["architecture"] = max(boosts.get("architecture", 1.0), 1.38)
        boosts["machine_configuration"] = max(boosts.get("machine_configuration", 1.0), 1.55)
        boosts["operators"] = max(boosts.get("operators", 1.0), 1.18)
        boosts["extensions"] = max(boosts.get("extensions", 1.0), 1.1)
        penalties["support"] = min(penalties.get("support", 1.0), 0.54)
        penalties["release_notes"] = min(penalties.get("release_notes", 1.0), 0.58)
        penalties["edge_computing"] = min(penalties.get("edge_computing", 1.0), 0.72)
        penalties["security_and_compliance"] = min(
            penalties.get("security_and_compliance", 1.0),
            0.74,
        )
        penalties["machine_apis"] = min(penalties.get("machine_apis", 1.0), 0.55)
        penalties["windows_container_support_for_openshift"] = min(
            penalties.get("windows_container_support_for_openshift", 1.0),
            0.8,
        )

    if has_project_terminating_intent(normalized):
        boosts["building_applications"] = max(boosts.get("building_applications", 1.0), 1.16)
        boosts["support"] = max(boosts.get("support", 1.0), 1.32)
        penalties["cli_tools"] = min(penalties.get("cli_tools", 1.0), 0.6)

    if has_project_finalizer_intent(normalized):
        boosts["support"] = max(boosts.get("support", 1.0), 1.52)
        penalties["building_applications"] = min(
            penalties.get("building_applications", 1.0),
            0.88,
        )
        penalties["cli_tools"] = min(penalties.get("cli_tools", 1.0), 0.45)

    if has_node_drain_intent(normalized):
        boosts["nodes"] = max(boosts.get("nodes", 1.0), 1.45)
        boosts["support"] = max(boosts.get("support", 1.0), 1.18)
        penalties["updating_clusters"] = min(
            penalties.get("updating_clusters", 1.0),
            0.62,
        )
        penalties["installation_overview"] = min(
            penalties.get("installation_overview", 1.0),
            0.74,
        )
        penalties["cli_tools"] = min(penalties.get("cli_tools", 1.0), 0.76)

    if has_cluster_node_usage_intent(normalized):
        boosts["support"] = max(boosts.get("support", 1.0), 1.5)
        boosts["nodes"] = max(boosts.get("nodes", 1.0), 1.18)
        penalties["cli_tools"] = min(penalties.get("cli_tools", 1.0), 0.8)

    if has_pod_pending_troubleshooting_intent(normalized) or has_crash_loop_troubleshooting_intent(normalized):
        boosts["support"] = max(boosts.get("support", 1.0), 1.45)
        boosts["validation_and_troubleshooting"] = max(
            boosts.get("validation_and_troubleshooting", 1.0),
            1.22,
        )
        boosts["nodes"] = max(boosts.get("nodes", 1.0), 1.12)
        penalties["workloads_apis"] = min(penalties.get("workloads_apis", 1.0), 0.58)
        penalties["monitoring_apis"] = min(penalties.get("monitoring_apis", 1.0), 0.74)
        penalties["schedule_and_quota_apis"] = min(
            penalties.get("schedule_and_quota_apis", 1.0),
            0.76,
        )
        penalties["storage_apis"] = min(penalties.get("storage_apis", 1.0), 0.78)

    if has_crash_loop_troubleshooting_intent(normalized):
        boosts["support"] = max(boosts.get("support", 1.0), 1.58)
        boosts["validation_and_troubleshooting"] = max(
            boosts.get("validation_and_troubleshooting", 1.0),
            1.26,
        )
        boosts["building_applications"] = max(
            boosts.get("building_applications", 1.0),
            1.14,
        )
        boosts["nodes"] = max(boosts.get("nodes", 1.0), 1.12)
        penalties["security_and_compliance"] = min(
            penalties.get("security_and_compliance", 1.0),
            0.74,
        )
        penalties["monitoring_apis"] = min(
            penalties.get("monitoring_apis", 1.0),
            0.52,
        )
        penalties["network_apis"] = min(
            penalties.get("network_apis", 1.0),
            0.58,
        )
        penalties["installation_overview"] = min(
            penalties.get("installation_overview", 1.0),
            0.66,
        )
        penalties["specialized_hardware_and_driver_enablement"] = min(
            penalties.get("specialized_hardware_and_driver_enablement", 1.0),
            0.72,
        )
        penalties["hosted_control_planes"] = min(
            penalties.get("hosted_control_planes", 1.0),
            0.62,
        )

    if has_pod_lifecycle_concept_intent(normalized):
        boosts["architecture"] = max(boosts.get("architecture", 1.0), 1.52)
        boosts["overview"] = max(boosts.get("overview", 1.0), 1.18)
        boosts["building_applications"] = max(
            boosts.get("building_applications", 1.0),
            1.08,
        )
        penalties["workloads_apis"] = min(penalties.get("workloads_apis", 1.0), 0.54)
        penalties["nodes"] = min(penalties.get("nodes", 1.0), 0.78)
        penalties["security_and_compliance"] = min(
            penalties.get("security_and_compliance", 1.0),
            0.64,
        )
        penalties["installation_overview"] = min(
            penalties.get("installation_overview", 1.0),
            0.58,
        )

    if has_backup_restore_intent(normalized) and ETCD_RE.search(context_text) and not ETCD_RE.search(normalized):
        boosts["postinstallation_configuration"] = max(
            boosts.get("postinstallation_configuration", 1.0),
            1.6,
        )
        boosts["etcd"] = max(boosts.get("etcd", 1.0), 1.2)
        if not has_hosted_control_plane_signal(normalized):
            penalties["hosted_control_planes"] = min(
                penalties.get("hosted_control_planes", 1.0),
                0.25,
            )

    if rbac_intent:
        boosts["authentication_and_authorization"] = max(
            boosts.get("authentication_and_authorization", 1.0),
            1.42,
        )
        boosts["security_and_compliance"] = max(
            boosts.get("security_and_compliance", 1.0),
            1.08,
        )
        if project_scoped_rbac:
            boosts["postinstallation_configuration"] = max(
                boosts.get("postinstallation_configuration", 1.0),
                1.14,
            )
        if rbac_assignment:
            boosts["tutorials"] = max(boosts.get("tutorials", 1.0), 1.18)
        if not prefers_rbac_api_docs:
            penalties["role_apis"] = min(penalties.get("role_apis", 1.0), 0.72)
            penalties["project_apis"] = min(penalties.get("project_apis", 1.0), 0.84)

    if detect_unsupported_product(normalized):
        penalties["registry"] = min(penalties.get("registry", 1.0), 0.5)
        penalties["images"] = min(penalties.get("images", 1.0), 0.5)
        penalties["installation_overview"] = min(penalties.get("installation_overview", 1.0), 0.55)

    if has_certificate_monitor_intent(normalized):
        boosts["cli_tools"] = max(boosts.get("cli_tools", 1.0), 1.55)
        boosts["security_and_compliance"] = max(
            boosts.get("security_and_compliance", 1.0),
            1.06,
        )
        penalties["security_and_compliance"] = min(
            penalties.get("security_and_compliance", 1.0),
            0.88,
        )
        penalties["cert_manager_operator_for_red_hat_openshift"] = min(
            penalties.get("cert_manager_operator_for_red_hat_openshift", 1.0),
            0.75,
        )

    return boosts, penalties


def normalize_query(query: str) -> str:
    normalized = _collapse_spaces(query)
    if not normalized:
        return normalized

    terms: list[str] = []
    rbac_intent = has_rbac_intent(normalized)
    project_scoped_rbac = has_project_scoped_rbac_intent(normalized)
    rbac_assignment = has_rbac_assignment_intent(normalized)

    if OCP_RE.search(normalized):
        terms.extend(["OpenShift", "Container", "Platform"])
    if OPENSHIFT_RE.search(normalized):
        terms.append("OpenShift")
    if KUBERNETES_RE.search(normalized):
        terms.append("Kubernetes")
    if ARCHITECTURE_RE.search(normalized):
        terms.extend(["architecture", "구조"])
    if LOGGING_RE.search(normalized):
        terms.extend(["로깅", "logging"])
    if MONITORING_RE.search(normalized):
        terms.extend(["monitoring"])
    if SECURITY_RE.search(normalized):
        terms.extend(["security"])
    if AUTH_RE.search(normalized):
        terms.extend(["authentication"])
    if CERT_RE.search(normalized):
        terms.extend(["certificate", "certificates"])
    if AUTHZ_RE.search(normalized):
        terms.extend(["authorization"])
    if rbac_intent:
        terms.extend(["RBAC", "role", "binding", "rolebinding"])
        if project_scoped_rbac:
            terms.extend(["project", "namespace", "local", "binding"])
        if rbac_assignment:
            terms.extend(["grant", "assign", "policy", "oc", "adm", "add-role-to-user"])
        if USER_SUBJECT_RE.search(normalized):
            terms.extend(["user", "group", "serviceaccount"])
        if ADMIN_ROLE_RE.search(normalized):
            terms.append("admin")
        if EDIT_ROLE_RE.search(normalized):
            terms.append("edit")
        if VIEW_ROLE_RE.search(normalized):
            terms.append("view")
        if CLUSTER_ADMIN_RE.search(normalized):
            terms.append("cluster-admin")
    if MCO_RE.search(normalized):
        terms.extend(["Machine", "Config", "Operator", "machine", "configuration", "operators"])
    if has_mco_concept_intent(normalized):
        terms.extend(
            [
                "Machine Config Operator",
                "MCO",
                "machineconfigpool",
                "machine config pool",
                "machine config daemon",
                "MCD",
                "Ignition",
                "node",
                "configuration",
                "RHCOS",
                "kubelet",
                "CRI-O",
            ]
        )
    if has_operator_concept_intent(normalized):
        terms.extend(
            [
                "Operator",
                "controller",
                "lifecycle",
                "automation",
                "운영",
                "관리",
            ]
        )
    if DISCONNECTED_RE.search(normalized):
        terms.extend(["disconnected"])
    if has_project_terminating_intent(normalized):
        terms.extend(["project", "namespace", "Terminating", "delete"])
    if has_project_finalizer_intent(normalized):
        terms.extend(
            [
                "finalizer",
                "finalizers",
                "metadata.finalizers",
                "CRD",
                "custom resource",
                "error resolving resource",
            ]
        )
    if has_node_drain_intent(normalized):
        terms.extend(
            [
                "oc",
                "adm",
                "drain",
                "ignore-daemonsets",
                "cordon",
                "worker",
                "node",
            ]
        )
    if has_cluster_node_usage_intent(normalized):
        terms.extend(
            [
                "oc",
                "adm",
                "top",
                "nodes",
                "cpu",
                "memory",
            ]
        )
    if has_pod_pending_troubleshooting_intent(normalized):
        terms.extend(
            [
                "Pending",
                "pod",
                "status",
                "scheduling",
                "FailedScheduling",
                "scheduler",
                "events",
                "describe",
                "oc",
                "logs",
                "troubleshooting",
                "pod issues",
                "error states",
                "node affinity",
                "taint",
                "toleration",
            ]
        )
    if CRASH_LOOP_RE.search(normalized):
        terms.extend(
            [
                "CrashLoopBackOff",
                "pod",
                "container",
                "restart",
                "back-off",
                "restartCount",
                "OOMKilled",
                "ImagePullBackOff",
                "ErrImagePull",
                "Back-off restarting failed container",
                "livenessProbe",
                "readinessProbe",
                "events",
                "describe",
                "oc",
                "logs",
                "troubleshooting",
                "pod issues",
                "error states",
                "application diagnostics",
                "애플리케이션 오류",
            ]
        )
    if POD_LIFECYCLE_RE.search(normalized):
        terms.extend(
            [
                "pod",
                "lifecycle",
                "phase",
                "status",
                "Pending",
                "Running",
                "Succeeded",
                "Failed",
                "Unknown",
                "개념",
                "overview",
                "definition",
                "glossary",
                "용어집",
                "pod phase",
                "pod status",
            ]
        )
    if OC_LOGIN_RE.search(normalized):
        terms.extend(["oc", "login", "token", "--token", "--server", "cli"])
    if "기본 문서" in normalized:
        terms.extend(["개요", "overview"])

    if has_doc_locator_intent(normalized):
        terms.extend(["문서", "guide", "documentation"])
    if BACKUP_RE.search(normalized):
        terms.extend(["backup"])
    if RESTORE_RE.search(normalized):
        terms.extend(["restore", "복원"])
    if has_certificate_monitor_intent(normalized):
        terms.extend(
            [
                "monitor-certificates",
                "oc",
                "adm",
                "ocp-certificates",
                "certificate",
                "expiry",
            ]
        )
    if is_explainer_query(normalized):
        terms.extend(["개요", "overview"])
    if is_generic_intro_query(normalized):
        terms.extend(["소개", "overview", "architecture", "기본", "개념"])
    if has_openshift_kubernetes_compare_intent(normalized):
        terms.extend(["comparison", "difference", "비교", "차이점", "유사점"])

    if ETCD_RE.search(normalized):
        terms.append("etcd")
        if has_backup_restore_intent(normalized):
            terms.extend(["backup", "restore", "disaster", "recovery", "snapshot"])
        elif is_explainer_query(normalized) or "중요" in normalized or "역할" in normalized:
            terms.extend(["quorum", "control", "plane", "cluster", "state", "key-value", "store"])

    return _append_terms(normalized, terms)


def _token_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def has_explicit_topic_signal(query: str) -> bool:
    normalized = query or ""
    return any(
        [
            bool(OCP_RE.search(normalized)),
            bool(OPENSHIFT_RE.search(normalized)),
            bool(ETCD_RE.search(normalized)),
            bool(MCO_RE.search(normalized)),
            bool(RBAC_RE.search(normalized)),
            bool(PROJECT_SCOPE_RE.search(normalized)),
            bool(LOGGING_RE.search(normalized)),
            bool(MONITORING_RE.search(normalized)),
            bool(SECURITY_RE.search(normalized)),
            bool(AUTH_RE.search(normalized)),
            bool(AUTHZ_RE.search(normalized)),
            bool(ARCHITECTURE_RE.search(normalized)),
            bool(OPERATOR_RE.search(normalized)),
        ]
    )


def has_follow_up_reference(query: str) -> bool:
    normalized = _collapse_spaces(query)
    lowered = normalized.lower()
    if any(hint in normalized for hint in FOLLOW_UP_HINTS):
        return True
    return lowered.startswith(
        (
            "그리고",
            "그럼",
            "그러면",
            "이어서",
            "그 다음",
            "또 ",
            "찾았는데도",
            "거기서",
            "그 상태에서",
        )
    )


def needs_rewrite(query: str, context: SessionContext) -> bool:
    normalized = _collapse_spaces(query)
    if not normalized:
        return False
    if not any(
        [
            context.current_topic,
            context.user_goal,
            context.open_entities,
            context.ocp_version,
            context.unresolved_question,
        ]
    ):
        return False

    if has_follow_up_reference(normalized):
        return True
    if has_explicit_topic_signal(normalized):
        return False
    return _token_count(normalized) <= 3


def rewrite_query(query: str, context: SessionContext | None = None) -> str:
    normalized = query
    context = context or SessionContext()
    if not needs_rewrite(normalized, context):
        return normalized

    hints: list[str] = []
    if context.ocp_version:
        hints.append(f"OCP {context.ocp_version}")
    if context.current_topic:
        hints.append(f"주제 {context.current_topic}")
    if context.open_entities:
        hints.append(f"엔터티 {', '.join(context.open_entities)}")
    if context.unresolved_question:
        hints.append(f"미해결 질문 {context.unresolved_question}")
    elif context.user_goal:
        hints.append(f"사용자 목표 {context.user_goal}")
    hints.append(normalized)
    return " | ".join(hints)
