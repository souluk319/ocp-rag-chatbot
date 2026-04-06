from __future__ import annotations

import re

from ocp_rag.session import SessionContext

from .command_memory import build_command_template_hints


HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
SPACE_RE = re.compile(r"\s+")
VERSION_RE = re.compile(r"(?<!\d)4\.(\d+)(?!\d)")
STEP_REFERENCE_RE = re.compile(r"(?<!\d)(1[0-2]|[1-9])번(?:\s*단계)?")
PROCEDURE_NEXT_STEP_RE = re.compile(r"(다음(?:\s*단계)?|그 다음|이어서|다음으로|계속(?:해서)?)", re.IGNORECASE)
PROCEDURE_CURRENT_STEP_RE = re.compile(
    r"(이 단계|현재 단계|여기서|여기부터|방금 단계|해당 단계)",
    re.IGNORECASE,
)
PROCEDURE_DONE_UNTIL_RE = re.compile(
    r"(?<!\d)(1[0-2]|[1-9])번(?:\s*단계)?(?:까지|까진|까지는).*(했|끝|완료)",
    re.IGNORECASE,
)
OCP_RE = re.compile(r"(?<![a-z0-9])ocp(?![a-z0-9])", re.IGNORECASE)
OPENSHIFT_RE = re.compile(r"(오픈시프트|openshift)", re.IGNORECASE)
KUBERNETES_RE = re.compile(r"(쿠버네티스|kubernetes)", re.IGNORECASE)
COMPARE_RE = re.compile(r"(차이|다른 점|비교|vs|versus|유사점)", re.IGNORECASE)
ARCHITECTURE_RE = re.compile(r"(아키텍처|architecture)", re.IGNORECASE)
LOGGING_RE = re.compile(r"(로그|로깅|logging)", re.IGNORECASE)
AUDIT_RE = re.compile(r"(감사|audit)", re.IGNORECASE)
EVENT_RE = re.compile(r"(이벤트|event)", re.IGNORECASE)
APP_RE = re.compile(r"(애플리케이션|application|pod|컨테이너|container)", re.IGNORECASE)
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
ROLE_OBJECT_RE = re.compile(r"(역할|\brole\b)", re.IGNORECASE)
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
STEP_BY_STEP_RE = re.compile(
    r"(단계별|순서대로|차근차근|step-by-step|step by step|stepwise)",
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
)
FOLLOW_UP_STARTERS = (
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
COMMAND_STYLE_HINTS = (
    "그 명령",
    "그 커맨드",
    "그 yaml",
    "그 매니페스트",
    "yaml로",
    "명령어로",
    "커맨드로",
    "cli로",
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


OC_LOGIN_RE = re.compile(r"\boc\s+login\b", re.IGNORECASE)
POD_PENDING_RE = re.compile(
    r"(?:\bpod\b.*\bpending\b|\bpending\b.*\bpod\b|pod\s*pending(?:[가-힣]+)?)",
    re.IGNORECASE,
)
CRASHLOOPBACKOFF_RE = re.compile(r"crashloopbackoff(?:[가-힣]+)?", re.IGNORECASE)
POD_LIFECYCLE_RE = re.compile(
    r"(?:\bpod\b.*\blifecycle\b|\blifecycle\b.*\bpod\b|pod\s*lifecycle(?:[가-힣]+)?)",
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


def _has_intro_keyword(text: str) -> bool:
    normalized = text or ""
    lowered = normalized.lower()
    return any(
        keyword in normalized
        for keyword in (
            "소개",
            "소개해줘",
            "소개해 줘",
            "소개해주세요",
            "소개해 주세요",
        )
    ) or any(keyword in lowered for keyword in ("introduction", "intro"))


def has_doc_locator_intent(query: str) -> bool:
    return bool(DOC_LOCATOR_RE.search(query or ""))


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


def has_oc_login_intent(query: str) -> bool:
    return bool(OC_LOGIN_RE.search(query or ""))


def has_pod_pending_intent(query: str) -> bool:
    return bool(POD_PENDING_RE.search(query or ""))


def has_crashloopbackoff_intent(query: str) -> bool:
    return bool(CRASHLOOPBACKOFF_RE.search(query or ""))


def has_pod_lifecycle_intent(query: str) -> bool:
    return bool(POD_LIFECYCLE_RE.search(query or ""))


def has_rbac_intent(query: str) -> bool:
    normalized = query or ""
    if RBAC_RE.search(normalized):
        return True
    if bool(AUTHZ_RE.search(normalized)) and bool(
        PROJECT_SCOPE_RE.search(normalized)
        or ROLE_ASSIGN_RE.search(normalized)
        or ADMIN_ROLE_RE.search(normalized)
        or EDIT_ROLE_RE.search(normalized)
        or VIEW_ROLE_RE.search(normalized)
        or CLUSTER_ADMIN_RE.search(normalized)
    ):
        return True
    return bool(PROJECT_SCOPE_RE.search(normalized)) and bool(ROLE_ASSIGN_RE.search(normalized)) and bool(
        ROLE_OBJECT_RE.search(normalized)
        or USER_SUBJECT_RE.search(normalized)
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
        ARCHITECTURE_RE.search(query or "")
        or EXPLAINER_RE.search(query or "")
        or _has_intro_keyword(query or "")
    )


def has_openshift_kubernetes_compare_intent(query: str) -> bool:
    normalized = query or ""
    return bool(OPENSHIFT_RE.search(normalized)) and bool(KUBERNETES_RE.search(normalized)) and bool(
        COMPARE_RE.search(normalized) or "차이를" in normalized or "차이점" in normalized
    )


def is_explainer_query(query: str) -> bool:
    return bool(EXPLAINER_RE.search(query or "") or _has_intro_keyword(query or ""))


def has_step_by_step_intent(query: str) -> bool:
    return bool(STEP_BY_STEP_RE.search(query or ""))


def has_kubernetes_compare_follow_up_intent(query: str) -> bool:
    normalized = query or ""
    if has_openshift_kubernetes_compare_intent(normalized):
        return True
    if OPENSHIFT_RE.search(normalized) or OCP_RE.search(normalized):
        return False
    if not KUBERNETES_RE.search(normalized):
        return False
    return bool(
        COMPARE_RE.search(normalized)
        or "\ucc28\uc774" in normalized
        or "\ube44\uad50" in normalized
    )


def has_architecture_explainer_intent(query: str) -> bool:
    normalized = query or ""
    lowered = normalized.lower()
    return bool(ARCHITECTURE_RE.search(normalized)) and bool(
        is_explainer_query(normalized)
        or "\ud55c \uc7a5" in normalized
        or "\uac1c\uc694" in normalized
        or "\uc694\uc57d" in normalized
        or "overview" in lowered
        or "summary" in lowered
    )


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
    oc_login_intent = has_oc_login_intent(normalized)
    pod_pending_intent = has_pod_pending_intent(normalized)
    crashloopbackoff_intent = has_crashloopbackoff_intent(normalized)
    pod_lifecycle_intent = has_pod_lifecycle_intent(normalized)

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

    if has_openshift_kubernetes_compare_intent(normalized) or has_kubernetes_compare_follow_up_intent(
        normalized
    ):
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

    if has_architecture_explainer_intent(normalized):
        boosts["architecture"] = max(boosts.get("architecture", 1.0), 1.42)
        boosts["overview"] = max(boosts.get("overview", 1.0), 1.18)
        penalties["tutorials"] = min(penalties.get("tutorials", 1.0), 0.7)
        penalties["support"] = min(penalties.get("support", 1.0), 0.72)
        penalties["cli_tools"] = min(penalties.get("cli_tools", 1.0), 0.76)

    if oc_login_intent:
        boosts["cli_tools"] = max(boosts.get("cli_tools", 1.0), 1.65)
        boosts["web_console"] = max(boosts.get("web_console", 1.0), 1.16)
        boosts["authentication_and_authorization"] = max(
            boosts.get("authentication_and_authorization", 1.0),
            1.14,
        )
        penalties["release_notes"] = min(penalties.get("release_notes", 1.0), 0.72)
        penalties["registry"] = min(penalties.get("registry", 1.0), 0.78)

    if pod_pending_intent:
        boosts["cli_tools"] = max(boosts.get("cli_tools", 1.0), 1.42)
        boosts["nodes"] = max(boosts.get("nodes", 1.0), 1.3)
        boosts["support"] = max(boosts.get("support", 1.0), 1.16)
        boosts["edge_computing"] = max(boosts.get("edge_computing", 1.0), 1.1)
        penalties["machine_management"] = min(penalties.get("machine_management", 1.0), 0.58)
        penalties["updating_clusters"] = min(penalties.get("updating_clusters", 1.0), 0.62)
        penalties["authentication_and_authorization"] = min(
            penalties.get("authentication_and_authorization", 1.0),
            0.72,
        )
        penalties["ingress_and_load_balancing"] = min(
            penalties.get("ingress_and_load_balancing", 1.0),
            0.76,
        )

    if crashloopbackoff_intent:
        boosts["support"] = max(boosts.get("support", 1.0), 1.44)
        boosts["cli_tools"] = max(boosts.get("cli_tools", 1.0), 1.34)
        boosts["nodes"] = max(boosts.get("nodes", 1.0), 1.18)
        boosts["postinstallation_configuration"] = max(
            boosts.get("postinstallation_configuration", 1.0),
            1.12,
        )
        penalties["hosted_control_planes"] = min(
            penalties.get("hosted_control_planes", 1.0),
            0.48,
        )
        penalties["ovn-kubernetes_network_plugin"] = min(
            penalties.get("ovn-kubernetes_network_plugin", 1.0),
            0.7,
        )
        penalties["specialized_hardware_and_driver_enablement"] = min(
            penalties.get("specialized_hardware_and_driver_enablement", 1.0),
            0.78,
        )

    if pod_lifecycle_intent:
        boosts["nodes"] = max(boosts.get("nodes", 1.0), 1.52)
        boosts["workloads_apis"] = max(boosts.get("workloads_apis", 1.0), 1.4)
        boosts["template_apis"] = max(boosts.get("template_apis", 1.0), 1.12)
        boosts["architecture"] = max(boosts.get("architecture", 1.0), 1.08)
        penalties["edge_computing"] = min(penalties.get("edge_computing", 1.0), 0.42)
        penalties["operators"] = min(penalties.get("operators", 1.0), 0.76)

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
    if "기본 문서" in normalized:
        terms.extend(["개요", "overview"])

    if has_doc_locator_intent(normalized):
        terms.extend(["문서", "guide", "documentation"])
    if has_step_by_step_intent(normalized):
        terms.extend(["절차", "단계", "순서", "procedure", "steps"])
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
    if has_architecture_explainer_intent(normalized):
        terms.extend(["OpenShift", "Container", "Platform"])
    if has_oc_login_intent(normalized):
        terms.extend(["cli", "login", "kubeconfig", "kubeadmin", "web", "browser"])
    if has_pod_pending_intent(normalized):
        terms.extend(["scheduling", "oc", "describe", "events", "resource", "namespace"])
    if has_crashloopbackoff_intent(normalized):
        terms.extend(["oc", "logs", "describe", "pod", "error", "troubleshooting"])
    if has_pod_lifecycle_intent(normalized):
        terms.extend(["nodes", "workloads", "initContainers", "restartPolicy", "spec", "status"])
    if has_openshift_kubernetes_compare_intent(normalized) or has_kubernetes_compare_follow_up_intent(
        normalized
    ):
        if not (OPENSHIFT_RE.search(normalized) or OCP_RE.search(normalized)):
            terms.extend(["OpenShift", "Container", "Platform"])
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
            has_oc_login_intent(normalized),
            has_pod_pending_intent(normalized),
            has_crashloopbackoff_intent(normalized),
            has_pod_lifecycle_intent(normalized),
        ]
    )


def has_follow_up_reference(query: str) -> bool:
    normalized = _collapse_spaces(query)
    lowered = normalized.lower()
    if STEP_REFERENCE_RE.search(normalized):
        return True
    if PROCEDURE_CURRENT_STEP_RE.search(normalized) or PROCEDURE_NEXT_STEP_RE.search(normalized):
        return True
    if any(hint in normalized for hint in FOLLOW_UP_HINTS):
        return True
    if lowered.startswith(FOLLOW_UP_STARTERS):
        return not has_explicit_topic_signal(normalized)
    return False


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
            context.recent_turns,
            context.topic_journal,
            context.reference_hints,
            context.recent_steps,
            context.recent_commands,
            context.procedure_memory,
        ]
    ):
        return False

    if _resolve_step_reference(normalized, context) or _resolve_procedure_step_index(normalized, context) is not None:
        return True
    if has_follow_up_reference(normalized):
        return True
    if has_explicit_topic_signal(normalized):
        return False
    return _token_count(normalized) <= 3


