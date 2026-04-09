# hybrid retrieval의 fusion/scoring 본체를 모아 둔 파일.
# "왜 이 문서가 올라왔는가"를 설명할 때 retriever보다 먼저 보게 될 핵심 모듈이다.

from __future__ import annotations

import copy
from collections import Counter

from play_book_studio.config.corpus_policy import is_reference_heavy_book_slug

from .models import RetrievalHit, SessionContext
from .query import (
    CRASH_LOOP_RE,
    OC_LOGIN_RE,
    contains_hangul,
    has_backup_restore_intent,
    has_certificate_monitor_intent,
    has_cluster_node_usage_intent,
    has_doc_locator_intent,
    has_hosted_control_plane_signal,
    has_machine_config_reboot_intent,
    has_mco_concept_intent,
    has_node_drain_intent,
    has_openshift_kubernetes_compare_intent,
    has_operator_concept_intent,
    has_project_finalizer_intent,
    has_project_scoped_rbac_intent,
    has_project_terminating_intent,
    has_pod_lifecycle_concept_intent,
    has_pod_pending_troubleshooting_intent,
    has_rbac_assignment_intent,
    has_rbac_intent,
    has_crash_loop_troubleshooting_intent,
    has_update_doc_locator_intent,
    is_generic_intro_query,
    query_book_adjustments,
)
from .ranking import (
    extract_structured_query_terms as _extract_structured_query_terms,
    is_noise_hit as _is_noise_hit,
)


