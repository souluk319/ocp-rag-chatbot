"""playbook viewer / customer-pack helper."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import html

from play_book_studio.config.settings import load_settings
from play_book_studio.intake import CustomerPackDraftStore
from play_book_studio.intake.service import evaluate_canonical_book_quality

from .presenters import _default_customer_pack_summary
from .viewer_page import _render_page_overlay_toolbar
from .viewers import (
    _build_study_section_cards,
    _parse_viewer_path,
    _render_study_viewer_html,
)
from .wiki_user_overlay import build_wiki_overlay_signal_payload
from .wiki_relations import load_wiki_relation_assets


GOLD_CANDIDATE_BOOK_PREFIX = "/playbooks/gold-candidates/wave1"
ACTIVE_WIKI_RUNTIME_BOOK_PREFIX = "/playbooks/wiki-runtime/active"
LEGACY_WIKI_RUNTIME_BOOK_PREFIX = "/playbooks/wiki-runtime/wave1"
MARKDOWN_VIEWER_PATH_RE = re.compile(r"^/playbooks/gold-candidates/wave1/([^/]+)/index\.html$")
ACTIVE_RUNTIME_WIKI_MARKDOWN_VIEWER_PATH_RE = re.compile(r"^/playbooks/wiki-runtime/active/([^/]+)/index\.html$")
RUNTIME_WIKI_MARKDOWN_VIEWER_PATH_RE = re.compile(r"^/playbooks/wiki-runtime/([^/]+)/([^/]+)/index\.html$")
ENTITY_HUB_VIEWER_PATH_RE = re.compile(r"^/wiki/entities/([^/]+)/index\.html$")
FIGURE_VIEWER_PATH_RE = re.compile(r"^/wiki/figures/([^/]+)/([^/]+)/index\.html$")
BUYER_PACKET_VIEWER_PATH_RE = re.compile(r"^/buyer-packets/([^/]+)$")

DEFAULT_ENTITY_HUBS: dict[str, dict[str, Any]] = {
    "etcd": {
        "title": "etcd",
        "eyebrow": "Entity Hub",
        "summary": "OpenShift control plane 상태를 보존하는 핵심 key-value store다. 백업, 수동 복구, quorum 이상, static pod health와 직접 연결된다.",
        "overview": [
            "etcd 는 control plane 의 사실상 상태 저장소다.",
            "운영 관점에서는 백업, 수동 복구, member health, snapshot 검증, static pod 상태를 함께 본다.",
            "이 허브는 관련 운영 북, 장애 대응 경로, 후속 읽기 경로를 하나로 묶는다.",
        ],
        "related_books": [
            {
                "label": "Backup and Restore",
                "href": "/playbooks/wiki-runtime/active/backup_and_restore/index.html",
                "summary": "etcd 백업, 수동 복구, 복구 후 검증의 기준 문서다.",
            },
            {
                "label": "Machine Configuration",
                "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html",
                "summary": "복구 이후 node 와 MCO 상태가 정상으로 수렴하는지 확인할 때 이어진다.",
            },
            {
                "label": "Monitoring Troubleshooting",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "복구 후 cluster signal 과 operator 이상 징후를 추적할 때 이어진다.",
            },
        ],
        "next_reading_path": [
            {
                "label": "1. 백업 및 복구 절차 확인",
                "href": "/playbooks/wiki-runtime/active/backup_and_restore/index.html",
                "summary": "etcd 를 실제로 다룰 때 가장 먼저 봐야 하는 운영 경로다.",
            },
            {
                "label": "2. node / MCO 안정화 점검",
                "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html",
                "summary": "복구 이후 control plane node 구성과 rollout 상태를 확인한다.",
            },
            {
                "label": "3. 관측 신호 추적",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "alert, metrics, operator degraded 신호로 후속 이상을 추적한다.",
            },
        ],
    },
    "machine-config-operator": {
        "title": "Machine Config Operator",
        "eyebrow": "Entity Hub",
        "summary": "노드 설정, MCP rollout, 재부팅, kubelet 구성 반영을 조율하는 핵심 운영 컴포넌트다.",
        "overview": [
            "Machine Config Operator 는 node 설정 변경을 클러스터 전체에 안전하게 반영하는 control loop 다.",
            "운영 관점에서는 MCP 상태, degraded 원인, paused 여부, node rollout, reboot 흐름을 함께 본다.",
            "이 허브는 구성 변경, 설치 직후 안정화, monitoring 연계 추적을 한 곳에 묶는다.",
        ],
        "related_books": [
            {
                "label": "Machine Configuration",
                "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html",
                "summary": "MCO, MCP, node rollout, verify 절차의 기준 문서다.",
            },
            {
                "label": "Installing on Any Platform",
                "href": "/playbooks/wiki-runtime/active/installing_on_any_platform/index.html",
                "summary": "설치 직후 MCO 수렴과 bootstrap 후속 안정화 점검으로 이어진다.",
            },
            {
                "label": "Monitoring Alerts Admin Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "MCO degraded 와 node alert 를 관측 신호로 추적할 때 같이 본다.",
            },
        ],
        "next_reading_path": [
            {
                "label": "1. MCO/MCP 운영 절차 확인",
                "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html",
                "summary": "상태 확인, verify, failure signal 을 먼저 본다.",
            },
            {
                "label": "2. 설치 후 안정화 확인",
                "href": "/playbooks/wiki-runtime/active/installing_on_any_platform/index.html",
                "summary": "설치 직후 cluster baseline 이 정상인지 되짚는다.",
            },
            {
                "label": "3. alert 연계 추적",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "구성 변경이 실제 alert 로 이어졌는지 본다.",
            },
        ],
    },
    "prometheus": {
        "title": "Prometheus",
        "eyebrow": "Entity Hub",
        "summary": "OpenShift monitoring stack 의 핵심 메트릭 수집/질의 컴포넌트다. 경보, 지표 확인, troubleshooting 의 중심점이다.",
        "overview": [
            "Prometheus 는 cluster signal 을 수집하고 query 하는 핵심 monitoring 컴포넌트다.",
            "운영 관점에서는 메트릭 확인, alert 연계, scrape target 이상, operator 문제를 함께 본다.",
            "이 허브는 metrics, alerts, troubleshooting 문서를 하나의 관측 허브로 연결한다.",
        ],
        "related_books": [
            {
                "label": "Monitoring Metrics Admin Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "Prometheus 기반 메트릭 확인의 기준 문서다.",
            },
            {
                "label": "Monitoring Alerts Admin Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "메트릭 이상이 alert 로 어떻게 보이는지 연결한다.",
            },
            {
                "label": "Monitoring Troubleshooting Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "scrape target, query, operator 이상을 파고들 때 이어진다.",
            },
        ],
        "next_reading_path": [
            {
                "label": "1. 메트릭 확인",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "현재 cluster signal 을 수치로 먼저 본다.",
            },
            {
                "label": "2. alert 상태 연결",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "메트릭 이상이 실제 경보와 연결됐는지 확인한다.",
            },
            {
                "label": "3. troubleshooting 진입",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "원인 분석과 장애 대응 경로로 넘어간다.",
            },
        ],
    },
    "control-plane-nodes": {
        "title": "Control Plane Nodes",
        "eyebrow": "Entity Hub",
        "summary": "OpenShift control plane 을 실제로 호스팅하는 핵심 노드 집합이다. etcd, static pod, MCO rollout, 복구 후 검증이 모두 여기로 수렴한다.",
        "overview": [
            "Control plane node 는 cluster 의 API, scheduler, controller-manager, etcd 같은 핵심 구성요소가 실제로 돌아가는 운영 표면이다.",
            "운영 관점에서는 SSH 접근, debug shell, static pod 상태, kubelet 상태, MCO rollout, 복구 직후 health check 를 함께 본다.",
            "이 허브는 backup and restore, machine configuration, monitoring 신호를 node 관점으로 묶는다.",
        ],
        "related_books": [
            {
                "label": "Backup and Restore",
                "href": "/playbooks/wiki-runtime/active/backup_and_restore/index.html",
                "summary": "etcd 백업과 수동 복구 절차를 control plane node 작업 맥락으로 확인한다.",
            },
            {
                "label": "Machine Configuration",
                "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html",
                "summary": "MCO, MCP, node rollout 상태를 직접 검증할 때 이어진다.",
            },
            {
                "label": "Monitoring Troubleshooting Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "복구 이후 degraded signal, operator 이상, alert 신호를 node 관점으로 연결한다.",
            },
        ],
        "next_reading_path": [
            {
                "label": "1. 복구 절차 확인",
                "href": "/playbooks/wiki-runtime/active/backup_and_restore/index.html",
                "summary": "control plane node 에 들어가 실제 복구를 수행하기 전에 절차를 먼저 고정한다.",
            },
            {
                "label": "2. MCO / node rollout 확인",
                "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html",
                "summary": "복구나 변경 이후 node 구성이 정상 수렴하는지 확인한다.",
            },
            {
                "label": "3. 관측 신호 추적",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "control plane 이상이 실제 metrics, alerts, operator 상태에 어떻게 나타나는지 추적한다.",
            },
        ],
    },
    "cluster-wide-proxy": {
        "title": "Cluster-Wide Proxy",
        "eyebrow": "Entity Hub",
        "summary": "클러스터 전역 egress 경로를 제어하는 공통 프록시 설정이다. 설치 준비, debug shell, 백업/복구 전 네트워크 접근성 확인과 직접 연결된다.",
        "overview": [
            "Cluster-wide proxy 는 외부 registry, API, mirror, 패키지 접근이 프록시를 거쳐야 하는 환경에서 핵심 전역 설정이다.",
            "운영 관점에서는 설치 전 준비, debug shell 환경 변수 주입, egress 차단 원인 분석, 복구 절차 중 외부 접근성 확인을 함께 본다.",
            "이 허브는 설치 준비, 백업/복구, 후속 네트워크 구성을 하나의 탐색 축으로 묶는다.",
        ],
        "related_books": [
            {
                "label": "Installing on Any Platform",
                "href": "/playbooks/wiki-runtime/active/installing_on_any_platform/index.html",
                "summary": "프록시와 방화벽을 설치 전 인프라 준비 항목으로 고정할 때 먼저 보는 문서다.",
            },
            {
                "label": "Backup and Restore",
                "href": "/playbooks/wiki-runtime/active/backup_and_restore/index.html",
                "summary": "debug shell 안에서 proxy 환경 변수를 확인하고 복구 절차 전 네트워크 접근성을 점검할 때 이어진다.",
            },
            {
                "label": "Monitoring Troubleshooting Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "프록시 문제로 인한 external scrape, operator degraded, telemetry 이상을 추적할 때 연결한다.",
            },
        ],
        "next_reading_path": [
            {
                "label": "1. 설치 전 프록시 준비",
                "href": "/playbooks/wiki-runtime/active/installing_on_any_platform/index.html",
                "summary": "DNS, 방화벽, 외부 대상 접근 경로와 함께 프록시 기준선을 맞춘다.",
            },
            {
                "label": "2. 복구 절차 중 proxy 확인",
                "href": "/playbooks/wiki-runtime/active/backup_and_restore/index.html",
                "summary": "debug shell 과 수동 복구 절차에서 proxy 변수가 실제로 필요한지 확인한다.",
            },
            {
                "label": "3. 장애 신호 추적",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "프록시 misconfiguration 이 메트릭, alert, operator health 에 어떻게 드러나는지 본다.",
            },
        ],
    },
}

DEFAULT_CHAT_NAVIGATION_ALIASES: dict[str, list[dict[str, str]]] = {
    "etcd": [
        {"label": "etcd", "href": "/wiki/entities/etcd/index.html", "kind": "entity"},
        {"label": "Backup and Restore", "href": "/playbooks/wiki-runtime/active/backup_and_restore/index.html", "kind": "book"},
    ],
    "postinstallation_configuration": [
        {"label": "Cluster-Wide Proxy", "href": "/wiki/entities/cluster-wide-proxy/index.html", "kind": "entity"},
        {"label": "Backup and Restore", "href": "/playbooks/wiki-runtime/active/backup_and_restore/index.html", "kind": "book"},
    ],
    "machine_configuration": [
        {"label": "Machine Config Operator", "href": "/wiki/entities/machine-config-operator/index.html", "kind": "entity"},
        {"label": "Machine Configuration", "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html", "kind": "book"},
    ],
    "nodes": [
        {"label": "Control Plane Nodes", "href": "/wiki/entities/control-plane-nodes/index.html", "kind": "entity"},
        {"label": "Machine Configuration", "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html", "kind": "book"},
    ],
    "monitoring": [
        {"label": "Prometheus", "href": "/wiki/entities/prometheus/index.html", "kind": "entity"},
        {"label": "Monitoring Metrics Admin Book", "href": "/playbooks/wiki-runtime/active/monitoring/index.html", "kind": "book"},
    ],
}


def _customer_pack_boundary_payload(record: Any) -> dict[str, Any]:
    truth_label = "Customer Source-First Pack"
    boundary_badge = "Private Pack Runtime"
    evidence = {
        "source_lane": str(getattr(record, "source_lane", "") or "customer_source_first_pack"),
        "source_fingerprint": str(getattr(record, "source_fingerprint", "") or ""),
        "parser_route": str(getattr(record, "parser_route", "") or ""),
        "parser_backend": str(getattr(record, "parser_backend", "") or ""),
        "parser_version": str(getattr(record, "parser_version", "") or ""),
        "ocr_used": bool(getattr(record, "ocr_used", False)),
        "extraction_confidence": float(getattr(record, "extraction_confidence", 0.0) or 0.0),
        "tenant_id": str(getattr(record, "tenant_id", "") or ""),
        "workspace_id": str(getattr(record, "workspace_id", "") or ""),
        "approval_state": str(getattr(record, "approval_state", "") or "unreviewed"),
        "publication_state": str(getattr(record, "publication_state", "") or "draft"),
        "boundary_truth": "private_customer_pack_runtime",
        "runtime_truth_label": truth_label,
        "boundary_badge": boundary_badge,
    }
    return {
        **evidence,
        "customer_pack_evidence": evidence,
    }

DEFAULT_WIKI_CANDIDATE_RELATIONS: dict[str, dict[str, Any]] = {
    "backup_and_restore": {
        "entities": [
            {"label": "etcd", "href": "/wiki/entities/etcd/index.html"},
            {"label": "Control Plane Nodes", "href": "/wiki/entities/control-plane-nodes/index.html"},
            {"label": "Machine Configuration", "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html"},
            {"label": "Cluster-Wide Proxy", "href": "/wiki/entities/cluster-wide-proxy/index.html"},
        ],
        "related_docs": [
            {
                "label": "Installing on Any Platform",
                "href": "/playbooks/wiki-runtime/active/installing_on_any_platform/index.html",
                "summary": "UPI 설치 준비와 bootstrap 검증 경로를 먼저 확인할 때 연결한다.",
            },
            {
                "label": "Machine Configuration",
                "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html",
                "summary": "복구 후 노드 구성과 MCO 상태를 점검할 때 같이 본다.",
            },
            {
                "label": "Monitoring Troubleshooting",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "복구 이후 cluster signal 과 alert 관찰을 이어서 본다.",
            },
        ],
        "next_reading_path": [
            {
                "label": "1. 설치/구성 기준 확인",
                "href": "/playbooks/wiki-runtime/active/installing_on_any_platform/index.html",
                "summary": "복구 전후에 설치 기준선과 인프라 조건을 다시 맞춘다.",
            },
            {
                "label": "2. 노드 구성 안정화",
                "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html",
                "summary": "MCP, kubelet, daemon rollout 을 점검한다.",
            },
            {
                "label": "3. 복구 후 관측 신호 확인",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "alert, metrics, operator 상태를 기반으로 후속 이상 신호를 추적한다.",
            },
        ],
        "parent_topic": {
            "label": "Control Plane Recovery",
            "href": "/playbooks/wiki-runtime/active/backup_and_restore/index.html",
            "summary": "etcd 백업, 수동 복구, 복구 후 검증을 묶는 운영 허브다.",
        },
        "siblings": [
            {
                "label": "Installing on Any Platform",
                "href": "/playbooks/wiki-runtime/active/installing_on_any_platform/index.html",
                "summary": "클러스터 기준선과 설치 전후 검증 절차를 같이 본다.",
            },
            {
                "label": "Machine Configuration",
                "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html",
                "summary": "복구 후 MCO, MCP, node rollout 안정화를 확인한다.",
            },
        ],
    },
    "installing_on_any_platform": {
        "entities": [
            {"label": "Installer", "href": "/playbooks/wiki-runtime/active/installing_on_any_platform/index.html"},
            {"label": "Bootstrap", "href": "/playbooks/wiki-runtime/active/installing_on_any_platform/index.html#bootstrap-validation"},
            {"label": "Cluster-Wide Proxy", "href": "/wiki/entities/cluster-wide-proxy/index.html"},
            {"label": "Machine Configuration", "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html"},
            {"label": "Monitoring", "href": "/playbooks/wiki-runtime/active/monitoring/index.html"},
        ],
        "related_docs": [
            {
                "label": "Machine Configuration",
                "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html",
                "summary": "설치 직후 노드 구성과 MCO 수렴 상태를 점검할 때 같이 본다.",
            },
            {
                "label": "Backup and Restore",
                "href": "/playbooks/wiki-runtime/active/backup_and_restore/index.html",
                "summary": "설치 후 운영 단계에서 control plane 복구 경로를 준비할 때 이어서 본다.",
            },
            {
                "label": "Monitoring Troubleshooting",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "설치 이후 cluster signal 검증과 경보 추적에 연결한다.",
            },
        ],
        "next_reading_path": [
            {
                "label": "1. 노드 구성 안정화",
                "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html",
                "summary": "설치 직후 MCO와 MCP가 정상 수렴하는지 확인한다.",
            },
            {
                "label": "2. 관측 신호 확인",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "메트릭과 operator 상태로 초기 안정성을 확인한다.",
            },
            {
                "label": "3. 복구 경로 준비",
                "href": "/playbooks/wiki-runtime/active/backup_and_restore/index.html",
                "summary": "운영 이전에 etcd 백업과 수동 복구 절차를 익힌다.",
            },
        ],
        "parent_topic": {
            "label": "Cluster Provisioning",
            "href": "/playbooks/wiki-runtime/active/installing_on_any_platform/index.html",
            "summary": "UPI 설치, bootstrap 검증, 설치 후 안정화의 허브다.",
        },
        "siblings": [
            {
                "label": "Machine Configuration",
                "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html",
                "summary": "설치 이후 바로 이어지는 node 구성 점검 문서다.",
            },
            {
                "label": "Monitoring Metrics Admin Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "설치 후 cluster health를 수치로 확인할 때 함께 본다.",
            },
        ],
    },
    "machine_configuration": {
        "entities": [
            {"label": "Machine Config Operator", "href": "/wiki/entities/machine-config-operator/index.html"},
            {"label": "MachineConfigPool", "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html#mcp-status"},
            {"label": "Control Plane Nodes", "href": "/wiki/entities/control-plane-nodes/index.html"},
            {"label": "Monitoring", "href": "/playbooks/wiki-runtime/active/monitoring/index.html"},
        ],
        "related_docs": [
            {
                "label": "Installing on Any Platform",
                "href": "/playbooks/wiki-runtime/active/installing_on_any_platform/index.html",
                "summary": "설치 직후 MCO 수렴과 bootstrap 후속 점검으로 이어진다.",
            },
            {
                "label": "Backup and Restore",
                "href": "/playbooks/wiki-runtime/active/backup_and_restore/index.html",
                "summary": "복구 후 node 구성과 static pod 상태를 확인할 때 같이 본다.",
            },
            {
                "label": "Monitoring Alerts Admin Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "MCO 관련 alert 와 degraded signal 을 함께 추적한다.",
            },
        ],
        "next_reading_path": [
            {
                "label": "1. MCO/MCP 상태 확인",
                "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html#mcp-status",
                "summary": "degraded, updating, paused 상태를 먼저 확인한다.",
            },
            {
                "label": "2. 경보/메트릭 확인",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "구성 변경이 alert 로 이어지는지 바로 추적한다.",
            },
            {
                "label": "3. 복구 절차 대비",
                "href": "/playbooks/wiki-runtime/active/backup_and_restore/index.html",
                "summary": "문제가 control plane 전체로 번지기 전 복구 경로를 숙지한다.",
            },
        ],
        "parent_topic": {
            "label": "Node Configuration",
            "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html",
            "summary": "MCO, MCP, node rollout, kubelet 설정을 묶는 허브다.",
        },
        "siblings": [
            {
                "label": "Monitoring Alerts Admin Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "구성 이상이 실제 alert 로 올라오는지 같이 본다.",
            },
            {
                "label": "Monitoring Troubleshooting Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "MCO degraded 이후 follow-up 문제를 추적할 때 이어진다.",
            },
        ],
    },
    "monitoring_alerts_admin": {
        "entities": [
            {"label": "Alertmanager", "href": "/playbooks/wiki-runtime/active/monitoring/index.html"},
            {"label": "Prometheus", "href": "/wiki/entities/prometheus/index.html"},
            {"label": "ClusterOperator", "href": "/docs/ocp/4.20/ko/operators/understanding-operators/olm-understanding-operatorhub.html"},
            {"label": "Machine Configuration", "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html"},
        ],
        "related_docs": [
            {
                "label": "Monitoring Metrics Admin Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "경보가 실제 메트릭 이상과 어떻게 연결되는지 이어서 본다.",
            },
            {
                "label": "Monitoring Troubleshooting Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "경보 원인을 더 깊게 파고들 때 연결한다.",
            },
            {
                "label": "Machine Configuration",
                "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html",
                "summary": "node or MCO 관련 alert 는 구성 문서와 함께 본다.",
            },
        ],
        "next_reading_path": [
            {
                "label": "1. 메트릭 확인",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "alert 와 연결된 수치 신호를 바로 확인한다.",
            },
            {
                "label": "2. 원인 추적",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "operator, target, scrape 문제를 세부적으로 추적한다.",
            },
            {
                "label": "3. 구성 점검",
                "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html",
                "summary": "node configuration 문제인지 연결해서 확인한다.",
            },
        ],
        "parent_topic": {
            "label": "Monitoring",
            "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
            "summary": "경보, 메트릭, 트러블슈팅을 묶는 monitoring 허브다.",
        },
        "siblings": [
            {
                "label": "Monitoring Metrics Admin Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "alerts 와 같이 보는 메트릭 중심 문서다.",
            },
            {
                "label": "Monitoring Troubleshooting Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "경보 원인 분석과 장애 대응 문서다.",
            },
        ],
    },
    "monitoring_metrics_admin": {
        "entities": [
            {"label": "Prometheus", "href": "/wiki/entities/prometheus/index.html"},
            {"label": "Alertmanager", "href": "/playbooks/wiki-runtime/active/monitoring/index.html"},
            {"label": "Cluster Metrics", "href": "/playbooks/wiki-runtime/active/monitoring/index.html"},
            {"label": "Monitoring Troubleshooting", "href": "/playbooks/wiki-runtime/active/monitoring/index.html"},
        ],
        "related_docs": [
            {
                "label": "Monitoring Alerts Admin Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "메트릭 이상이 alert 로 어떻게 반영되는지 연결한다.",
            },
            {
                "label": "Monitoring Troubleshooting Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "query 결과 이상이나 target missing 상태를 추적한다.",
            },
            {
                "label": "Installing on Any Platform",
                "href": "/playbooks/wiki-runtime/active/installing_on_any_platform/index.html",
                "summary": "설치 직후 cluster 안정성 검증과 함께 본다.",
            },
        ],
        "next_reading_path": [
            {
                "label": "1. Alert 상태 연결",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "수치 이상이 실제 경보와 연결됐는지 본다.",
            },
            {
                "label": "2. 원인 분석",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "scrape target, operator, query 오류를 추적한다.",
            },
            {
                "label": "3. 설치 기준 재확인",
                "href": "/playbooks/wiki-runtime/active/installing_on_any_platform/index.html",
                "summary": "초기 cluster baseline 자체가 맞는지 되짚는다.",
            },
        ],
        "parent_topic": {
            "label": "Monitoring",
            "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
            "summary": "Prometheus 기반 메트릭 확인과 운영 해석 허브다.",
        },
        "siblings": [
            {
                "label": "Monitoring Alerts Admin Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "같은 monitoring 축의 경보 문서다.",
            },
            {
                "label": "Monitoring Troubleshooting Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "이상 신호가 있을 때 바로 이어지는 장애 대응 문서다.",
            },
        ],
    },
    "monitoring_troubleshooting": {
        "entities": [
            {"label": "Alertmanager", "href": "/playbooks/wiki-runtime/active/monitoring/index.html"},
            {"label": "Prometheus", "href": "/wiki/entities/prometheus/index.html"},
            {"label": "Cluster Monitoring Operator", "href": "/playbooks/wiki-runtime/active/monitoring/index.html"},
            {"label": "Machine Configuration", "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html"},
        ],
        "related_docs": [
            {
                "label": "Monitoring Alerts Admin Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "경보에서 들어왔을 때 가장 먼저 이어지는 문서다.",
            },
            {
                "label": "Monitoring Metrics Admin Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "장애 원인을 수치로 검증할 때 같이 본다.",
            },
            {
                "label": "Machine Configuration",
                "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html",
                "summary": "node or MCO 이슈가 원인일 때 연결된다.",
            },
        ],
        "next_reading_path": [
            {
                "label": "1. Alert 상태 확인",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "현재 어떤 경보가 active 인지 다시 확인한다.",
            },
            {
                "label": "2. Metrics 검증",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "원인 후보를 메트릭으로 확인한다.",
            },
            {
                "label": "3. Node/MCO 경로 점검",
                "href": "/playbooks/wiki-runtime/active/machine_configuration/index.html",
                "summary": "문제가 monitoring 자체가 아니라 node 구성일 수 있는지 본다.",
            },
        ],
        "parent_topic": {
            "label": "Monitoring",
            "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
            "summary": "관측 계층의 장애 원인 분석과 대응 허브다.",
        },
        "siblings": [
            {
                "label": "Monitoring Alerts Admin Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "경보 상태를 직접 보는 대응 문서다.",
            },
            {
                "label": "Monitoring Metrics Admin Book",
                "href": "/playbooks/wiki-runtime/active/monitoring/index.html",
                "summary": "메트릭 기반으로 원인을 검증하는 문서다.",
            },
        ],
    },
}

def _wiki_relation_assets() -> dict[str, dict[str, Any]]:
    return load_wiki_relation_assets()


def _entity_hubs() -> dict[str, dict[str, Any]]:
    payload = _wiki_relation_assets().get("entity_hubs")
    return payload if isinstance(payload, dict) and payload else DEFAULT_ENTITY_HUBS


def _chat_navigation_aliases() -> dict[str, list[dict[str, str]]]:
    payload = _wiki_relation_assets().get("chat_navigation_aliases")
    return payload if isinstance(payload, dict) and payload else DEFAULT_CHAT_NAVIGATION_ALIASES


def _chat_link_truth_payload(root_dir: Path, href: str, kind: str) -> dict[str, str]:
    normalized_href = str(href or "").strip()
    normalized_kind = str(kind or "").strip()
    if normalized_kind == "entity":
        return {}
    settings = load_settings(root_dir)
    if normalized_href.startswith("/playbooks/customer-packs/"):
        return {
            "source_lane": "customer_source_first_pack",
            "boundary_truth": "private_customer_pack_runtime",
            "runtime_truth_label": "Customer Source-First Pack",
            "boundary_badge": "Private Runtime",
        }
    if normalized_href.startswith("/playbooks/wiki-runtime/active/"):
        return {
            "source_lane": "approved_wiki_runtime",
            "boundary_truth": "official_validated_runtime",
            "runtime_truth_label": f"{settings.active_pack.pack_label} Runtime",
            "boundary_badge": "Validated Runtime",
        }
    return {}


def _contains_hangul(text: str) -> bool:
    return any("\uac00" <= char <= "\ud7a3" for char in str(text or ""))


def _link_book_slug(href: str) -> str:
    match = RUNTIME_WIKI_MARKDOWN_VIEWER_PATH_RE.match(str(href or "").strip())
    if match:
        return str(match.group(2) or "").strip()
    return ""


def _prefer_korean_book_links(links: list[dict[str, str]]) -> list[dict[str, str]]:
    korean_books = [
        link for link in links
        if str(link.get("kind") or "").strip() == "book" and _contains_hangul(str(link.get("label") or ""))
    ]
    if korean_books:
        return korean_books
    return links


def _is_final_runtime_href(href: str) -> bool:
    return str(href or "").strip().startswith(f"{ACTIVE_WIKI_RUNTIME_BOOK_PREFIX}/")


def _candidate_relations() -> dict[str, dict[str, Any]]:
    payload = _wiki_relation_assets().get("candidate_relations")
    return payload if isinstance(payload, dict) and payload else DEFAULT_WIKI_CANDIDATE_RELATIONS


def _figure_assets() -> dict[str, list[dict[str, Any]]]:
    payload = _wiki_relation_assets().get("figure_assets")
    return payload.get("entries", {}) if isinstance(payload, dict) and isinstance(payload.get("entries"), dict) else {}


def _figure_entity_index() -> dict[str, Any]:
    payload = _wiki_relation_assets().get("figure_entity_index")
    return payload if isinstance(payload, dict) else {}


def _figure_section_index() -> dict[str, Any]:
    payload = _wiki_relation_assets().get("figure_section_index")
    return payload if isinstance(payload, dict) else {}


def _section_relation_index() -> dict[str, Any]:
    payload = _wiki_relation_assets().get("section_relation_index")
    return payload if isinstance(payload, dict) else {}


def _figure_asset_filename(asset: dict[str, Any]) -> str:
    asset_url = str(asset.get("asset_url") or "").strip()
    return Path(urlparse(asset_url).path).name.strip()


def _figure_viewer_href(slug: str, asset: dict[str, Any]) -> str:
    viewer_path = str(asset.get("viewer_path") or "").strip()
    if viewer_path:
        return viewer_path
    asset_name = _figure_asset_filename(asset)
    if not slug or not asset_name:
        return str(asset.get("asset_url") or "").strip()
    return f"/wiki/figures/{slug}/{asset_name}/index.html"


def _figure_asset_by_name(slug: str, asset_name: str) -> dict[str, Any] | None:
    normalized_slug = str(slug or "").strip()
    normalized_asset_name = str(asset_name or "").strip()
    if not normalized_slug or not normalized_asset_name:
        return None
    for item in _figure_assets().get(normalized_slug, []):
        if not isinstance(item, dict):
            continue
        if _figure_asset_filename(item) == normalized_asset_name:
            return item
    return None


def _figure_section_match(slug: str, asset_name: str) -> dict[str, Any] | None:
    payload = _figure_section_index()
    by_slug = payload.get("by_slug") if isinstance(payload.get("by_slug"), dict) else {}
    records = by_slug.get(str(slug or "").strip())
    if not isinstance(records, list):
        return None
    normalized_asset_name = str(asset_name or "").strip()
    for item in records:
        if not isinstance(item, dict):
            continue
        if str(item.get("asset_name") or "").strip() == normalized_asset_name:
            return item
    return None


def _book_related_sections(slug: str) -> list[dict[str, Any]]:
    payload = _section_relation_index()
    by_book = payload.get("by_book") if isinstance(payload.get("by_book"), dict) else {}
    items = by_book.get(str(slug or "").strip())
    return [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []


def _entity_related_sections(entity_slug: str) -> list[dict[str, Any]]:
    payload = _section_relation_index()
    by_entity = payload.get("by_entity") if isinstance(payload.get("by_entity"), dict) else {}
    items = by_entity.get(str(entity_slug or "").strip())
    return [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []


def _wiki_relation_items(relation: dict[str, Any], key: str) -> list[dict[str, str]]:
    return [item for item in relation.get(key, []) if isinstance(item, dict)]


def _active_wiki_runtime_manifest_path(root_dir: Path) -> Path:
    return root_dir / "data" / "wiki_runtime_books" / "active_manifest.json"


def _active_wiki_runtime_manifest(root_dir: Path) -> dict[str, Any]:
    manifest_path = _active_wiki_runtime_manifest_path(root_dir)
    if not manifest_path.exists() or not manifest_path.is_file():
        return {}
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _legacy_wiki_runtime_manifest_path(root_dir: Path, group: str) -> Path:
    return root_dir / "data" / "wiki_runtime_books" / f"{group}_manifest.json"


def _legacy_wiki_runtime_manifest(root_dir: Path, group: str) -> dict[str, Any]:
    manifest_path = _legacy_wiki_runtime_manifest_path(root_dir, group)
    if not manifest_path.exists() or not manifest_path.is_file():
        return {}
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _runtime_markdown_path_from_entries(entries: list[Any], slug: str) -> Path | None:
    normalized_slug = str(slug or "").strip()
    if not normalized_slug:
        return None
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        entry_slug = str(entry.get("slug") or "").strip()
        if entry_slug != normalized_slug:
            continue
        runtime_path = Path(str(entry.get("runtime_path") or "")).resolve()
        if runtime_path.exists() and runtime_path.is_file():
            return runtime_path
    return None


def _active_runtime_markdown_path(root_dir: Path, slug: str) -> Path | None:
    payload = _active_wiki_runtime_manifest(root_dir)
    entries = payload.get("entries") if isinstance(payload.get("entries"), list) else []
    return _runtime_markdown_path_from_entries(entries, slug)


def _legacy_runtime_markdown_path(root_dir: Path, group: str, slug: str) -> Path | None:
    payload = _legacy_wiki_runtime_manifest(root_dir, group)
    entries = payload.get("entries") if isinstance(payload.get("entries"), list) else []
    return _runtime_markdown_path_from_entries(entries, slug)


def _approved_wiki_runtime_slugs(root_dir: Path) -> set[str]:
    payload = _active_wiki_runtime_manifest(root_dir)
    entries = payload.get("entries") if isinstance(payload, dict) else []
    approved: set[str] = set()
    if not isinstance(entries, list):
        return approved
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        slug = str(entry.get("slug") or "").strip()
        if slug:
            approved.add(slug)
    return approved


def _preferred_book_href(root_dir: Path, slug: str) -> str:
    normalized = str(slug or "").strip()
    if not normalized:
        return ""
    if normalized in _approved_wiki_runtime_slugs(root_dir):
        return f"{ACTIVE_WIKI_RUNTIME_BOOK_PREFIX}/{normalized}/index.html"
    settings = load_settings(root_dir)
    return f"/docs/ocp/{settings.ocp_version}/{settings.docs_language}/{normalized}/index.html"


def _rewrite_book_href(root_dir: Path, href: str) -> str:
    normalized = str(href or "").strip()
    if normalized.startswith("/docs/ocp/"):
        parsed = urlparse(normalized)
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) >= 5 and parts[-1] == "index.html":
            slug = parts[-2]
            anchor = parsed.fragment
            rewritten = _preferred_book_href(root_dir, slug)
            if anchor:
                rewritten = f"{rewritten}#{anchor}"
            return rewritten
    if normalized.startswith(f"{GOLD_CANDIDATE_BOOK_PREFIX}/") or normalized.startswith(f"{LEGACY_WIKI_RUNTIME_BOOK_PREFIX}/"):
        parts = [part for part in normalized.split("/") if part]
        if len(parts) >= 4:
            slug = parts[-2]
            return _preferred_book_href(root_dir, slug)
    return normalized


def _relation_href_matches_slug(href: str, slug: str) -> bool:
    normalized = str(href or "").strip()
    docs_pattern = re.compile(rf"^/docs/ocp/[^/]+/[^/]+/{re.escape(slug)}/index\.html$")
    return normalized in {
        f"{GOLD_CANDIDATE_BOOK_PREFIX}/{slug}/index.html",
        f"{ACTIVE_WIKI_RUNTIME_BOOK_PREFIX}/{slug}/index.html",
        f"{LEGACY_WIKI_RUNTIME_BOOK_PREFIX}/{slug}/index.html",
    } or bool(docs_pattern.match(normalized))


def _build_backlinks(root_dir: Path, slug: str) -> list[dict[str, str]]:
    backlinks: list[dict[str, str]] = []
    seen: set[str] = set()
    for source_slug, relation in _candidate_relations().items():
        if source_slug == slug:
            continue
        for item in _wiki_relation_items(relation, "related_docs") + _wiki_relation_items(relation, "next_reading_path") + _wiki_relation_items(relation, "siblings"):
            href = str(item.get("href") or "").strip()
            if not _relation_href_matches_slug(href, slug):
                continue
            if source_slug in seen:
                continue
            seen.add(source_slug)
            backlinks.append(
                {
                    "label": source_slug.replace("_", " ").title(),
                    "href": _preferred_book_href(root_dir, source_slug),
                    "summary": str(item.get("summary") or "").strip() or "이 문서에서 현재 문서로 이동한다.",
                }
            )
    return backlinks


def _build_entity_backlinks(root_dir: Path, entity_slug: str) -> list[dict[str, str]]:
    target_path = f"/wiki/entities/{entity_slug}/index.html"
    backlinks: list[dict[str, str]] = []
    seen: set[str] = set()
    for source_slug, relation in _candidate_relations().items():
        for item in _wiki_relation_items(relation, "entities"):
            href = str(item.get("href") or "").strip()
            if href != target_path or source_slug in seen:
                continue
            seen.add(source_slug)
            backlinks.append(
                {
                    "label": source_slug.replace("_", " ").title(),
                    "href": _preferred_book_href(root_dir, source_slug),
                    "summary": f"{item.get('label') or entity_slug} 엔터티를 이 문서에서 직접 다룬다.",
                }
            )
    return backlinks


def _entity_hub_sections(entity_slug: str) -> list[dict[str, Any]]:
    entity = _entity_hubs().get(entity_slug)
    if entity is None:
        return []
    overview_text = "\n\n".join(
        str(item).strip() for item in entity.get("overview", []) if str(item).strip()
    )
    navigation_text = "\n\n".join(
        [
            "이 엔터티는 절차 문서, 장애 대응 문서, 상위 운영 문서 사이의 연결 허브다.",
            "관련 북, 역참조 문서, 연계 섹션을 함께 볼 수 있다.",
            "연결 구조를 따라 필요한 문서와 경로를 탐색한다.",
        ]
    )
    title = str(entity.get("title") or entity_slug)
    return [
        {
            "anchor": "overview",
            "heading": "Overview",
            "section_path": [title, "Overview"],
            "text": overview_text,
            "blocks": [],
        },
        {
            "anchor": "how-to-navigate",
            "heading": "How To Navigate",
            "section_path": [title, "How To Navigate"],
            "text": navigation_text,
            "blocks": [],
        },
    ]


def _build_entity_hub_supplementary_blocks(root_dir: Path, entity_slug: str) -> list[str]:
    entity = _entity_hubs().get(entity_slug)
    if entity is None:
        return []
    related_books = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in entity.get("related_books", [])
        if isinstance(item, dict)
    )
    next_path_links = "".join(
        """
        <div class="wiki-path">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in entity.get("next_reading_path", [])
        if isinstance(item, dict)
    )
    backlinks = _build_entity_backlinks(root_dir, entity_slug)
    figure_index = _figure_entity_index()
    related_figures = figure_index.get("by_entity", {}).get(entity_slug, []) if isinstance(figure_index.get("by_entity"), dict) else []
    related_sections = _entity_related_sections(entity_slug)
    backlink_links = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(str(item.get("href") or ""), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in backlinks
    )
    figure_links = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(str(item.get("viewer_path") or item.get("asset_url") or ""), quote=True),
            label=html.escape(str(item.get("caption") or "Figure")),
            summary=html.escape(
                "{book} · {section}".format(
                    book=str(item.get("book_title") or item.get("book_slug") or "").strip() or "related book",
                    section=str(item.get("section_hint") or "unmatched").strip() or "unmatched",
                )
            ),
        ).strip()
        for item in related_figures[:6]
        if isinstance(item, dict)
    )
    section_links = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in related_sections[:6]
        if isinstance(item, dict)
    )
    return [
        """
        <section class="wiki-parent-card">
          <div class="wiki-parent-eyebrow">Entity Hub</div>
          <a href="/wiki/entities/{entity_slug}/index.html">{title}</a>
          <p>{summary}</p>
        </section>
        <section class="wiki-grid wiki-grid-primary">
          <article class="wiki-card wiki-card-primary">
            <h3>Recommended Path</h3>
            {next_path_links}
          </article>
          <article class="wiki-card wiki-card-primary">
            <h3>Connections</h3>
            <div class="wiki-card-stack">
              <div>
                <h4>Books</h4>
                {related_books}
              </div>
              <div>
                <h4>Referenced By</h4>
                {backlink_links}
              </div>
            </div>
          </article>
        </section>
        <details class="wiki-details">
          <summary>More</summary>
          <section class="wiki-grid wiki-grid-secondary">
            <article class="wiki-card">
              <h3>Related Figures</h3>
              {figure_links}
            </article>
            <article class="wiki-card">
              <h3>Related Sections</h3>
              {section_links}
            </article>
          </section>
        </details>
        """.format(
            entity_slug=html.escape(entity_slug, quote=True),
            title=html.escape(str(entity.get("title") or entity_slug)),
            summary=html.escape(str(entity.get("summary") or "")),
            related_books=related_books or '<div class="wiki-empty">연결된 북이 아직 없습니다.</div>',
            next_path_links=next_path_links or '<div class="wiki-empty">연결된 경로가 아직 없습니다.</div>',
            backlink_links=backlink_links or '<div class="wiki-empty">이 엔터티를 참조하는 문서가 아직 없습니다.</div>',
            figure_links=figure_links or '<div class="wiki-empty">연결된 figure 자산이 아직 없습니다.</div>',
            section_links=section_links or '<div class="wiki-empty">연결된 절차 섹션이 아직 없습니다.</div>',
        ).strip()
    ]