def _resolve_step_reference(query: str, context: SessionContext) -> str | None:
    match = STEP_REFERENCE_RE.search(query or "")
    if not match or not context.recent_steps:
        return None
    index = int(match.group(1)) - 1
    if index < 0 or index >= len(context.recent_steps):
        return None
    return context.recent_steps[index]


def _needs_command_reference_hint(query: str) -> bool:
    normalized = (query or "").lower()
    return any(hint in normalized for hint in COMMAND_STYLE_HINTS)


def _resolve_procedure_step_index(query: str, context: SessionContext) -> int | None:
    procedure = context.procedure_memory
    if procedure is None or not procedure.steps:
        return None

    normalized = query or ""
    match = STEP_REFERENCE_RE.search(normalized)
    if match:
        index = int(match.group(1)) - 1
        if 0 <= index < len(procedure.steps):
            return index

    completed_match = PROCEDURE_DONE_UNTIL_RE.search(normalized)
    if completed_match:
        index = int(completed_match.group(1))
        return min(index, len(procedure.steps) - 1)

    if PROCEDURE_CURRENT_STEP_RE.search(normalized):
        return procedure.active_step_index

    if PROCEDURE_NEXT_STEP_RE.search(normalized):
        if procedure.active_step_index is None:
            return 0 if procedure.steps else None
        return min(procedure.active_step_index + 1, len(procedure.steps) - 1)

    return None


