from __future__ import annotations

# 개념 설명/문서 위치 찾기처럼 "어떤 문서군을 우선 볼지"를 정하는 조정 규칙 모음이다.

from .intents import *  # noqa: F403


def apply_discovery_adjustments(
    normalized: str,
    *,
    context_text: str,
    boosts: dict[str, float],
    penalties: dict[str, float],
) -> None:
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
        penalties["release_notes"] = 0.55

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
        penalties["release_notes"] = min(penalties.get("release_notes", 1.0), 0.58)

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

    if has_update_doc_locator_intent(normalized):
        boosts["updating_clusters"] = max(boosts.get("updating_clusters", 1.0), 1.72)
        boosts["release_notes"] = max(boosts.get("release_notes", 1.0), 1.38)
        boosts["overview"] = max(boosts.get("overview", 1.0), 1.08)
        penalties["cli_tools"] = min(penalties.get("cli_tools", 1.0), 0.34)
        penalties["web_console"] = min(penalties.get("web_console", 1.0), 0.44)
        penalties["building_applications"] = min(
            penalties.get("building_applications", 1.0),
            0.62,
        )
        penalties["validation_and_troubleshooting"] = min(
            penalties.get("validation_and_troubleshooting", 1.0),
            0.74,
        )
        penalties["config_apis"] = min(penalties.get("config_apis", 1.0), 0.42)
        penalties["specialized_hardware_and_driver_enablement"] = min(
            penalties.get("specialized_hardware_and_driver_enablement", 1.0),
            0.48,
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

    if MCO_RE.search(normalized):
        boosts["machine_management"] = max(boosts.get("machine_management", 1.0), 1.3)
        boosts["architecture"] = max(boosts.get("architecture", 1.0), 1.12)
        boosts["overview"] = max(boosts.get("overview", 1.0), 1.06)
        penalties["machine_apis"] = 0.76

    if has_operator_concept_intent(normalized):
        boosts["architecture"] = max(boosts.get("architecture", 1.0), 1.16)
        boosts["extensions"] = max(boosts.get("extensions", 1.0), 1.36)
        boosts["operators"] = max(boosts.get("operators", 1.0), 1.22)
        boosts["overview"] = max(boosts.get("overview", 1.0), 1.2)
        if MCO_RE.search(normalized) or MCO_RE.search(context_text):
            boosts["machine_management"] = max(boosts.get("machine_management", 1.0), 1.42)
        penalties["support"] = min(penalties.get("support", 1.0), 0.58)
        penalties["web_console"] = min(penalties.get("web_console", 1.0), 0.62)
        penalties["release_notes"] = min(penalties.get("release_notes", 1.0), 0.7)
        penalties["edge_computing"] = min(penalties.get("edge_computing", 1.0), 0.78)
        penalties["installation_overview"] = min(
            penalties.get("installation_overview", 1.0),
            0.56,
        )

    if has_mco_concept_intent(normalized):
        boosts["architecture"] = max(boosts.get("architecture", 1.0), 1.28)
        boosts["overview"] = max(boosts.get("overview", 1.0), 1.24)
        boosts["machine_management"] = max(boosts.get("machine_management", 1.0), 1.55)
        boosts["postinstallation_configuration"] = max(
            boosts.get("postinstallation_configuration", 1.0),
            1.08,
        )
        penalties["support"] = min(penalties.get("support", 1.0), 0.54)
        penalties["release_notes"] = min(penalties.get("release_notes", 1.0), 0.58)
        penalties["edge_computing"] = min(penalties.get("edge_computing", 1.0), 0.72)
        penalties["security_and_compliance"] = min(
            penalties.get("security_and_compliance", 1.0),
            0.74,
        )
        penalties["machine_apis"] = min(penalties.get("machine_apis", 1.0), 0.55)
        penalties["images"] = min(penalties.get("images", 1.0), 0.62)
        penalties["windows_container_support_for_openshift"] = min(
            penalties.get("windows_container_support_for_openshift", 1.0),
            0.42,
        )
        penalties["updating_clusters"] = min(
            penalties.get("updating_clusters", 1.0),
            0.48,
        )
    elif MCO_RE.search(context_text):
        boosts["machine_management"] = max(boosts.get("machine_management", 1.0), 1.12)
        boosts["architecture"] = max(boosts.get("architecture", 1.0), 1.08)
        boosts["cli_tools"] = max(boosts.get("cli_tools", 1.0), 1.1)
        boosts["overview"] = max(boosts.get("overview", 1.0), 1.06)
        penalties["network_security"] = min(penalties.get("network_security", 1.0), 0.32)
        penalties["hosted_control_planes"] = min(
            penalties.get("hosted_control_planes", 1.0),
            0.38,
        )
        penalties["specialized_hardware_and_driver_enablement"] = min(
            penalties.get("specialized_hardware_and_driver_enablement", 1.0),
            0.34,
        )
        if (
            "자동 재부팅" in context_text
            or "자동으로 재부팅되지 않도록" in context_text
            or "spec.paused" in context_text.lower()
        ):
            boosts["support"] = max(boosts.get("support", 1.0), 1.58)
            boosts["cli_tools"] = max(boosts.get("cli_tools", 1.0), 1.18)
            penalties["updating_clusters"] = min(
                penalties.get("updating_clusters", 1.0),
                0.52,
            )
            penalties["edge_computing"] = min(
                penalties.get("edge_computing", 1.0),
                0.58,
            )
            penalties["security_and_compliance"] = min(
                penalties.get("security_and_compliance", 1.0),
                0.72,
            )
            penalties["windows_container_support_for_openshift"] = min(
                penalties.get("windows_container_support_for_openshift", 1.0),
                0.46,
            )
            penalties["network_security"] = min(
                penalties.get("network_security", 1.0),
                0.24,
            )
            penalties["specialized_hardware_and_driver_enablement"] = min(
                penalties.get("specialized_hardware_and_driver_enablement", 1.0),
                0.24,
            )
            penalties["hosted_control_planes"] = min(
                penalties.get("hosted_control_planes", 1.0),
                0.28,
            )
            penalties["machine_apis"] = min(penalties.get("machine_apis", 1.0), 0.68)
            penalties["release_notes"] = min(penalties.get("release_notes", 1.0), 0.62)