def fuse_ranked_hits(
    query: str,
    ranked_lists: dict[str, list[RetrievalHit]],
    *,
    context: SessionContext | None = None,
    top_k: int,
    rrf_k: int = 60,
    weights: dict[str, float] | None = None,
) -> list[RetrievalHit]:
    # semantic/vector hit가 tie 상황에서 약간 앞서더라도, 전체 동작은 설명 가능하도록 RRF 기반을 유지한다.
    weights = weights or {"bm25": 1.0, "doc_to_book_bm25": 1.35, "vector": 1.1}
    context = context or SessionContext()
    fused_by_id: dict[str, RetrievalHit] = {}
    book_sources: dict[str, set[str]] = {}
    query_has_hangul = contains_hangul(query)
    structured_query_terms = _extract_structured_query_terms(query)
    book_boosts, book_penalties = query_book_adjustments(query, context=context)
    doc_locator_intent = has_doc_locator_intent(query)
    update_doc_locator_intent = has_update_doc_locator_intent(query)
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
    machine_config_reboot_intent = has_machine_config_reboot_intent(query)
    pod_pending_intent = has_pod_pending_troubleshooting_intent(query)
    crash_loop_intent = has_crash_loop_troubleshooting_intent(query)
    pod_lifecycle_intent = has_pod_lifecycle_concept_intent(query)
    oc_login_intent = bool(OC_LOGIN_RE.search(query))
    concept_like_intent = any(
        (
            is_generic_intro_query(query),
            compare_intent,
            operator_concept_intent,
            mco_concept_intent,
            pod_lifecycle_intent,
        )
    )
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
            hit.fused_score *= 1.42
        if query_has_hangul:
            if contains_hangul(hit.text):
                hit.fused_score *= 1.05
            else:
                hit.fused_score *= 0.85
        if is_reference_heavy_book_slug(hit.book_slug):
            if concept_like_intent and not doc_locator_intent and not structured_query_terms:
                hit.fused_score *= 0.34
            elif not doc_locator_intent and not structured_query_terms:
                hit.fused_score *= 0.82
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
            if hit.book_slug == "extensions":
                hit.fused_score *= 1.24
            elif hit.book_slug == "overview":
                hit.fused_score *= 1.16
            elif hit.book_slug == "architecture":
                hit.fused_score *= 1.08
            elif hit.book_slug == "installation_overview":
                hit.fused_score *= 0.52
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
                "operator controller" in lowered_section
                or "olm v1 구성 요소 개요" in hit.section
                or ("controller" in lowered_section and "operator" in lowered_section)
            ):
                hit.fused_score *= 0.82
            if "정의" in hit.section or "purpose" in lowered_section or "목적" in hit.section:
                hit.fused_score *= 1.08
            if (
                hit.book_slug in {"support", "web_console", "release_notes", "edge_computing"}
                or "문제 해결" in hit.section
                or "troubleshooting" in lowered_section
            ):
                hit.fused_score *= 0.55
            if "machine config operator" in context_text:
                if hit.book_slug == "machine_management":
                    hit.fused_score *= 1.18
                if hit.book_slug == "postinstallation_configuration":
                    hit.fused_score *= 1.1
                if hit.book_slug in {"hosted_control_planes", "installation_overview"}:
                    hit.fused_score *= 0.42
            if "console." in lowered_text or "api" in lowered_section:
                hit.fused_score *= 0.78
        if mco_concept_intent:
            lowered_section = hit.section.lower()
            lowered_text = hit.text.lower()
            if hit.book_slug == "architecture":
                hit.fused_score *= 1.2
            elif hit.book_slug == "overview":
                hit.fused_score *= 1.16
            elif hit.book_slug == "machine_management":
                hit.fused_score *= 1.14
            elif hit.book_slug == "postinstallation_configuration":
                hit.fused_score *= 1.12
            elif hit.book_slug == "images":
                hit.fused_score *= 1.08
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
            if hit.book_slug in {"hosted_control_planes", "installation_overview"}:
                hit.fused_score *= 0.42
            if hit.book_slug == "updating_clusters":
                hit.fused_score *= 0.52
            if hit.book_slug == "windows_container_support_for_openshift":
                hit.fused_score *= 0.38
        elif "machine config operator" in context_text:
            lowered_section = hit.section.lower()
            lowered_text = hit.text.lower()
            pause_control_signal = (
                "자동으로 재부팅되지 않도록" in context_text
                or "spec.paused" in context_text.lower()
                or "자동으로 재부팅되지 않도록" in query
                or "spec.paused" in query.lower()
            )
            if hit.book_slug == "machine_management":
                hit.fused_score *= 1.16
            if hit.book_slug == "postinstallation_configuration":
                hit.fused_score *= 1.14
            if hit.book_slug == "architecture":
                hit.fused_score *= 1.12
            if hit.book_slug == "overview":
                hit.fused_score *= 1.06
            if hit.book_slug == "nodes":
                hit.fused_score *= 1.1
            if hit.book_slug == "support":
                hit.fused_score *= 1.28 if pause_control_signal else 0.78
            if hit.book_slug == "cli_tools":
                hit.fused_score *= 0.62
            if machine_config_reboot_intent:
                if hit.book_slug == "updating_clusters":
                    hit.fused_score *= 1.34
                if hit.book_slug == "nodes":
                    hit.fused_score *= 1.08
            if (
                "자동으로 재부팅되지 않도록" in lowered_text
                or "자동으로 재부팅되지 않도록" in lowered_section
                or "spec.paused" in lowered_text
                or "spec.paused" in lowered_section
            ):
                hit.fused_score *= 1.26
            if "machineconfigpool" in lowered_text or "machine config pool" in lowered_text:
                hit.fused_score *= 1.12
            if hit.book_slug in {"specialized_hardware_and_driver_enablement", "network_security", "hosted_control_planes"}:
                hit.fused_score *= 0.24
            if hit.book_slug == "installation_overview":
                hit.fused_score *= 0.42
            if hit.book_slug == "updating_clusters":
                hit.fused_score *= 0.86 if machine_config_reboot_intent else 0.56
        if update_doc_locator_intent:
            lowered_section = hit.section.lower()
            lowered_text = hit.text.lower()
            is_update_guide = hit.book_slug == "updating_clusters"
            is_release_notes = hit.book_slug == "release_notes"
            if is_update_guide:
                hit.fused_score *= 1.34
            elif is_release_notes:
                hit.fused_score *= 1.18
            elif hit.book_slug == "overview":
                hit.fused_score *= 1.05
            elif hit.book_slug == "cli_tools":
                hit.fused_score *= 0.42
            if (
                "업데이트" in hit.section
                or "업그레이드" in hit.section
                or "업데이트" in hit.text
                or "업그레이드" in hit.text
                or "update" in lowered_section
                or "upgrade" in lowered_section
            ):
                hit.fused_score *= 1.1
            if "릴리스 노트" in hit.section or "release notes" in lowered_section or "release notes" in lowered_text:
                hit.fused_score *= 1.08
            if "oc explain" in lowered_text or "리소스에 대한 문서 가져오기" in hit.section or "resource document" in lowered_text:
                hit.fused_score *= 0.22
            if hit.book_slug.endswith("_apis"):
                hit.fused_score *= 0.46
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
            if not hosted_signal and "etcd" in context_text and hit.book_slug == "hosted_control_planes":
                hit.fused_score *= 0.24
            if hit.book_slug == "postinstallation_configuration" and ("etcd 작업" in hit.chapter or "이전 클러스터 상태로 복원" in hit.section):
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
            if hit.book_slug == "support" and "operator 문제 해결" in hit.text and "애플리케이션" not in hit.text:
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
            is_command_section = hit.section.strip().startswith("$ ")
            is_operational_pod_section = (
                "검사" in hit.section
                or "oc get pod" in lowered_text
                or "oc get pods" in lowered_text
                or "[code]" in lowered_text
            )
            if hit.book_slug == "architecture":
                hit.fused_score *= 1.28
            if hit.book_slug == "nodes":
                hit.fused_score *= 1.22
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
            if "용어집" in hit.section or "glossary" in lowered_section or "개요" in hit.section or "overview" in lowered_section:
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
            if (
                "pod 이해" in hit.section
                or "pod 사용" in hit.section
                or hit.section.strip() == "Pod"
                or "pod 구성의 예" in hit.section
            ):
                hit.fused_score *= 1.24
            if hit.book_slug.endswith("_apis"):
                hit.fused_score *= 0.52
            if is_command_section:
                hit.fused_score *= 0.24
            if (
                "[code]" in lowered_text
                or "oc get pod" in lowered_text
                or "evicted" in lowered_text
                or "oomkilled" in lowered_text
            ) and "용어집" not in hit.section and "glossary" not in lowered_section:
                hit.fused_score *= 0.72
            if is_intake_doc and is_operational_pod_section and "pod 이해" not in hit.section:
                hit.fused_score *= 0.46
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
    if pod_lifecycle_intent or operator_concept_intent or mco_concept_intent:
        diversified_hits: list[RetrievalHit] = []
        per_book_counts: Counter[str] = Counter()
        seen_intake_sections: set[tuple[str, str]] = set()
        for hit in fused_hits:
            normalized_section = hit.section.strip().lower()
            if hit.viewer_path.startswith("/docs/intake/"):
                section_key = (hit.book_slug, normalized_section)
                if section_key in seen_intake_sections:
                    continue
                seen_intake_sections.add(section_key)
            if per_book_counts[hit.book_slug] >= 2:
                continue
            diversified_hits.append(hit)
            per_book_counts[hit.book_slug] += 1
        fused_hits = diversified_hits
    return fused_hits[:top_k]