def _overlay_recent_target_scores(
    root_dir: Path,
    *,
    user_id: str | None = None,
) -> tuple[dict[str, int], dict[str, int]]:
    normalized_user_id = str(user_id or "").strip()
    if not normalized_user_id:
        return {}, {}
    try:
        payload = build_wiki_overlay_signal_payload(root_dir, user_id=normalized_user_id)
    except Exception:  # noqa: BLE001
        return {}, {}
    user_focus = payload.get("user_focus") if isinstance(payload, dict) else None
    recent_targets = user_focus.get("recent_targets") if isinstance(user_focus, dict) else None
    if not isinstance(recent_targets, list):
        return {}, {}
    href_scores: dict[str, int] = {}
    ref_scores: dict[str, int] = {}
    for index, item in enumerate(recent_targets[:12]):
        if not isinstance(item, dict):
            continue
        base_score = max(10, 80 - index * 6)
        href = _rewrite_book_href(root_dir, str(item.get("href") or "").strip())
        target_ref = str(item.get("target_ref") or "").strip()
        if href:
            href_scores[href] = max(href_scores.get(href, 0), base_score)
        if target_ref:
            ref_scores[target_ref] = max(ref_scores.get(target_ref, 0), base_score)
    return href_scores, ref_scores


def _link_target_ref(kind: str, href: str) -> str:
    normalized_kind = str(kind or "").strip()
    normalized_href = str(href or "").strip()
    parsed = urlparse(normalized_href)
    request_path = parsed.path.strip()
    entity_match = ENTITY_HUB_VIEWER_PATH_RE.match(request_path)
    if entity_match:
        return f"entity:{entity_match.group(1)}"
    figure_match = FIGURE_VIEWER_PATH_RE.match(request_path)
    if figure_match:
        return f"figure:{figure_match.group(1)}:{figure_match.group(2)}"
    active_book_match = ACTIVE_RUNTIME_WIKI_MARKDOWN_VIEWER_PATH_RE.match(request_path)
    if active_book_match:
        slug = active_book_match.group(1)
        if normalized_kind == "section":
            anchor = parsed.fragment.strip()
            if anchor:
                return f"section:{slug}#{anchor}"
        return f"book:{slug}"
    runtime_book_match = RUNTIME_WIKI_MARKDOWN_VIEWER_PATH_RE.match(request_path)
    if runtime_book_match:
        slug = runtime_book_match.group(2)
        if normalized_kind == "section":
            anchor = parsed.fragment.strip()
            if anchor:
                return f"section:{slug}#{anchor}"
        return f"book:{slug}"
    gold_book_match = MARKDOWN_VIEWER_PATH_RE.match(request_path)
    if gold_book_match:
        slug = gold_book_match.group(1)
        if normalized_kind == "section":
            anchor = parsed.fragment.strip()
            if anchor:
                return f"section:{slug}#{anchor}"
        return f"book:{slug}"
    return ""


