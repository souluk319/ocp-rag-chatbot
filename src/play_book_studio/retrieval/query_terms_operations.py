from __future__ import annotations

# 운영 절차/트러블슈팅 성격의 질의 확장 용어를 모아 둔 helper다.

from .intents import *  # noqa: F403


def append_operation_query_terms(normalized: str, terms: list[str]) -> None:
    rbac_intent = has_rbac_intent(normalized)
    project_scoped_rbac = has_project_scoped_rbac_intent(normalized)
    rbac_assignment = has_rbac_assignment_intent(normalized)

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
    if has_deployment_scaling_intent(normalized):
        terms.extend(
            [
                "deployment",
                "deployments",
                "replicas",
                "oc",
                "scale",
                "--replicas",
                "수동 스케일링",
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
