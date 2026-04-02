from __future__ import annotations

import re

from .models import SessionContext


HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
SPACE_RE = re.compile(r"\s+")
OCP_RE = re.compile(r"\bocp\b", re.IGNORECASE)
OPENSHIFT_RE = re.compile(r"(오픈시프트|openshift)", re.IGNORECASE)
ARCHITECTURE_RE = re.compile(r"(아키텍처|architecture)", re.IGNORECASE)
LOGGING_RE = re.compile(r"(로그|로깅|logging)", re.IGNORECASE)
MONITORING_RE = re.compile(r"(모니터링|monitoring)", re.IGNORECASE)
SECURITY_RE = re.compile(r"(보안|security)", re.IGNORECASE)
AUTH_RE = re.compile(r"(인증|authentication)", re.IGNORECASE)
AUTHZ_RE = re.compile(r"(권한|authorization)", re.IGNORECASE)
MCO_RE = re.compile(r"machine config operator", re.IGNORECASE)
DISCONNECTED_RE = re.compile(r"(연결이 없는 환경|분리망|disconnect)", re.IGNORECASE)
ETCD_RE = re.compile(r"etcd", re.IGNORECASE)
BACKUP_RE = re.compile(r"(백업|backup)", re.IGNORECASE)
RESTORE_RE = re.compile(r"(복구|복원|restore)", re.IGNORECASE)
DOC_LOCATOR_RE = re.compile(
    r"(문서|가이드|어디서|어디 있어|어디를|찾아|찾을|봐야|보려면|보고 싶|참고할)",
    re.IGNORECASE,
)
EXPLAINER_RE = re.compile(
    r"(설명해줘|설명해 줘|처음 설명|개념 설명|뭐야\??|무엇인가\??|무슨 역할|왜 중요|차이가 뭐야\??|역할이 뭐야\??)",
    re.IGNORECASE,
)
GENERIC_INTRO_RE = re.compile(
    r"(오픈시프트|openshift).*(뭐야|무엇|소개|개요|아키텍처|architecture)|"
    r"(쿠버네티스|kubernetes).*(오픈시프트|openshift).*(차이|다른 점)",
    re.IGNORECASE,
)
FOLLOW_UP_HINTS = (
    "그거",
    "그건",
    "저거",
    "그 설정",
    "그 문서",
    "그 내용",
    "아까",
    "이전",
    "해당",
    "1번",
    "2번",
    "3번",
)
UNSUPPORTED_PRODUCTS = (
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


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = (text or "").lower()
    return any(keyword in lowered for keyword in keywords)


def has_doc_locator_intent(query: str) -> bool:
    return bool(DOC_LOCATOR_RE.search(query or ""))


def has_backup_restore_intent(query: str) -> bool:
    return bool(BACKUP_RE.search(query or "") or RESTORE_RE.search(query or ""))


def is_generic_intro_query(query: str) -> bool:
    lowered = (query or "").lower()
    if GENERIC_INTRO_RE.search(query or ""):
        return True
    return "openshift" in lowered and bool(
        ARCHITECTURE_RE.search(query or "") or EXPLAINER_RE.search(query or "")
    )


def is_explainer_query(query: str) -> bool:
    return bool(EXPLAINER_RE.search(query or ""))


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


def query_book_adjustments(query: str) -> tuple[dict[str, float], dict[str, float]]:
    normalized = _collapse_spaces(query)
    boosts: dict[str, float] = {}
    penalties: dict[str, float] = {}

    if is_generic_intro_query(normalized):
        boosts["architecture"] = 1.35
        boosts["overview"] = 1.18
        penalties["networking_overview"] = 0.68
        penalties["observability_overview"] = 0.8
        penalties["api_overview"] = 0.78
        penalties["project_apis"] = 0.82

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

    if ETCD_RE.search(normalized):
        if has_backup_restore_intent(normalized):
            boosts["etcd"] = max(boosts.get("etcd", 1.0), 1.25)
            boosts["backup_and_restore"] = max(boosts.get("backup_and_restore", 1.0), 1.12)
        elif is_explainer_query(normalized) or "중요" in normalized or "역할" in normalized:
            boosts["etcd"] = max(boosts.get("etcd", 1.0), 1.4)
            boosts["architecture"] = max(boosts.get("architecture", 1.0), 1.08)
            penalties["backup_and_restore"] = 0.62

    if "machine config operator" in normalized.lower():
        boosts["machine_configuration"] = max(boosts.get("machine_configuration", 1.0), 1.3)
        boosts["operators"] = max(boosts.get("operators", 1.0), 1.15)
        penalties["machine_apis"] = 0.76

    if detect_unsupported_product(normalized):
        penalties["registry"] = min(penalties.get("registry", 1.0), 0.5)
        penalties["images"] = min(penalties.get("images", 1.0), 0.5)
        penalties["installation_overview"] = min(penalties.get("installation_overview", 1.0), 0.55)

    return boosts, penalties


def normalize_query(query: str) -> str:
    normalized = _collapse_spaces(query)
    if not normalized:
        return normalized

    terms: list[str] = []

    if OCP_RE.search(normalized):
        terms.extend(["OpenShift", "Container", "Platform"])
    if OPENSHIFT_RE.search(normalized):
        terms.append("OpenShift")
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
    if AUTHZ_RE.search(normalized):
        terms.extend(["authorization"])
    if MCO_RE.search(normalized):
        terms.extend(["Machine", "Config", "Operator", "machine", "configuration", "operators"])
    if DISCONNECTED_RE.search(normalized):
        terms.extend(["disconnected"])
    if "기본 문서" in normalized:
        terms.extend(["개요", "overview"])

    if has_doc_locator_intent(normalized):
        terms.extend(["문서", "guide", "documentation"])
    if BACKUP_RE.search(normalized):
        terms.extend(["backup"])
    if RESTORE_RE.search(normalized):
        terms.extend(["restore", "복원"])
    if is_explainer_query(normalized):
        terms.extend(["개요", "overview"])
    if is_generic_intro_query(normalized):
        terms.extend(["소개", "overview", "architecture", "기본", "개념"])

    if ETCD_RE.search(normalized):
        terms.append("etcd")
        if has_backup_restore_intent(normalized):
            terms.extend(["backup", "restore", "disaster", "recovery", "snapshot"])
        elif is_explainer_query(normalized) or "중요" in normalized or "역할" in normalized:
            terms.extend(["quorum", "control", "plane", "cluster", "state", "key-value", "store"])

    return _append_terms(normalized, terms)


def _token_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def needs_rewrite(query: str, context: SessionContext) -> bool:
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
    if _token_count(query) <= 5:
        return True
    lowered = query.lower()
    return any(hint in query for hint in FOLLOW_UP_HINTS) or lowered.startswith("그리고")


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