def build_chat_navigation_links(
    root_dir: Path,
    citations: list[dict[str, Any]] | list[Any],
    *,
    user_id: str | None = None,
) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    seen: set[str] = set()
    slug_seen: set[str] = set()
    semantic_seen: set[str] = set()
    alias_map = _chat_navigation_aliases()
    relation_map = _candidate_relations()
    href_scores, ref_scores = _overlay_recent_target_scores(root_dir, user_id=user_id)

    def duplicate_semantic(label: str, kind: str) -> bool:
        normalized = re.sub(r"\s+", " ", str(label or "").strip().lower())
        if not normalized:
            return False
        keys = {normalized, f"{kind}:{normalized}"}
        if any(key in semantic_seen for key in keys):
            return True
        semantic_seen.update(keys)
        return False

    for citation in citations:
        if not isinstance(citation, dict):
            continue
        slug = str(citation.get("book_slug") or "").strip()
        if slug and slug in alias_map:
            for item in alias_map.get(slug, []):
                kind = str(item.get("kind") or "book")
                if kind != "book":
                    continue
                href = str(item.get("href") or "").strip()
                label = str(item.get("label") or "").strip()
                rewritten_href = _rewrite_book_href(root_dir, href)
                book_slug = _link_book_slug(rewritten_href)
                if (
                    not href
                    or not label
                    or not _is_final_runtime_href(rewritten_href)
                    or rewritten_href in seen
                    or (book_slug and book_slug in slug_seen)
                    or duplicate_semantic(label, kind)
                ):
                    continue
                seen.add(rewritten_href)
                if book_slug:
                    slug_seen.add(book_slug)
                links.append(
                    {
                        "label": label,
                        "href": rewritten_href,
                        "kind": kind,
                        **_chat_link_truth_payload(root_dir, rewritten_href, kind),
                    }
                )
        relation = relation_map.get(slug) if slug else None
        if relation is None and not slug:
            continue
        if relation is None:
            excerpt = str(citation.get("excerpt") or "")
            section = str(citation.get("section") or "")
            haystack = f"{slug} {section} {excerpt}".lower()
            if "etcd" in haystack:
                relation = relation_map.get("backup_and_restore")
            elif "machine config" in haystack or "mco" in haystack:
                relation = relation_map.get("machine_configuration")
            elif "prometheus" in haystack or "alert" in haystack or "monitoring" in haystack:
                relation = relation_map.get("monitoring_troubleshooting")
        if relation is None:
            continue
        for item in _wiki_relation_items(relation, "related_docs")[:2]:
            href = str(item.get("href") or "").strip()
            label = str(item.get("label") or "").strip()
            rewritten_href = _rewrite_book_href(root_dir, href)
            book_slug = _link_book_slug(rewritten_href)
            if (
                not href
                or not label
                or not _is_final_runtime_href(rewritten_href)
                or rewritten_href in seen
                or (book_slug and book_slug in slug_seen)
                or duplicate_semantic(label, "book")
            ):
                continue
            seen.add(rewritten_href)
            if book_slug:
                slug_seen.add(book_slug)
            links.append(
                {
                    "label": label,
                    "href": rewritten_href,
                    "kind": "book",
                    **_chat_link_truth_payload(root_dir, rewritten_href, "book"),
                }
            )
        if len(links) >= 2:
            break
    links = _prefer_korean_book_links(links)
    ranked_links = sorted(
        links,
        key=lambda item: (
            -max(
                href_scores.get(str(item.get("href") or "").strip(), 0),
                ref_scores.get(
                    _link_target_ref(
                        str(item.get("kind") or "").strip(),
                        str(item.get("href") or "").strip(),
                    ),
                    0,
                ),
            ),
            0 if _contains_hangul(str(item.get("label") or "")) else 1,
            str(item.get("label") or ""),
        ),
    )
    return ranked_links[:2]


