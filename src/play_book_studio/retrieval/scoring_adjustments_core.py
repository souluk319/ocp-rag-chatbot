# 일반 개념/문서 탐색 쿼리의 점수 조정 규칙.
from __future__ import annotations

from .models import RetrievalHit
from .scoring_signals import ScoreSignals


def apply_core_adjustments(hit: RetrievalHit, *, signals: ScoreSignals) -> None:
    lowered_text = hit.text.lower()
    lowered_section = hit.section.lower()
    context_text = signals.context_text

    if signals.generic_intro_intent:
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

    if signals.compare_intent:
        if hit.book_slug in {"architecture", "overview", "security_and_compliance"}:
            hit.fused_score *= 1.08
        if "유사점 및 차이점" in hit.section or "difference" in lowered_section or "comparison" in lowered_section:
            hit.fused_score *= 1.16
        if "쿠버네티스" in hit.text or "kubernetes" in lowered_text:
            hit.fused_score *= 1.08
        if hit.book_slug in {"tutorials", "support", "cli_tools"}:
            hit.fused_score *= 0.75

    if signals.operator_concept_intent:
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

    if signals.mco_concept_intent:
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
        pause_control_signal = (
            "자동으로 재부팅되지 않도록" in context_text
            or "spec.paused" in context_text.lower()
            or "자동으로 재부팅되지 않도록" in signals.query
            or "spec.paused" in signals.query.lower()
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
        if signals.machine_config_reboot_intent:
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
            hit.fused_score *= 0.86 if signals.machine_config_reboot_intent else 0.56

    if signals.update_doc_locator_intent:
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

    if signals.doc_locator_intent and hit.book_slug.endswith("_apis"):
        hit.fused_score *= 0.82

    if signals.certificate_monitor_intent:
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

    if signals.backup_restore_intent:
        if "cluster-backup.sh" in lowered_text:
            hit.fused_score *= 1.26
        if "oc debug --as-root node" in lowered_text or "chroot /host" in lowered_text:
            hit.fused_score *= 1.12
        if "snapshot save" in lowered_text:
            hit.fused_score *= 1.05
        if "cluster-restore.sh" in lowered_text or "restore.sh" in lowered_text:
            hit.fused_score *= 1.18
        if not signals.hosted_signal and "etcd" in context_text and hit.book_slug == "hosted_control_planes":
            hit.fused_score *= 0.24
        if hit.book_slug == "postinstallation_configuration" and (
            "etcd 작업" in hit.chapter or "이전 클러스터 상태로 복원" in hit.section
        ):
            hit.fused_score *= 1.16
        if hit.book_slug == "updating_clusters" and "업데이트 전 etcd 백업" in hit.section:
            hit.fused_score *= 0.84
        if "velero" in lowered_text or "oadp" in lowered_text or "hosted cluster" in lowered_text:
            hit.fused_score *= 0.46 if not signals.hosted_signal else 1.0
