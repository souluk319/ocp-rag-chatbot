from __future__ import annotations

# 운영 절차/트러블슈팅/RBAC처럼 "어떤 실행 문서군을 우선 볼지"를 정하는 조정 규칙 모음이다.

from .corpus_scope import detect_unsupported_product
from .intents import *  # noqa: F403


def apply_operation_adjustments(
    normalized: str,
    *,
    context_text: str,
    boosts: dict[str, float],
    penalties: dict[str, float],
) -> None:
    rbac_intent = has_rbac_intent(normalized)
    project_scoped_rbac = has_project_scoped_rbac_intent(normalized)
    rbac_assignment = has_rbac_assignment_intent(normalized)
    prefers_rbac_api_docs = bool(ROLE_API_STYLE_RE.search(normalized))

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

    if has_machine_config_reboot_intent(normalized) or (
        MCO_RE.search(context_text) and "재부팅" in normalized
    ):
        boosts["machine_management"] = max(boosts.get("machine_management", 1.0), 1.7)
        boosts["support"] = max(boosts.get("support", 1.0), 1.18)
        boosts["nodes"] = max(boosts.get("nodes", 1.0), 1.12)
        boosts["updating_clusters"] = max(boosts.get("updating_clusters", 1.0), 1.12)
        penalties["specialized_hardware_and_driver_enablement"] = min(
            penalties.get("specialized_hardware_and_driver_enablement", 1.0),
            0.18,
        )
        penalties["network_security"] = min(penalties.get("network_security", 1.0), 0.22)
        penalties["windows_container_support_for_openshift"] = min(
            penalties.get("windows_container_support_for_openshift", 1.0),
            0.28,
        )
        penalties["security_and_compliance"] = min(
            penalties.get("security_and_compliance", 1.0),
            0.55,
        )
        penalties["hosted_control_planes"] = min(
            penalties.get("hosted_control_planes", 1.0),
            0.42,
        )

    if has_deployment_scaling_intent(normalized) or has_deployment_scaling_intent(context_text):
        boosts["cli_tools"] = max(boosts.get("cli_tools", 1.0), 1.82)
        boosts["building_applications"] = max(boosts.get("building_applications", 1.0), 1.35)
        penalties["authentication_and_authorization"] = min(
            penalties.get("authentication_and_authorization", 1.0),
            0.32,
        )
        penalties["postinstallation_configuration"] = min(
            penalties.get("postinstallation_configuration", 1.0),
            0.38,
        )
        penalties["machine_management"] = min(
            penalties.get("machine_management", 1.0),
            0.46,
        )
        penalties["nodes"] = min(penalties.get("nodes", 1.0), 0.72)

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
        boosts["nodes"] = max(boosts.get("nodes", 1.0), 1.24)
        boosts["overview"] = max(boosts.get("overview", 1.0), 1.18)
        boosts["building_applications"] = max(
            boosts.get("building_applications", 1.0),
            1.12,
        )
        penalties["workloads_apis"] = min(penalties.get("workloads_apis", 1.0), 0.54)
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