_SECTION_TOKEN_RE = re.compile(r"[0-9A-Za-z가-힣_-]+")


def _tokenize_section_text(*parts: str) -> set[str]:
    tokens: set[str] = set()
    for part in parts:
        for token in _SECTION_TOKEN_RE.findall(str(part or "").lower()):
            normalized = token.strip("-_ ")
            if len(normalized) >= 2:
                tokens.add(normalized)
    return tokens


def _section_link_score(item: dict[str, Any], citation: dict[str, Any]) -> int:
    score = 0
    item_href = str(item.get("href") or "").strip()
    item_label = str(item.get("label") or "").strip()
    item_summary = str(item.get("summary") or "").strip()
    citation_href = str(citation.get("href") or "").strip()
    citation_section = str(citation.get("section") or "").strip()
    citation_excerpt = str(citation.get("excerpt") or "").strip()
    citation_source_label = str(citation.get("source_label") or "").strip()

    if citation_href and item_href == citation_href:
        score += 1000
    if citation_section and item_label:
        lowered_section = citation_section.lower()
        lowered_label = item_label.lower()
        if lowered_section == lowered_label:
            score += 300
        elif lowered_section in lowered_label or lowered_label in lowered_section:
            score += 120

    citation_tokens = _tokenize_section_text(citation_section, citation_excerpt, citation_source_label)
    item_tokens = _tokenize_section_text(item_label, item_summary)
    overlap = citation_tokens & item_tokens
    score += len(overlap) * 15

    if citation_excerpt and item_summary:
        lowered_excerpt = citation_excerpt.lower()
        lowered_summary = item_summary.lower()
        if lowered_summary and lowered_summary in lowered_excerpt:
            score += 40
        elif lowered_excerpt and lowered_excerpt[:80] in lowered_summary:
            score += 20

    return score


