from __future__ import annotations

# 제품/개념/문서 탐색 성격의 질의 확장 용어를 모아 둔 helper다.

from .intents import *  # noqa: F403


def append_core_query_terms(normalized: str, terms: list[str]) -> None:
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

    if "기본 문서" in normalized:
        terms.extend(["개요", "overview"])

    if has_doc_locator_intent(normalized):
        terms.extend(["문서", "guide", "documentation"])
    if has_update_doc_locator_intent(normalized):
        terms.extend(
            [
                "update guide",
                "updating clusters",
                "release notes",
                "릴리스 노트",
                "클러스터 업데이트",
                "업데이트 준비",
                "업데이트 이해",
            ]
        )
    if BACKUP_RE.search(normalized):
        terms.extend(["backup"])
    if RESTORE_RE.search(normalized):
        terms.extend(["restore", "복원"])
    if is_explainer_query(normalized):
        terms.extend(["개요", "overview"])
    if is_generic_intro_query(normalized):
        terms.extend(["소개", "overview", "architecture", "기본", "개념"])
    if has_openshift_kubernetes_compare_intent(normalized):
        terms.extend(["comparison", "difference", "비교", "차이점", "유사점"])
