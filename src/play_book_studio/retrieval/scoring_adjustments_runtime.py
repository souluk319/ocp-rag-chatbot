# 운영/트러블슈팅 질의의 점수 조정 규칙.
from __future__ import annotations

from .models import RetrievalHit
from .scoring_signals import ScoreSignals


def apply_runtime_adjustments(
    hit: RetrievalHit,
    *,
    signals: ScoreSignals,
    is_intake_doc: bool,
) -> None:
    lowered_text = hit.text.lower()
    lowered_section = hit.section.lower()

    if signals.project_terminating_intent:
        if hit.book_slug == "building_applications" and "프로젝트 삭제" in hit.section:
            hit.fused_score *= 1.05
        if hit.book_slug == "support" and "종료 중" in hit.text:
            hit.fused_score *= 1.2
        if "oc adm prune" in lowered_text or "prune" in lowered_section:
            hit.fused_score *= 0.42

    if signals.project_finalizer_intent:
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

    if signals.node_drain_intent:
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

    if signals.cluster_node_usage_intent:
        if hit.book_slug in {"support", "nodes"}:
            hit.fused_score *= 1.14
        if "oc adm top nodes" in lowered_text:
            hit.fused_score *= 1.3
        if "oc adm top node" in lowered_text:
            hit.fused_score *= 1.08
        if "oc top pods" in lowered_text or "kubectl top pods" in lowered_text:
            hit.fused_score *= 0.72

    if signals.pod_pending_intent:
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

    if signals.crash_loop_intent:
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

    if signals.pod_lifecycle_intent:
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

    if signals.oc_login_intent:
        if hit.book_slug == "cli_tools":
            hit.fused_score *= 1.2
        if "oc login" in lowered_text:
            hit.fused_score *= 1.28

    if signals.rbac_intent:
        if (
            "rbac" in lowered_text
            or "rolebinding" in lowered_text
            or "역할 바인딩" in hit.text
            or "로컬 바인딩" in hit.text
        ):
            hit.fused_score *= 1.06
        if signals.project_scoped_rbac and (
            "프로젝트" in hit.text
            or "네임스페이스" in hit.text
            or "project" in lowered_text
            or "namespace" in lowered_text
        ):
            hit.fused_score *= 1.05
        if signals.rbac_assignment and (
            "oc adm policy" in lowered_text
            or "add-role-to-user" in lowered_text
            or "rolebinding" in lowered_text
        ):
            hit.fused_score *= 1.08