def build_chat_section_links(
    root_dir: Path,
    citations: list[dict[str, Any]] | list[Any],
    *,
    user_id: str | None = None,
) -> list[dict[str, str]]:
    candidates: dict[str, dict[str, Any]] = {}
    label_seen: set[str] = set()
    slug_seen: set[str] = set()
    href_scores, ref_scores = _overlay_recent_target_scores(root_dir, user_id=user_id)
    for citation in citations:
        if not isinstance(citation, dict):
            continue
        slug = str(citation.get("book_slug") or "").strip()
        if not slug:
            continue
        citation_href = str(citation.get("href") or "").strip()
        citation_section = str(citation.get("section") or "").strip()
        if citation_href and citation_section:
            rewritten_citation_href = _rewrite_book_href(root_dir, citation_href)
            if _is_final_runtime_href(rewritten_citation_href) and _contains_hangul(citation_section):
                direct_candidate = {
                    "label": citation_section,
                    "href": rewritten_citation_href,
                    "kind": "section",
                    "summary": str(citation.get("source_label") or "").strip(),
                }
                candidates[rewritten_citation_href] = {
                    **direct_candidate,
                    "_score": max(int(candidates.get(rewritten_citation_href, {}).get("_score", 0)), 1500),
                }
        for item in _book_related_sections(slug):
            href = str(item.get("href") or "").strip()
            label = str(item.get("label") or "").strip()
            if not href or not label:
                continue
            score = _section_link_score(item, citation)
            current = candidates.get(href)
            rewritten_href = _rewrite_book_href(root_dir, href)
            if not _is_final_runtime_href(rewritten_href) or not _contains_hangul(label):
                continue
            if current is None or score > int(current.get("_score", 0)):
                candidates[href] = {
                    "label": label,
                    "href": rewritten_href,
                    "kind": "section",
                    "summary": str(item.get("summary") or "").strip(),
                    "_score": score,
                }
    ranked = sorted(
        candidates.values(),
        key=lambda item: (
            -max(
                int(item.get("_score", 0)),
                href_scores.get(str(item.get("href") or "").strip(), 0),
                ref_scores.get(
                    _link_target_ref(
                        "section",
                        str(item.get("href") or "").strip(),
                    ),
                    0,
                ),
            ),
            str(item.get("label") or ""),
        ),
    )
    links: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in ranked:
        href = str(item.get("href") or "").strip()
        label = str(item.get("label") or "").strip()
        normalized_label = re.sub(r"\s+", " ", label.lower())
        book_slug = _link_book_slug(href)
        if (
            not href
            or href in seen
            or (normalized_label and normalized_label in label_seen)
            or (book_slug and book_slug in slug_seen)
        ):
            continue
        seen.add(href)
        if normalized_label:
            label_seen.add(normalized_label)
        if book_slug:
            slug_seen.add(book_slug)
        links.append(
            {
                "label": label,
                "href": href,
                "kind": "section",
                "summary": str(item.get("summary") or "").strip(),
            }
        )
        if len(links) >= 2:
            break
    return links


def _playbook_book_path(root_dir: Path, book_slug: str) -> Path:
    settings = load_settings(root_dir)
    return settings.playbook_books_dir / f"{book_slug}.json"


def _playbook_book_candidates(root_dir: Path, book_slug: str) -> tuple[Path, ...]:
    settings = load_settings(root_dir)
    return tuple(directory / f"{book_slug}.json" for directory in settings.playbook_book_dirs)