def _needs_procedure_command_hint(query: str) -> bool:
    normalized = _collapse_spaces(query)
    return _needs_command_reference_hint(normalized) or any(
        token in normalized for token in ["확인", "체크", "검증", "명령", "커맨드", "yaml", "manifest"]
    )


def _procedure_memory_hints(query: str, context: SessionContext) -> list[str]:
    procedure = context.procedure_memory
    if procedure is None or not procedure.steps:
        return []

    normalized = _collapse_spaces(query)
    hints: list[str] = []
    if procedure.goal:
        hints.append(f"절차 목표 {procedure.goal}")

    focused_index = _resolve_procedure_step_index(normalized, context)
    if focused_index is not None:
        step = procedure.steps[focused_index]
        hints.append(f"절차 참조 단계 {focused_index + 1}. {step}")
        command = procedure.command_for(focused_index)
        if command and _needs_procedure_command_hint(normalized):
            hints.append(f"절차 단계 명령 {command}")
    elif has_follow_up_reference(normalized) and procedure.active_step_index is not None:
        active_step = procedure.active_step()
        if active_step:
            hints.append(f"현재 절차 단계 {procedure.active_step_index + 1}. {active_step}")
        if PROCEDURE_NEXT_STEP_RE.search(normalized):
            next_index = min(procedure.active_step_index + 1, len(procedure.steps) - 1)
            hints.append(f"다음 절차 단계 {next_index + 1}. {procedure.steps[next_index]}")

    if procedure.references and has_follow_up_reference(normalized):
        hints.append(f"진행 중 절차 근거 {' | '.join(procedure.references[:2])}")
    return hints