def _load_playbook_book(root_dir: Path, book_slug: str) -> dict[str, Any] | None:
    for path in _playbook_book_candidates(root_dir, book_slug):
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    return None


def _playbook_viewer_chrome(playbook_book: dict[str, Any]) -> tuple[str, str]:
    source_metadata = (
        playbook_book.get("source_metadata")
        if isinstance(playbook_book.get("source_metadata"), dict)
        else {}
    )
    source_type = str(source_metadata.get("source_type") or "").strip()
    if source_type == "topic_playbook":
        summary = str(playbook_book.get("topic_summary") or "").strip()
        if not summary:
            parent_title = str(source_metadata.get("derived_from_title") or "").strip()
            if parent_title:
                summary = f"{parent_title}에서 실행 절차만 추린 토픽 플레이북입니다."
            else:
                summary = "실행 절차 중심으로 다시 엮은 토픽 플레이북입니다."
        return "Topic Playbook", summary
    return "Manual Book", "정리된 AST 기준의 유저용 매뉴얼북을 보여줍니다."


def internal_viewer_html(root_dir: Path, viewer_path: str) -> str | None:
    parsed = _parse_viewer_path(viewer_path)
    if parsed is None:
        return None

    request = urlparse((viewer_path or "").strip())
    embedded = "embed=1" in request.query
    book_slug, target_anchor = parsed
    playbook_book = _load_playbook_book(root_dir, book_slug)
    if playbook_book is None:
        return None
    sections = [dict(section) for section in (playbook_book.get("sections") or []) if isinstance(section, dict)]
    if not sections:
        return None
    book_title = str(playbook_book.get("title") or book_slug)
    source_url = str(playbook_book.get("source_uri") or "")
    eyebrow, summary = _playbook_viewer_chrome(playbook_book)

    cards = _build_study_section_cards(sections, book_slug=book_slug, target_anchor=target_anchor, embedded=embedded)
    return _render_study_viewer_html(
        title=book_title,
        source_url=source_url,
        cards=cards,
        section_count=len(sections),
        eyebrow=eyebrow,
        summary=summary,
        embedded=embedded,
        page_overlay_toolbar=_render_page_overlay_toolbar(
            target_kind="book",
            target_ref=f"book:{book_slug}",
            title=book_title,
            book_slug=book_slug,
            viewer_path=f"/docs/ocp/{load_settings(root_dir).ocp_version}/{load_settings(root_dir).docs_language}/{book_slug}/index.html",
        ),
    )


def _parse_markdown_heading(line: str) -> tuple[int, str] | None:
    stripped = line.strip()
    if not stripped.startswith("#"):
        return None
    level = len(stripped) - len(stripped.lstrip("#"))
    if level < 1 or level > 6:
        return None
    title = stripped[level:].strip()
    if not title:
        return None
    return level, title


def _anchorify_heading(text: str) -> str:
    normalized = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    normalized = re.sub(r"[\s_]+", "-", normalized)
    return normalized or "section"


def _markdown_sections(markdown_text: str) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    path_stack: list[str] = []
    for raw_line in markdown_text.splitlines():
        heading = _parse_markdown_heading(raw_line)
        if heading is not None:
            level, title = heading
            while len(path_stack) >= level:
                path_stack.pop()
            path_stack.append(title)
            current = {
                "anchor": _anchorify_heading(title),
                "heading": title,
                "section_path": list(path_stack),
                "text": "",
                "blocks": [],
            }
            sections.append(current)
            continue
        if current is None:
            continue
        current["text"] = f"{current['text']}\n{raw_line}".strip()
    return [section for section in sections if str(section.get("text") or "").strip() or str(section.get("heading") or "").strip()]


def _markdown_summary(sections: list[dict[str, Any]]) -> str:
    for section in sections:
        raw_text = str(section.get("text") or "").strip()
        if not raw_text:
            continue
        paragraph = raw_text.split("\n\n", 1)[0].strip()
        paragraph = re.sub(r"\s+", " ", paragraph)
        if len(paragraph) > 180:
            paragraph = paragraph[:177].rstrip() + "..."
        if paragraph:
            return paragraph
    return ""


def _trim_leading_title_section(sections: list[dict[str, Any]], *, title: str) -> list[dict[str, Any]]:
    if not sections:
        return sections
    first = sections[0]
    first_heading = str(first.get("heading") or "").strip()
    if first_heading != str(title or "").strip():
        return sections
    section_path = [str(item).strip() for item in (first.get("section_path") or []) if str(item).strip()]
    if len(section_path) != 1:
        return sections
    remaining = sections[1:]
    if not remaining:
        return sections
    carry_text = str(first.get("text") or "").strip()
    if not carry_text:
        return remaining
    merged_first = dict(remaining[0])
    next_text = str(merged_first.get("text") or "").strip()
    merged_first["text"] = f"{carry_text}\n\n{next_text}".strip() if next_text else carry_text
    return [merged_first, *remaining[1:]]


def _build_wiki_supplementary_blocks(root_dir: Path, slug: str) -> list[str]:
    relation = _candidate_relations().get(slug)
    if relation is None:
        return []
    figure_assets = [item for item in _figure_assets().get(slug, []) if isinstance(item, dict)]
    related_sections = _book_related_sections(slug)
    parent_topic = relation.get("parent_topic") if isinstance(relation.get("parent_topic"), dict) else None
    sibling_links = _wiki_relation_items(relation, "siblings")
    backlinks = _build_backlinks(root_dir, slug)
    entity_links = "".join(
        f'<a href="{html.escape(_rewrite_book_href(root_dir, item["href"]), quote=True)}">{html.escape(item["label"])}</a>'
        for item in relation.get("entities", [])
        if isinstance(item, dict)
    )
    related_links = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in relation.get("related_docs", [])
        if isinstance(item, dict)
    )
    next_path_links = "".join(
        """
        <div class="wiki-path">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in relation.get("next_reading_path", [])
        if isinstance(item, dict)
    )
    backlink_links = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in backlinks
    )
    sibling_blocks = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in sibling_links
    )
    figure_blocks = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_figure_viewer_href(slug, item), quote=True),
            label=html.escape(str(item.get("caption") or "Figure")),
            summary=html.escape(
                "section: {section} · entities: {entities}".format(
                    section=str(item.get("section_hint") or "unmatched").strip() or "unmatched",
                    entities=", ".join(
                        str(entity.get("label") or "").strip()
                        for entity in (item.get("related_entities") or [])
                        if isinstance(entity, dict) and str(entity.get("label") or "").strip()
                    ) or "none",
                )
            ),
        ).strip()
        for item in figure_assets[:6]
        if str(item.get("asset_url") or "").strip()
    )
    section_blocks = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in related_sections[:6]
        if isinstance(item, dict)
    )
    parent_block = ""
    if parent_topic:
        parent_block = """
        <section class="wiki-parent-card">
          <div class="wiki-parent-eyebrow">Topic</div>
          <a href="{href}">{label}</a>
          <p>{summary}</p>
        </section>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(parent_topic.get("href") or "")), quote=True),
            label=html.escape(str(parent_topic.get("label") or "")),
            summary=html.escape(str(parent_topic.get("summary") or "")),
        ).strip()
    return [
        """
        {parent_block}
        <section class="wiki-grid wiki-grid-primary">
          <article class="wiki-card wiki-card-primary">
            <h3>Recommended Path</h3>
            {next_path_links}
          </article>
          <article class="wiki-card wiki-card-primary">
            <h3>Connections</h3>
            <div class="wiki-card-stack">
              <div>
                <h4>Entities</h4>
                <div class="wiki-entity-list">{entity_links}</div>
              </div>
              <div>
                <h4>Documents</h4>
                {related_links}
              </div>
            </div>
          </article>
        </section>
        <details class="wiki-details">
          <summary>More</summary>
          <section class="wiki-grid wiki-grid-secondary">
            <article class="wiki-card">
              <h3>Referenced By</h3>
              {backlink_links}
            </article>
            <article class="wiki-card">
              <h3>Sibling Tasks</h3>
              {sibling_blocks}
            </article>
            <article class="wiki-card">
              <h3>Related Figures</h3>
              {figure_blocks}
            </article>
            <article class="wiki-card">
              <h3>Related Sections</h3>
              {section_blocks}
            </article>
          </section>
        </details>
        """.format(
            parent_block=parent_block,
            entity_links=entity_links or '<div class="wiki-empty">핵심 엔터티 연결이 아직 없습니다.</div>',
            related_links=related_links or '<div class="wiki-empty">연결된 문서가 아직 없습니다.</div>',
            next_path_links=next_path_links or '<div class="wiki-empty">연결된 경로가 아직 없습니다.</div>',
            backlink_links=backlink_links or '<div class="wiki-empty">아직 연결된 역방향 문서가 없습니다.</div>',
            sibling_blocks=sibling_blocks or '<div class="wiki-empty">같은 작업군 문서는 아직 준비 중입니다.</div>',
            figure_blocks=figure_blocks or '<div class="wiki-empty">연결된 figure 자산이 아직 없습니다.</div>',
            section_blocks=section_blocks or '<div class="wiki-empty">연결된 절차 섹션이 아직 없습니다.</div>',
        ).strip()
    ]


def parse_gold_candidate_markdown_viewer_path(viewer_path: str) -> tuple[str, str, str | None] | None:
    parsed = urlparse((viewer_path or "").strip())
    active_runtime_match = ACTIVE_RUNTIME_WIKI_MARKDOWN_VIEWER_PATH_RE.fullmatch(parsed.path.strip())
    if active_runtime_match is not None:
        return ("runtime", active_runtime_match.group(1), "active")
    return None


def parse_entity_hub_viewer_path(viewer_path: str) -> str | None:
    parsed = urlparse((viewer_path or "").strip())
    match = ENTITY_HUB_VIEWER_PATH_RE.fullmatch(parsed.path.strip())
    if match is None:
        return None
    return match.group(1)


def parse_figure_viewer_path(viewer_path: str) -> tuple[str, str] | None:
    parsed = urlparse((viewer_path or "").strip())
    match = FIGURE_VIEWER_PATH_RE.fullmatch(parsed.path.strip())
    if match is None:
        return None
    return match.group(1), match.group(2)


def parse_buyer_packet_viewer_path(viewer_path: str) -> str | None:
    parsed = urlparse((viewer_path or "").strip())
    match = BUYER_PACKET_VIEWER_PATH_RE.fullmatch(parsed.path.strip())
    if match is None:
        return None
    return match.group(1)


def _load_buyer_packet_bundle(root_dir: Path) -> dict[str, Any] | None:
    path = root_dir / "reports" / "build_logs" / "buyer_packet_bundle_index.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_buyer_packet_entry(root_dir: Path, packet_id: str) -> tuple[dict[str, Any], dict[str, Any]] | None:
    bundle = _load_buyer_packet_bundle(root_dir)
    if bundle is None:
        return None
    packets = bundle.get("packets") if isinstance(bundle.get("packets"), list) else []
    match = next(
        (
            item for item in packets
            if isinstance(item, dict) and str(item.get("id") or "").strip() == packet_id
        ),
        None,
    )
    if not isinstance(match, dict):
        return None
    return bundle, match


def _build_buyer_packet_supplementary_blocks(bundle: dict[str, Any], packet: dict[str, Any]) -> list[str]:
    stage = str(bundle.get("current_stage") or "").strip()
    commercial_truth = str(bundle.get("commercial_truth") or "").strip()
    purpose = str(packet.get("purpose") or "").strip()
    related_packets = [
        item for item in (bundle.get("packets") or [])
        if isinstance(item, dict) and str(item.get("id") or "").strip() != str(packet.get("id") or "").strip()
    ]
    related_links = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(f"/buyer-packets/{str(item.get('id') or '').strip()}", quote=True),
            label=html.escape(str(item.get("title") or "")),
            summary=html.escape(str(item.get("purpose") or "")),
        ).strip()
        for item in related_packets[:4]
    )
    pills = "".join(
        f'<span class="meta-pill">{html.escape(bit)}</span>'
        for bit in [
            "Release Packet",
            stage if stage else "",
            "ready" if str(packet.get("status") or "") == "ok" else str(packet.get("status") or ""),
        ]
        if bit
    )
    return [
        """
        <section class="wiki-parent-card">
          <div class="wiki-parent-eyebrow">Release Packet</div>
          <div class="viewer-truth-topline">
            <span class="viewer-truth-badge">Release Packet</span>
            <a class="viewer-truth-link" href="/playbook-library">Playbook Library</a>
          </div>
          <div class="viewer-truth-title">{title}</div>
          <p>{summary}</p>
          <div class="wiki-entity-list">{pills}</div>
        </section>
        <section class="wiki-grid">
          <article class="wiki-card">
            <h3>Commercial Truth</h3>
            <div class="wiki-links">
              <a href="/playbook-library">Current Stage</a>
              <span>{commercial_truth}</span>
            </div>
          </article>
          <article class="wiki-card">
            <h3>Related Packets</h3>
            {related_links}
          </article>
        </section>
        """.format(
            title=html.escape(str(packet.get("title") or "")),
            summary=html.escape(purpose or "현재 판매/데모/릴리스 기준선을 고정하는 packet."),
            pills=pills or '<span class="meta-pill">Release Packet</span>',
            commercial_truth=html.escape(commercial_truth or "current commercial truth unavailable"),
            related_links=related_links or '<div class="wiki-empty">연결된 release packet 이 아직 없습니다.</div>',
        ).strip()
    ]


def _figure_viewer_sections(slug: str, asset_name: str, asset: dict[str, Any]) -> list[dict[str, Any]]:
    caption = str(asset.get("caption") or asset.get("alt") or asset_name).strip() or asset_name
    asset_url = str(asset.get("asset_url") or "").strip()
    source_file = Path(str(asset.get("source_file") or "").strip()).name
    source_asset_ref = str(asset.get("source_asset_ref") or "").strip()
    section_hint = str(asset.get("section_hint") or "").strip()
    visual_text = "\n".join(
        [
            f"![{caption}]({asset_url})" if asset_url else "",
            "",
            caption,
            "",
            f"이 figure 는 `{slug}` 문서의 시각 자산이다.",
            f"섹션 힌트: {section_hint or 'unmatched'}",
        ]
    ).strip()
    source_text = "\n".join(
        [
            f"원본 파일: `{source_file}`" if source_file else "",
            f"원본 자산: `{source_asset_ref}`" if source_asset_ref else "",
        ]
    ).strip()
    return [
        {
            "anchor": "visual",
            "heading": "Figure",
            "section_path": [caption, "Figure"],
            "text": visual_text,
            "blocks": [],
        },
        {
            "anchor": "source-trace",
            "heading": "Source Trace",
            "section_path": [caption, "Source Trace"],
            "text": source_text,
            "blocks": [],
        },
    ]