def _recent_turn_memory_hints(query: str, context: SessionContext) -> list[str]:
    normalized = _collapse_spaces(query)
    recent_turns = [turn for turn in context.recent_turns if turn.query or turn.topic or turn.answer_focus]
    if not recent_turns:
        return []

    hints: list[str] = []
    latest_turn = recent_turns[-1]
    if has_follow_up_reference(normalized):
        if len(recent_turns) > 1:
            capsules: list[str] = []
            for turn in recent_turns[-2:]:
                if turn.topic:
                    capsules.append(f"{turn.query} -> {turn.topic}")
                elif turn.answer_focus:
                    capsules.append(f"{turn.query} -> {turn.answer_focus}")
                else:
                    capsules.append(turn.query)
            if capsules:
                hint = f"최근 대화 캡슐 {' || '.join(capsules)}"
                if latest_turn.references:
                    hint = f"{hint} | refs={' | '.join(latest_turn.references[:2])}"
                hints.append(hint)
        else:
            capsule_parts = [f"query={latest_turn.query}"]
            if latest_turn.topic:
                capsule_parts.append(f"topic={latest_turn.topic}")
            if latest_turn.answer_focus:
                capsule_parts.append(f"focus={latest_turn.answer_focus}")
            if latest_turn.references:
                capsule_parts.append(f"refs={' | '.join(latest_turn.references[:2])}")
            if capsule_parts:
                hints.append(f"최근 대화 캡슐 {' | '.join(capsule_parts)}")
        return hints

    if _token_count(normalized) <= 6:
        capsules: list[str] = []
        for turn in recent_turns[-2:]:
            capsule_parts = []
            if turn.topic:
                capsule_parts.append(turn.topic)
            if turn.answer_focus:
                capsule_parts.append(turn.answer_focus)
            if turn.references:
                capsule_parts.append(turn.references[0])
            if capsule_parts:
                capsules.append(" / ".join(capsule_parts))
        if capsules:
            hints.append(f"최근 대화 캡슐 {' || '.join(capsules)}")
    return hints


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
    if context.topic_journal:
        hints.append(f"최근 주제 흐름 {' -> '.join(context.topic_journal[-3:])}")
    hints.extend(_recent_turn_memory_hints(normalized, context))
    hints.extend(_procedure_memory_hints(normalized, context))
    hints.extend(build_command_template_hints(normalized, context))
    if context.open_entities:
        hints.append(f"엔터티 {', '.join(context.open_entities)}")
    if context.reference_hints:
        hints.append(f"최근 근거 메모 {' | '.join(context.reference_hints[-2:])}")
    step_reference = _resolve_step_reference(normalized, context)
    if step_reference:
        hints.append(f"참조 단계 {step_reference}")
    elif context.recent_steps and has_follow_up_reference(normalized):
        hints.append(f"최근 단계 {' | '.join(context.recent_steps[:3])}")
    if context.recent_commands and _needs_command_reference_hint(normalized):
        hints.append(f"최근 명령 {' | '.join(context.recent_commands[:2])}")
    if context.unresolved_question:
        hints.append(f"미해결 질문 {context.unresolved_question}")
    elif context.user_goal:
        hints.append(f"사용자 목표 {context.user_goal}")
    hints.append(normalized)
    return " | ".join(hints)