def _build_figure_supplementary_blocks(root_dir: Path, slug: str, asset_name: str, asset: dict[str, Any]) -> list[str]:
    relation = _candidate_relations().get(slug, {})
    section_match = _figure_section_match(slug, asset_name)
    parent_title = slug.replace("_", " ").title()
    parent_summary = "이 figure 가 포함된 부모 북으로 돌아간다."
    related_entities = [
        item for item in (asset.get("related_entities") or [])
        if isinstance(item, dict) and str(item.get("href") or "").strip()
    ]
    related_entity_links = "".join(
        f'<a href="{html.escape(str(item.get("href") or ""), quote=True)}">{html.escape(str(item.get("label") or ""))}</a>'
        for item in related_entities
    )
    related_books = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in _wiki_relation_items(relation, "related_docs")
    )
    next_path_links = "".join(
        """
        <div class="wiki-path">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in _wiki_relation_items(relation, "next_reading_path")
    )
    sibling_figures = [
        item for item in _figure_assets().get(slug, [])
        if isinstance(item, dict) and _figure_asset_filename(item) != asset_name
    ]
    sibling_figure_links = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_figure_viewer_href(slug, item), quote=True),
            label=html.escape(str(item.get("caption") or _figure_asset_filename(item) or "Figure")),
            summary=html.escape(str(item.get("section_hint") or "같은 문서의 다른 figure 자산")),
        ).strip()
        for item in sibling_figures[:6]
    )
    related_section_block = ""
    if isinstance(section_match, dict) and str(section_match.get("section_href") or "").strip():
        related_section_block = """
        <article class="wiki-card">
          <h3>Related Section</h3>
          <div class="wiki-links">
            <a href="{href}">{label}</a>
            <span>{summary}</span>
          </div>
        </article>
        """.format(
            href=html.escape(str(section_match.get("section_href") or ""), quote=True),
            label=html.escape(str(section_match.get("section_heading") or "Related Section")),
            summary=html.escape(str(section_match.get("section_path") or str(section_match.get("section_hint") or ""))),
        ).strip()
    return [
        """
        <section class="wiki-parent-card">
          <div class="wiki-parent-eyebrow">Parent Book</div>
          <a href="{href}">{label}</a>
          <p>{summary}</p>
        </section>
        <section class="wiki-grid">
          <article class="wiki-card">
            <h3>Entities</h3>
            <div class="wiki-entity-list">{entity_links}</div>
          </article>
          <article class="wiki-card">
            <h3>Documents</h3>
            {related_books}
          </article>
          <article class="wiki-card">
            <h3>Recommended Path</h3>
            {next_path_links}
          </article>
        </section>
        <section class="wiki-grid wiki-grid-secondary">
          {related_section_block}
          <article class="wiki-card">
            <h3>Figures</h3>
            {sibling_figure_links}
          </article>
        </section>
        """.format(
            href=html.escape(_preferred_book_href(root_dir, slug), quote=True),
            label=html.escape(parent_title),
            summary=html.escape(parent_summary),
            entity_links=related_entity_links or '<div class="wiki-empty">연결된 엔터티가 아직 없습니다.</div>',
            related_books=related_books or '<div class="wiki-empty">연관 문서가 아직 없습니다.</div>',
            next_path_links=next_path_links or '<div class="wiki-empty">연결된 경로가 아직 없습니다.</div>',
            related_section_block=related_section_block or '<article class="wiki-card"><h3>Section Match</h3><div class="wiki-empty">정확한 섹션 매칭이 아직 없습니다.</div></article>',
            sibling_figure_links=sibling_figure_links or '<div class="wiki-empty">같은 문서의 다른 figure 자산이 없습니다.</div>',
        ).strip()
    ]


def internal_gold_candidate_markdown_viewer_html(root_dir: Path, viewer_path: str) -> str | None:
    parsed = parse_gold_candidate_markdown_viewer_path(viewer_path)
    if parsed is None:
        return None
    viewer_kind, slug, runtime_group = parsed
    request = urlparse((viewer_path or "").strip())
    embedded = "embed=1" in request.query
    if viewer_kind == "runtime":
        if runtime_group == "active":
            markdown_path = _active_runtime_markdown_path(root_dir, slug)
        else:
            markdown_path = _legacy_runtime_markdown_path(root_dir, str(runtime_group or "").strip(), slug)
    else:
        markdown_path = root_dir / "data" / "gold_candidate_books" / "wave1" / f"{slug}.md"
    if markdown_path is None:
        return None
    if not markdown_path.exists() or not markdown_path.is_file():
        return None
    sections = _markdown_sections(markdown_path.read_text(encoding="utf-8"))
    if not sections:
        return None
    title = sections[0].get("heading") or slug.replace("_", " ").title()
    content_sections = _trim_leading_title_section(sections, title=str(title))
    summary = _markdown_summary(content_sections)
    cards = _build_study_section_cards(content_sections, book_slug=slug, target_anchor=request.fragment.strip(), embedded=embedded)
    return _render_study_viewer_html(
        title=str(title),
        source_url="",
        cards=cards,
        supplementary_blocks=_build_wiki_supplementary_blocks(root_dir, slug),
        section_count=len(content_sections),
        eyebrow=(
            "Approved Wiki Runtime Book"
            if viewer_kind == "runtime" and runtime_group == "active"
            else "Archived Wiki Runtime Reference"
            if viewer_kind == "runtime"
            else "Archived Gold Candidate Reference"
        ),
        summary=summary,
        embedded=embedded,
        page_overlay_toolbar=_render_page_overlay_toolbar(
            target_kind="book",
            target_ref=f"book:{slug}",
            title=str(title),
            book_slug=slug,
            viewer_path=_preferred_book_href(root_dir, slug),
        ),
    )


def internal_entity_hub_viewer_html(root_dir: Path, viewer_path: str) -> str | None:
    parsed = parse_entity_hub_viewer_path(viewer_path)
    if parsed is None:
        return None
    entity = _entity_hubs().get(parsed)
    if entity is None:
        return None
    request = urlparse((viewer_path or "").strip())
    embedded = "embed=1" in request.query
    sections = _entity_hub_sections(parsed)
    cards = _build_study_section_cards(sections, target_anchor=request.fragment.strip(), embedded=embedded)
    return _render_study_viewer_html(
        title=str(entity.get("title") or parsed),
        source_url="",
        cards=cards,
        supplementary_blocks=_build_entity_hub_supplementary_blocks(root_dir, parsed),
        section_count=len(sections),
        eyebrow=str(entity.get("eyebrow") or "Entity Hub"),
        summary=str(entity.get("summary") or ""),
        embedded=embedded,
        page_overlay_toolbar=_render_page_overlay_toolbar(
            target_kind="entity_hub",
            target_ref=f"entity:{parsed}",
            title=str(entity.get("title") or parsed),
            entity_slug=parsed,
            viewer_path=f"/wiki/entities/{parsed}/index.html",
        ),
    )


def internal_figure_viewer_html(root_dir: Path, viewer_path: str) -> str | None:
    parsed = parse_figure_viewer_path(viewer_path)
    if parsed is None:
        return None
    slug, asset_name = parsed
    asset = _figure_asset_by_name(slug, asset_name)
    if asset is None:
        return None
    request = urlparse((viewer_path or "").strip())
    embedded = "embed=1" in request.query
    title = str(asset.get("caption") or asset.get("alt") or asset_name).strip() or asset_name
    sections = _figure_viewer_sections(slug, asset_name, asset)
    cards = _build_study_section_cards(sections, book_slug=slug, target_anchor=request.fragment.strip(), embedded=embedded)
    return _render_study_viewer_html(
        title=title,
        source_url=str(asset.get("asset_url") or "").strip(),
        cards=cards,
        supplementary_blocks=_build_figure_supplementary_blocks(root_dir, slug, asset_name, asset),
        section_count=len(sections),
        eyebrow="Figure Asset",
        summary=f"{slug.replace('_', ' ').title()} 문서에서 추출한 figure 자산이다.",
        embedded=embedded,
        page_overlay_toolbar=_render_page_overlay_toolbar(
            target_kind="figure",
            target_ref=f"figure:{slug}:{asset_name}",
            title=title,
            book_slug=slug,
            asset_name=asset_name,
            viewer_path=f"/wiki/figures/{slug}/{asset_name}/index.html",
        ),
    )


def internal_buyer_packet_viewer_html(root_dir: Path, viewer_path: str) -> str | None:
    packet_id = parse_buyer_packet_viewer_path(viewer_path)
    if packet_id is None:
        return None
    loaded = _load_buyer_packet_entry(root_dir, packet_id)
    if loaded is None:
        return None
    bundle, packet = loaded
    markdown_path = root_dir / str(packet.get("markdown_path") or "")
    if not markdown_path.exists() or not markdown_path.is_file():
        return None
    request = urlparse((viewer_path or "").strip())
    embedded = "embed=1" in request.query
    sections = _markdown_sections(markdown_path.read_text(encoding="utf-8"))
    if not sections:
        return None
    title = str(packet.get("title") or packet_id)
    content_sections = _trim_leading_title_section(sections, title=title)
    summary = str(packet.get("purpose") or "").strip() or _markdown_summary(content_sections)
    cards = _build_study_section_cards(content_sections, target_anchor=request.fragment.strip(), embedded=embedded)
    return _render_study_viewer_html(
        title=title,
        source_url=f"/api/buyer-packet?packet_id={packet_id}",
        cards=cards,
        supplementary_blocks=_build_buyer_packet_supplementary_blocks(bundle, packet),
        section_count=len(content_sections),
        eyebrow="Release Packet",
        summary=summary,
        embedded=embedded,
        page_overlay_toolbar=_render_page_overlay_toolbar(
            target_kind="book",
            target_ref=f"buyer_packet:{packet_id}",
            title=title,
            book_slug=f"buyer_packet__{packet_id}",
            viewer_path=f"/buyer-packets/{packet_id}",
        ),
    )


def parse_customer_pack_viewer_path(viewer_path: str) -> tuple[str, str] | None:
    parsed = urlparse((viewer_path or "").strip())
    request_path = parsed.path.strip()
    prefix = "/playbooks/customer-packs/"
    if not request_path.startswith(prefix):
        return None
    remainder = request_path[len(prefix) :]
    parts = [part for part in remainder.split("/") if part]
    if len(parts) == 2 and parts[1] == "index.html":
        return parts[0], parsed.fragment.strip()
    if len(parts) == 4 and parts[1] == "assets" and parts[3] == "index.html":
        return f"{parts[0]}::{parts[2]}", parsed.fragment.strip()
    return None


def load_customer_pack_book(root_dir: Path, draft_id: str) -> dict[str, Any] | None:
    resolved_draft_id = draft_id
    asset_slug = ""
    if "::" in draft_id:
        resolved_draft_id, asset_slug = draft_id.split("::", 1)
    record = CustomerPackDraftStore(root_dir).get(draft_id)
    if record is None and resolved_draft_id != draft_id:
        record = CustomerPackDraftStore(root_dir).get(resolved_draft_id)
    if record is None or not record.canonical_book_path.strip():
        return None
    canonical_path = (
        load_settings(root_dir).customer_pack_books_dir / f"{asset_slug}.json"
        if asset_slug
        else Path(record.canonical_book_path)
    )
    if not canonical_path.exists():
        return None
    payload = json.loads(canonical_path.read_text(encoding="utf-8"))
    payload["draft_id"] = record.draft_id
    payload["target_viewer_path"] = (
        f"/playbooks/customer-packs/{record.draft_id}/assets/{asset_slug}/index.html"
        if asset_slug
        else f"/playbooks/customer-packs/{record.draft_id}/index.html"
    )
    payload["target_anchor"] = payload.get("target_anchor") or ""
    payload["source_origin_url"] = f"/api/customer-packs/captured?draft_id={record.draft_id}"
    payload.setdefault("source_collection", record.plan.source_collection)
    payload.setdefault("pack_id", record.plan.pack_id)
    payload.setdefault("pack_label", record.plan.pack_label)
    payload.setdefault("inferred_product", record.plan.inferred_product)
    payload.setdefault("inferred_version", record.plan.inferred_version)
    payload.update(_customer_pack_boundary_payload(record))
    payload.update(evaluate_canonical_book_quality(payload))
    return payload


def internal_customer_pack_viewer_html(root_dir: Path, viewer_path: str) -> str | None:
    parsed = parse_customer_pack_viewer_path(viewer_path)
    if parsed is None:
        return None

    request = urlparse((viewer_path or "").strip())
    embedded = "embed=1" in request.query
    draft_id, target_anchor = parsed
    canonical_book = load_customer_pack_book(root_dir, draft_id)
    if canonical_book is None:
        return None

    sections = list(canonical_book.get("sections") or [])
    if not sections:
        return None
    cards = _build_study_section_cards(sections, target_anchor=target_anchor, embedded=embedded)
    family_label = str(canonical_book.get("family_label") or "").strip()
    family_summary = str(canonical_book.get("family_summary") or "").strip()
    derived_asset_count = int(canonical_book.get("derived_asset_count") or 0)
    if family_label:
        base_summary = family_summary or _default_customer_pack_summary(canonical_book)
    else:
        base_summary = _default_customer_pack_summary(canonical_book)
        if derived_asset_count > 0:
            base_summary = (
                f"{base_summary} 이 초안에서 {derived_asset_count}개의 파생 플레이북 자산이 추가로 생성되었습니다."
            )
    quality_summary = str(canonical_book.get("quality_summary") or "").strip()
    summary = f"{base_summary} {quality_summary}".strip() if quality_summary else base_summary
    if str(canonical_book.get("quality_status") or "ready") != "ready":
        summary = f"{summary} 이 자산은 아직 review needed 상태입니다."
    runtime_truth_label = str(canonical_book.get("runtime_truth_label") or "Customer Source-First Pack").strip()
    approval_state = str(canonical_book.get("approval_state") or "unreviewed").strip()
    publication_state = str(canonical_book.get("publication_state") or "draft").strip()
    source_lane = str(canonical_book.get("source_lane") or "customer_source_first_pack").strip()
    parser_backend = str(canonical_book.get("parser_backend") or "").strip()
    evidence_badges = [
        f"approval: {approval_state}",
        f"publication: {publication_state}",
    ]
    if parser_backend:
        evidence_badges.append(f"parser: {parser_backend}")
    if source_lane and source_lane != "customer_source_first_pack":
        evidence_badges.append(f"lane: {source_lane}")
    supplementary_blocks = [
        """
        <section class="wiki-parent-card">
          <div class="wiki-parent-eyebrow">Pack Runtime Truth</div>
          <div class="viewer-truth-topline">
            <span class="viewer-truth-badge">{badge}</span>
            <a class="viewer-truth-link" href="{source_url}" target="_blank" rel="noreferrer">원본 캡처 열기</a>
          </div>
          <div class="viewer-truth-title">{title}</div>
          <p>Customer pack runtime evidence</p>
          <div class="wiki-entity-list">{badges}</div>
        </section>
        """.format(
            source_url=html.escape(
                str(canonical_book.get("source_origin_url") or canonical_book.get("source_uri") or ""),
                quote=True,
            ),
            badge=html.escape(str(canonical_book.get("boundary_badge") or "Private Pack Runtime")),
            title=html.escape(runtime_truth_label),
            badges="".join(
                f'<span class="meta-pill">{html.escape(item)}</span>'
                for item in evidence_badges
                if item.strip()
            ),
        ).strip()
    ]
    return _render_study_viewer_html(
        title=str(canonical_book.get("title") or draft_id),
        source_url=str(canonical_book.get("source_origin_url") or canonical_book.get("source_uri") or ""),
        cards=cards,
        supplementary_blocks=supplementary_blocks,
        section_count=len(sections),
        eyebrow=family_label or "Customer Playbook Draft",
        summary=summary,
        embedded=embedded,
        page_overlay_toolbar=_render_page_overlay_toolbar(
            target_kind="book",
            target_ref=f"book:{str(canonical_book.get('book_slug') or draft_id)}",
            title=str(canonical_book.get("title") or draft_id),
            book_slug=str(canonical_book.get("book_slug") or draft_id),
            viewer_path=str(canonical_book.get("target_viewer_path") or f"/playbooks/customer-packs/{draft_id}/index.html"),
        ),
    )


def list_customer_pack_drafts(root_dir: Path) -> dict[str, Any]:
    drafts: list[dict[str, Any]] = []
    store = CustomerPackDraftStore(root_dir)
    for record in store.list():
        summary = record.to_summary()
        if record.canonical_book_path.strip():
            payload = load_customer_pack_book(root_dir, record.draft_id)
            if payload is not None:
                summary["quality_status"] = payload.get("quality_status")
                summary["quality_score"] = payload.get("quality_score")
                summary["quality_summary"] = payload.get("quality_summary")
                summary["quality_flags"] = payload.get("quality_flags")
                summary["playable_asset_count"] = payload.get("playable_asset_count", 1)
                summary["derived_asset_count"] = payload.get("derived_asset_count", 0)
                summary["derived_assets"] = payload.get("derived_assets", [])
        drafts.append(summary)
    return {"drafts": drafts}


__all__ = [
    "internal_buyer_packet_viewer_html",
    "build_chat_navigation_links",
    "internal_customer_pack_viewer_html",
    "internal_entity_hub_viewer_html",
    "internal_gold_candidate_markdown_viewer_html",
    "internal_viewer_html",
    "list_customer_pack_drafts",
    "load_customer_pack_book",
    "parse_customer_pack_viewer_path",
    "parse_entity_hub_viewer_path",
    "parse_gold_candidate_markdown_viewer_path",
]
