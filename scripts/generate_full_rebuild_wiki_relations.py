from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

FULL_REBUILD_MANIFEST_PATH = ROOT / "data" / "wiki_runtime_books" / "full_rebuild_manifest.json"
SOURCE_FIRST_MANIFEST_PATH = ROOT / "manifests" / "ocp420_source_first_full_rebuild_manifest.json"
ENTITY_HUBS_PATH = ROOT / "data" / "wiki_relations" / "entity_hubs.json"
CANDIDATE_RELATIONS_PATH = ROOT / "data" / "wiki_relations" / "candidate_relations.json"
CHAT_ALIASES_PATH = ROOT / "data" / "wiki_relations" / "chat_navigation_aliases.json"
FIGURE_ASSETS_PATH = ROOT / "data" / "wiki_relations" / "figure_assets.json"
FIGURE_ENTITY_INDEX_PATH = ROOT / "data" / "wiki_relations" / "figure_entity_index.json"
FIGURE_SECTION_INDEX_PATH = ROOT / "data" / "wiki_relations" / "figure_section_index.json"
SECTION_RELATION_INDEX_PATH = ROOT / "data" / "wiki_relations" / "section_relation_index.json"
CATALOG_MD_PATH = ROOT / "data" / "wiki_relations" / "full_rebuild_relation_catalog.md"
REPORT_PATH = ROOT / "reports" / "build_logs" / "full_rebuild_wiki_relations_report.json"

ACTIVE_BOOK_PREFIX = "/playbooks/wiki-runtime/active"

MANUAL_ENTITY_HUBS = {
    "etcd",
    "machine-config-operator",
    "prometheus",
    "control-plane-nodes",
    "cluster-wide-proxy",
}

HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*$")
HEADING_NUMBER_PREFIX_RE = re.compile(
    r"^\s*(?:chapter\s+\d+\.?\s*|\d+\s*장\.?\s*|(?:\d+|[A-Za-z])(?:\.\d+)*\.?\s+)",
    re.IGNORECASE,
)
SECTION_HINT_NOISE_RE = re.compile(r"\s*링크 복사.*$", re.IGNORECASE)

CLUSTERS: dict[str, dict[str, Any]] = {
    "platform-foundation": {
        "title": "Platform Foundation",
        "summary": "OpenShift 전체 구조와 핵심 개념을 이해하는 출발 허브다.",
        "overview": [
            "Platform Foundation 은 OpenShift의 큰 구조, 구성요소, 설치 전 개념 기준선을 묶는다.",
            "학습과 운영 모두에서 가장 먼저 돌아오는 상위 허브로 쓴다.",
        ],
        "books": ["overview", "architecture", "installation_overview"],
        "bridge_docs": ["installing_on_any_platform", "networking_overview"],
    },
    "installation-day2": {
        "title": "Installation and Day-2",
        "summary": "설치, 설치 직후 안정화, 설치 후 설정과 day-2 운영 변화의 허브다.",
        "overview": [
            "Installation and Day-2 는 설치, 초기 수렴, 설치 후 설정, 업그레이드 전후 점검 흐름을 묶는다.",
            "실제 운영 시작 전 기준선과 후속 작업을 재탐색하는 허브로 쓴다.",
        ],
        "books": ["installation_overview", "installing_on_any_platform", "postinstallation_configuration", "updating_clusters"],
        "bridge_docs": ["machine_configuration", "backup_and_restore"],
    },
    "control-plane-ops": {
        "title": "Control Plane and Node Operations",
        "summary": "control plane, node, 복구, MCO 수렴 같은 핵심 운영 작업의 허브다.",
        "overview": [
            "Control Plane and Node Operations 는 etcd, node, machine configuration, 복구 절차를 묶는다.",
            "장애 대응과 운영 검증에서 가장 자주 순환하는 작업 허브다.",
        ],
        "books": ["backup_and_restore", "etcd", "machine_configuration", "machine_management", "nodes"],
        "bridge_docs": ["monitoring", "validation_and_troubleshooting", "postinstallation_configuration"],
    },
    "observability": {
        "title": "Observability and Troubleshooting",
        "summary": "monitoring, logging, validation, troubleshooting을 묶는 관측 허브다.",
        "overview": [
            "Observability 는 metrics, alerts, logs, validation 절차를 하나의 탐색면으로 묶는다.",
            "운영 이후 확인, 이상 징후 추적, 문제 해결 진입점으로 사용한다.",
        ],
        "books": ["monitoring", "observability_overview", "logging", "validation_and_troubleshooting"],
        "bridge_docs": ["backup_and_restore", "machine_configuration"],
    },
    "networking": {
        "title": "Networking and Connectivity",
        "summary": "네트워킹, 프록시, ingress, disconnected 환경의 연결 허브다.",
        "overview": [
            "Networking and Connectivity 는 네트워크 구조, 프록시, ingress, disconnected 환경을 함께 묶는다.",
            "설치와 day-2 운영에서 연결성 문제를 되짚을 때 이 허브로 돌아온다.",
        ],
        "books": ["networking_overview", "advanced_networking", "ingress_and_load_balancing", "disconnected_environments"],
        "bridge_docs": ["postinstallation_configuration", "security_and_auth", "installation_overview"],
    },
    "security-and-auth": {
        "title": "Security and Access",
        "summary": "인증, 권한, 보안, 컴플라이언스 문서를 묶는 보안 허브다.",
        "overview": [
            "Security and Access 는 인증, 권한 부여, 보안 정책, 컴플라이언스 기준을 묶는다.",
            "운영 정책과 접근 제어 관점에서 관련 문서를 탐색하는 허브다.",
        ],
        "books": ["authentication_and_authorization", "security_and_compliance"],
        "bridge_docs": [],
    },
    "storage-and-content": {
        "title": "Storage, Registry, and Images",
        "summary": "스토리지, 레지스트리, 이미지 운영을 묶는 데이터 보관 허브다.",
        "overview": [
            "Storage, Registry, and Images 는 persistent storage, registry, image 관리 흐름을 함께 다룬다.",
            "배포와 운영에서 데이터 경로를 따라갈 때 이 허브를 기준으로 쓴다.",
        ],
        "books": ["storage", "registry", "images"],
        "bridge_docs": ["validation_and_troubleshooting", "operators", "disconnected_environments"],
    },
    "operators-and-tooling": {
        "title": "Operators and Tooling",
        "summary": "Operators, CLI, 웹 콘솔처럼 실제 조작 표면을 묶는 도구 허브다.",
        "overview": [
            "Operators and Tooling 은 설치된 기능을 관리하는 조작 표면과 도구 사용 경로를 묶는다.",
            "운영자가 실제 손을 대는 진입점을 다시 고르는 허브다.",
        ],
        "books": ["operators", "cli_tools", "web_console"],
        "bridge_docs": ["storage"],
    },
    "lifecycle-and-support": {
        "title": "Lifecycle and Support",
        "summary": "업데이트, 릴리스 노트, 지원 절차를 묶는 운영 lifecycle 허브다.",
        "overview": [
            "Lifecycle and Support 는 업데이트, 릴리스 변화, 지원 요청과 회귀 대응을 함께 본다.",
            "운영 변경 전후 판단과 지원 escalation 흐름의 허브다.",
        ],
        "books": ["updating_clusters", "release_notes", "support"],
        "bridge_docs": ["validation_and_troubleshooting", "backup_and_restore", "monitoring"],
    },
}

BOOK_ENTITY_MAP: dict[str, list[str]] = {
    "overview": ["platform-foundation"],
    "architecture": ["platform-foundation", "control-plane-nodes"],
    "installation_overview": ["platform-foundation", "installation-day2"],
    "installing_on_any_platform": ["cluster-wide-proxy", "machine-config-operator", "installation-day2"],
    "postinstallation_configuration": ["cluster-wide-proxy", "machine-config-operator", "installation-day2"],
    "updating_clusters": ["installation-day2", "lifecycle-and-support", "control-plane-nodes"],
    "backup_and_restore": ["etcd", "control-plane-nodes", "cluster-wide-proxy", "control-plane-ops"],
    "etcd": ["etcd", "control-plane-nodes", "control-plane-ops"],
    "machine_configuration": ["machine-config-operator", "control-plane-nodes", "control-plane-ops"],
    "machine_management": ["machine-config-operator", "control-plane-nodes", "control-plane-ops"],
    "nodes": ["control-plane-nodes", "machine-config-operator", "control-plane-ops"],
    "monitoring": ["prometheus", "observability"],
    "observability_overview": ["prometheus", "observability"],
    "logging": ["prometheus", "observability"],
    "validation_and_troubleshooting": ["prometheus", "control-plane-nodes", "observability"],
    "networking_overview": ["cluster-wide-proxy", "networking"],
    "advanced_networking": ["cluster-wide-proxy", "networking"],
    "ingress_and_load_balancing": ["cluster-wide-proxy", "networking"],
    "disconnected_environments": ["cluster-wide-proxy", "networking", "storage-and-content"],
    "authentication_and_authorization": ["security-and-auth"],
    "security_and_compliance": ["security-and-auth"],
    "storage": ["storage-and-content"],
    "registry": ["storage-and-content", "operators-and-tooling"],
    "images": ["storage-and-content", "operators-and-tooling"],
    "operators": ["operators-and-tooling"],
    "cli_tools": ["operators-and-tooling"],
    "web_console": ["operators-and-tooling"],
    "support": ["lifecycle-and-support"],
    "release_notes": ["lifecycle-and-support"],
}

SPECIAL_HUB_BOOKS: dict[str, dict[str, list[str]]] = {
    "etcd": {
        "related": ["backup_and_restore", "etcd", "machine_configuration", "monitoring"],
        "next": ["backup_and_restore", "machine_configuration", "monitoring"],
    },
    "machine-config-operator": {
        "related": ["machine_configuration", "machine_management", "nodes", "installing_on_any_platform"],
        "next": ["machine_configuration", "installing_on_any_platform", "monitoring"],
    },
    "prometheus": {
        "related": ["monitoring", "observability_overview", "logging", "validation_and_troubleshooting"],
        "next": ["monitoring", "logging", "validation_and_troubleshooting"],
    },
    "control-plane-nodes": {
        "related": ["nodes", "machine_configuration", "backup_and_restore", "etcd"],
        "next": ["backup_and_restore", "machine_configuration", "nodes"],
    },
    "cluster-wide-proxy": {
        "related": ["postinstallation_configuration", "installing_on_any_platform", "advanced_networking", "disconnected_environments"],
        "next": ["installing_on_any_platform", "postinstallation_configuration", "advanced_networking"],
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _book_href(slug: str) -> str:
    return f"{ACTIVE_BOOK_PREFIX}/{slug}/index.html"


def _hub_href(slug: str) -> str:
    return f"/wiki/entities/{slug}/index.html"


def _kind_for_href(href: str) -> str:
    return "entity" if str(href or "").startswith("/wiki/entities/") else "book"


def _normalize_href(href: str) -> str:
    text = str(href or "").strip()
    if not text:
        return ""
    marker = "/playbooks/"
    if marker not in text:
        return text
    parts = [part for part in text.split("/") if part]
    if "index.html" not in parts or len(parts) < 2:
        return text
    slug = parts[-2]
    return _book_href(slug)


def _book_item(slug: str, title_by_slug: dict[str, str], *, summary: str = "") -> dict[str, str]:
    title = title_by_slug.get(slug, slug.replace("_", " ").title())
    return {
        "label": title,
        "href": _book_href(slug),
        "summary": summary or f"{title} 문서로 바로 이동한다.",
    }


def _entity_item(entity_slug: str, entity_hubs: dict[str, dict[str, Any]]) -> dict[str, str]:
    title = str(entity_hubs.get(entity_slug, {}).get("title") or entity_slug.replace("-", " ").title())
    return {
        "label": title,
        "href": _hub_href(entity_slug),
    }


def _cluster_lookup() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for cluster_slug, cluster in CLUSTERS.items():
        for slug in cluster.get("books", []):
            mapping[str(slug)] = cluster_slug
    return mapping


def _seed_manual_hubs(title_by_slug: dict[str, str]) -> dict[str, dict[str, Any]]:
    existing = _load_json(ENTITY_HUBS_PATH)
    hubs: dict[str, dict[str, Any]] = {}
    for slug in MANUAL_ENTITY_HUBS:
        seed = existing.get(slug) if isinstance(existing.get(slug), dict) else {}
        record = {
            "title": str(seed.get("title") or slug.replace("-", " ").title()),
            "eyebrow": str(seed.get("eyebrow") or "Entity Hub"),
            "summary": str(seed.get("summary") or ""),
            "overview": [str(item).strip() for item in seed.get("overview", []) if str(item).strip()],
            "related_books": [],
            "next_reading_path": [],
        }
        config = SPECIAL_HUB_BOOKS.get(slug, {})
        record["related_books"] = [
            _book_item(book_slug, title_by_slug)
            for book_slug in config.get("related", [])
            if book_slug in title_by_slug
        ]
        record["next_reading_path"] = [
            {
                "label": f"{index}. {title_by_slug.get(book_slug, book_slug.replace('_', ' ').title())}",
                "href": _book_href(book_slug),
                "summary": f"{title_by_slug.get(book_slug, book_slug)} 문서로 이어서 탐색한다.",
            }
            for index, book_slug in enumerate(config.get("next", []), start=1)
            if book_slug in title_by_slug
        ]
        if not record["overview"]:
            record["overview"] = [record["summary"]] if record["summary"] else []
        hubs[slug] = record
    return hubs


def _topic_hubs(title_by_slug: dict[str, str]) -> dict[str, dict[str, Any]]:
    hubs: dict[str, dict[str, Any]] = {}
    for cluster_slug, cluster in CLUSTERS.items():
        books = [slug for slug in cluster.get("books", []) if slug in title_by_slug]
        bridges = [slug for slug in cluster.get("bridge_docs", []) if slug in title_by_slug]
        hubs[cluster_slug] = {
            "title": str(cluster.get("title") or cluster_slug.replace("-", " ").title()),
            "eyebrow": "Topic Hub",
            "summary": str(cluster.get("summary") or ""),
            "overview": [str(item).strip() for item in cluster.get("overview", []) if str(item).strip()],
            "related_books": [_book_item(slug, title_by_slug) for slug in books[:4]],
            "next_reading_path": [
                {
                    "label": f"{index}. {title_by_slug.get(slug, slug.replace('_', ' ').title())}",
                    "href": _book_href(slug),
                    "summary": f"{title_by_slug.get(slug, slug)} 문서로 이어서 읽는다.",
                }
                for index, slug in enumerate((books[:2] + bridges[:2])[:3], start=1)
            ],
        }
    return hubs


def _build_candidate_relations(title_by_slug: dict[str, str], entity_hubs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    cluster_by_slug = _cluster_lookup()
    relations: dict[str, dict[str, Any]] = {}
    for slug, title in title_by_slug.items():
        cluster_slug = cluster_by_slug.get(slug, "platform-foundation")
        cluster = CLUSTERS.get(cluster_slug, {})
        sibling_slugs = [item for item in cluster.get("books", []) if item in title_by_slug and item != slug]
        bridge_slugs = [item for item in cluster.get("bridge_docs", []) if item in title_by_slug and item != slug]
        entity_slugs = []
        for entity_slug in BOOK_ENTITY_MAP.get(slug, []):
            if entity_slug in entity_hubs and entity_slug not in entity_slugs:
                entity_slugs.append(entity_slug)
        if cluster_slug in entity_hubs and cluster_slug not in entity_slugs:
            entity_slugs.append(cluster_slug)
        relations[slug] = {
            "entities": [_entity_item(entity_slug, entity_hubs) for entity_slug in entity_slugs[:4]],
            "related_docs": [
                _book_item(target_slug, title_by_slug, summary=f"{title} 이후 함께 봐야 하는 문서다.")
                for target_slug in (sibling_slugs[:2] + bridge_slugs[:2])
            ],
            "next_reading_path": [
                {
                    "label": f"{index}. {title_by_slug.get(target_slug, target_slug.replace('_', ' ').title())}",
                    "href": _book_href(target_slug),
                    "summary": f"{title} 다음 경로로 {title_by_slug.get(target_slug, target_slug)}를 본다.",
                }
                for index, target_slug in enumerate((bridge_slugs[:2] + sibling_slugs[:2])[:3], start=1)
            ],
            "parent_topic": {
                "label": str(cluster.get("title") or cluster_slug.replace("-", " ").title()),
                "href": _hub_href(cluster_slug),
                "summary": str(cluster.get("summary") or ""),
            },
            "siblings": [
                _book_item(target_slug, title_by_slug, summary=f"{title}와 같은 작업군에 속한 문서다.")
                for target_slug in sibling_slugs[:3]
            ],
        }
    return relations


def _build_figure_entity_index(title_by_slug: dict[str, str]) -> dict[str, Any]:
    payload = _load_json(FIGURE_ASSETS_PATH)
    entries = payload.get("entries") if isinstance(payload.get("entries"), dict) else {}
    by_entity: dict[str, list[dict[str, Any]]] = {}
    by_book: dict[str, list[dict[str, Any]]] = {}
    for slug, figures in entries.items():
        if not isinstance(figures, list):
            continue
        book_title = title_by_slug.get(slug, str(slug).replace("_", " ").title())
        for figure in figures:
            if not isinstance(figure, dict):
                continue
            item = {
                "book_slug": str(slug),
                "book_title": book_title,
                "caption": str(figure.get("caption") or "").strip(),
                "viewer_path": str(figure.get("viewer_path") or "").strip(),
                "asset_url": str(figure.get("asset_url") or "").strip(),
                "section_hint": str(figure.get("section_hint") or "").strip(),
            }
            by_book.setdefault(str(slug), []).append(item)
            for entity in figure.get("related_entities") or []:
                if not isinstance(entity, dict):
                    continue
                href = str(entity.get("href") or "").strip()
                if not href.startswith("/wiki/entities/"):
                    continue
                entity_slug = href.removeprefix("/wiki/entities/").removesuffix("/index.html").strip("/")
                if not entity_slug:
                    continue
                entity_item = dict(item)
                entity_item["entity_label"] = str(entity.get("label") or "").strip()
                by_entity.setdefault(entity_slug, []).append(entity_item)
    return {
        "generated_at_utc": _utc_now(),
        "entity_count": len(by_entity),
        "book_count": len(by_book),
        "by_entity": by_entity,
        "by_book": by_book,
    }


def _normalize_heading_text(text: str) -> str:
    cleaned = SECTION_HINT_NOISE_RE.sub("", str(text or "").strip())
    cleaned = HEADING_NUMBER_PREFIX_RE.sub("", cleaned).strip()
    cleaned = re.sub(r"[^\w\s가-힣-]", " ", cleaned, flags=re.UNICODE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
    return cleaned


def _anchorify_heading(text: str) -> str:
    normalized = re.sub(r"[^\w\s-]", "", str(text or ""), flags=re.UNICODE).strip().lower()
    normalized = re.sub(r"[\s_]+", "-", normalized)
    return normalized or "section"


def _markdown_sections(markdown_path: Path) -> list[dict[str, str]]:
    if not markdown_path.exists() or not markdown_path.is_file():
        return []
    sections: list[dict[str, str]] = []
    path_stack: list[str] = []
    for raw_line in markdown_path.read_text(encoding="utf-8").splitlines():
        match = HEADING_RE.match(raw_line.strip())
        if match is None:
            continue
        level = len(match.group("hashes"))
        title = match.group("title").strip()
        while len(path_stack) >= level:
            path_stack.pop()
        path_stack.append(title)
        sections.append(
            {
                "heading": title,
                "anchor": _anchorify_heading(title),
                "path": " > ".join(path_stack),
                "norm_heading": _normalize_heading_text(title),
                "norm_path": _normalize_heading_text(" ".join(path_stack)),
            }
        )
    return sections


def _match_section(section_hint: str, sections: list[dict[str, str]]) -> dict[str, str] | None:
    hint_norm = _normalize_heading_text(section_hint)
    if not hint_norm or not sections:
        return None
    hint_tokens = {token for token in hint_norm.split() if token}
    best: dict[str, str] | None = None
    best_score = 0
    for section in sections:
        heading_norm = section.get("norm_heading", "")
        path_norm = section.get("norm_path", "")
        score = 0
        if heading_norm and heading_norm in hint_norm:
            score += 10
        if hint_norm and hint_norm in path_norm:
            score += 8
        heading_tokens = {token for token in heading_norm.split() if token}
        path_tokens = {token for token in path_norm.split() if token}
        score += len(hint_tokens & heading_tokens) * 3
        score += len(hint_tokens & path_tokens)
        if score > best_score:
            best_score = score
            best = section
    if best is None or best_score < 3:
        return None
    return best


def _build_figure_section_index(manifest_entries: list[dict[str, Any]]) -> dict[str, Any]:
    payload = _load_json(FIGURE_ASSETS_PATH)
    figure_entries = payload.get("entries") if isinstance(payload.get("entries"), dict) else {}
    by_slug: dict[str, list[dict[str, Any]]] = {}
    matched_count = 0
    total_count = 0
    for entry in manifest_entries:
        slug = str(entry.get("slug") or "").strip()
        runtime_path = Path(str(entry.get("runtime_path") or "")).resolve()
        if not slug:
            continue
        figures = figure_entries.get(slug)
        if not isinstance(figures, list) or not figures:
            continue
        sections = _markdown_sections(runtime_path)
        materialized: list[dict[str, Any]] = []
        for figure in figures:
            if not isinstance(figure, dict):
                continue
            total_count += 1
            asset_url = str(figure.get("asset_url") or "").strip()
            asset_name = Path(urlparse(asset_url).path).name.strip()
            matched = _match_section(str(figure.get("section_hint") or ""), sections)
            record = {
                "asset_name": asset_name,
                "viewer_path": str(figure.get("viewer_path") or "").strip(),
                "caption": str(figure.get("caption") or "").strip(),
                "section_hint": str(figure.get("section_hint") or "").strip(),
                "section_heading": str(matched.get("heading") or "") if matched else "",
                "section_anchor": str(matched.get("anchor") or "") if matched else "",
                "section_path": str(matched.get("path") or "") if matched else "",
                "section_href": (
                    f"{_book_href(slug)}#{matched.get('anchor')}" if matched and str(matched.get("anchor") or "").strip() else ""
                ),
            }
            if record["section_href"]:
                matched_count += 1
            materialized.append(record)
        by_slug[slug] = materialized
    return {
        "generated_at_utc": _utc_now(),
        "book_count": len(by_slug),
        "figure_count": total_count,
        "matched_section_count": matched_count,
        "by_slug": by_slug,
    }


def _dedupe_section_entries(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    unique: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        href = str(item.get("href") or "").strip()
        label = str(item.get("label") or "").strip()
        if not href or not label:
            continue
        key = (href, label)
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def _build_section_relation_index(
    title_by_slug: dict[str, str],
    relations: dict[str, dict[str, Any]],
    figure_entity_index: dict[str, Any],
    figure_section_index: dict[str, Any],
) -> dict[str, Any]:
    figure_section_by_viewer: dict[str, dict[str, Any]] = {}
    by_book: dict[str, list[dict[str, Any]]] = {}
    by_entity: dict[str, list[dict[str, Any]]] = {}

    for slug, entries in (figure_section_index.get("by_slug") or {}).items():
        if not isinstance(entries, list):
            continue
        items: list[dict[str, Any]] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            viewer_path = str(entry.get("viewer_path") or "").strip()
            if viewer_path:
                figure_section_by_viewer[viewer_path] = entry
            href = str(entry.get("section_href") or "").strip()
            label = str(entry.get("section_heading") or "").strip()
            if not href or not label:
                continue
            items.append(
                {
                    "label": label,
                    "href": href,
                    "summary": str(entry.get("section_path") or entry.get("section_hint") or "").strip(),
                    "source": "figure_section",
                }
            )
        by_book[str(slug)] = _dedupe_section_entries(items)[:6]

    for entity_slug, entries in (figure_entity_index.get("by_entity") or {}).items():
        if not isinstance(entries, list):
            continue
        items: list[dict[str, Any]] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            section_match = figure_section_by_viewer.get(str(entry.get("viewer_path") or "").strip(), {})
            href = str(section_match.get("section_href") or "").strip()
            label = str(section_match.get("section_heading") or "").strip()
            if not href or not label:
                continue
            items.append(
                {
                    "label": label,
                    "href": href,
                    "summary": "{book} · {path}".format(
                        book=str(entry.get("book_title") or entry.get("book_slug") or "").strip() or "related book",
                        path=str(section_match.get("section_path") or section_match.get("section_hint") or "").strip(),
                    ).strip(),
                    "source": "entity_figure_section",
                }
            )
        by_entity[str(entity_slug)] = _dedupe_section_entries(items)[:6]

    for slug, relation in relations.items():
        if not isinstance(relation, dict):
            continue
        seeded = list(by_book.get(str(slug), []))
        for item in relation.get("related_docs") or []:
            if not isinstance(item, dict):
                continue
            href = _normalize_href(str(item.get("href") or "").strip())
            parsed = urlparse(href)
            parts = [part for part in parsed.path.split("/") if part]
            if "index.html" not in parts or len(parts) < 2:
                continue
            target_slug = parts[-2]
            target_sections = by_book.get(target_slug, [])
            if not target_sections:
                continue
            first = target_sections[0]
            seeded.append(
                {
                    "label": str(first.get("label") or "").strip(),
                    "href": str(first.get("href") or "").strip(),
                    "summary": "{book} · {summary}".format(
                        book=title_by_slug.get(target_slug, target_slug.replace("_", " ").title()),
                        summary=str(first.get("summary") or "").strip(),
                    ).strip(),
                    "source": "related_doc_section",
                }
            )
        by_book[str(slug)] = _dedupe_section_entries(seeded)[:6]

    return {
        "generated_at_utc": _utc_now(),
        "book_count": len(by_book),
        "entity_count": len(by_entity),
        "by_book": by_book,
        "by_entity": by_entity,
    }


def _build_chat_aliases(relations: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, str]]]:
    aliases: dict[str, list[dict[str, str]]] = {}
    for slug, relation in relations.items():
        items: list[dict[str, str]] = []
        seen: set[str] = set()
        for group in ("entities", "related_docs", "next_reading_path"):
            for item in relation.get(group, []):
                if not isinstance(item, dict):
                    continue
                href = str(item.get("href") or "").strip()
                label = str(item.get("label") or "").strip()
                if not href or not label or href in seen:
                    continue
                seen.add(href)
                items.append({"label": label, "href": href, "kind": _kind_for_href(href)})
                if len(items) >= 4:
                    break
            if len(items) >= 4:
                break
        aliases[slug] = items
    return aliases


def _catalog_markdown(
    *,
    title_by_slug: dict[str, str],
    relations: dict[str, dict[str, Any]],
    entity_hubs: dict[str, dict[str, Any]],
    figure_entity_index: dict[str, Any],
    figure_section_index: dict[str, Any],
    section_relation_index: dict[str, Any],
    generated_at: str,
) -> str:
    lines = [
        "# OCP 4.20 Full Rebuild Wiki Relations",
        "",
        f"- generated_at_utc: `{generated_at}`",
        f"- entity_hub_count: `{len(entity_hubs)}`",
        f"- candidate_relation_count: `{len(relations)}`",
        "",
    ]
    for slug, title in title_by_slug.items():
        relation = relations.get(slug, {})
        entity_labels = ", ".join(str(item.get("label") or "") for item in relation.get("entities", []) if isinstance(item, dict))
        related_labels = ", ".join(str(item.get("label") or "") for item in relation.get("related_docs", []) if isinstance(item, dict))
        lines.extend(
            [
                f"## `{slug}`",
                "",
                f"- title: `{title}`",
                f"- entities: {entity_labels or '(none)'}",
                f"- related_docs: {related_labels or '(none)'}",
                "",
            ]
        )
    by_entity = figure_entity_index.get("by_entity") if isinstance(figure_entity_index, dict) else {}
    if isinstance(by_entity, dict) and by_entity:
        lines.extend(["## Figure Entity Coverage", ""])
        for entity_slug in sorted(by_entity.keys()):
            figures = by_entity.get(entity_slug)
            if not isinstance(figures, list):
                continue
            lines.append(f"- `{entity_slug}` · figure_count=`{len(figures)}`")
        lines.append("")
    by_slug = figure_section_index.get("by_slug") if isinstance(figure_section_index, dict) else {}
    if isinstance(by_slug, dict) and by_slug:
        lines.extend(["## Figure Section Coverage", ""])
        for slug in sorted(by_slug.keys()):
            figures = by_slug.get(slug)
            if not isinstance(figures, list):
                continue
            matched = sum(1 for item in figures if isinstance(item, dict) and str(item.get("section_href") or "").strip())
            lines.append(f"- `{slug}` · matched_sections=`{matched}/{len(figures)}`")
        lines.append("")
    by_book_sections = section_relation_index.get("by_book") if isinstance(section_relation_index, dict) else {}
    if isinstance(by_book_sections, dict) and by_book_sections:
        lines.extend(["## Section Relation Coverage", ""])
        for slug in sorted(by_book_sections.keys()):
            items = by_book_sections.get(slug)
            if not isinstance(items, list):
                continue
            lines.append(f"- `{slug}` · related_sections=`{len(items)}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    manifest = _load_json(FULL_REBUILD_MANIFEST_PATH)
    _ = _load_json(SOURCE_FIRST_MANIFEST_PATH)
    entries = manifest.get("entries") if isinstance(manifest.get("entries"), list) else []
    title_by_slug: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        slug = str(entry.get("slug") or "").strip()
        title = str(entry.get("title") or slug).strip() or slug
        if slug:
            title_by_slug[slug] = title

    entity_hubs = {}
    entity_hubs.update(_seed_manual_hubs(title_by_slug))
    entity_hubs.update(_topic_hubs(title_by_slug))
    relations = _build_candidate_relations(title_by_slug, entity_hubs)
    aliases = _build_chat_aliases(relations)
    figure_entity_index = _build_figure_entity_index(title_by_slug)
    manifest_entries = [entry for entry in entries if isinstance(entry, dict)]
    figure_section_index = _build_figure_section_index(manifest_entries)
    section_relation_index = _build_section_relation_index(title_by_slug, relations, figure_entity_index, figure_section_index)
    generated_at = _utc_now()

    ENTITY_HUBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ENTITY_HUBS_PATH.write_text(json.dumps(entity_hubs, ensure_ascii=False, indent=2), encoding="utf-8")
    CANDIDATE_RELATIONS_PATH.write_text(json.dumps(relations, ensure_ascii=False, indent=2), encoding="utf-8")
    FIGURE_ENTITY_INDEX_PATH.write_text(json.dumps(figure_entity_index, ensure_ascii=False, indent=2), encoding="utf-8")
    FIGURE_SECTION_INDEX_PATH.write_text(json.dumps(figure_section_index, ensure_ascii=False, indent=2), encoding="utf-8")
    SECTION_RELATION_INDEX_PATH.write_text(json.dumps(section_relation_index, ensure_ascii=False, indent=2), encoding="utf-8")
    CHAT_ALIASES_PATH.write_text(json.dumps(aliases, ensure_ascii=False, indent=2), encoding="utf-8")
    CATALOG_MD_PATH.write_text(
        _catalog_markdown(
            title_by_slug=title_by_slug,
            relations=relations,
            entity_hubs=entity_hubs,
            figure_entity_index=figure_entity_index,
            figure_section_index=figure_section_index,
            section_relation_index=section_relation_index,
            generated_at=generated_at,
        ),
        encoding="utf-8",
    )

    payload = {
        "status": "ok",
        "generated_at_utc": generated_at,
        "runtime_manifest_path": str(FULL_REBUILD_MANIFEST_PATH),
        "entity_hub_count": len(entity_hubs),
        "candidate_relation_count": len(relations),
        "chat_alias_count": len(aliases),
        "figure_entity_count": int(figure_entity_index.get("entity_count") or 0),
        "figure_book_count": int(figure_entity_index.get("book_count") or 0),
        "figure_section_book_count": int(figure_section_index.get("book_count") or 0),
        "figure_section_match_count": int(figure_section_index.get("matched_section_count") or 0),
        "section_relation_book_count": int(section_relation_index.get("book_count") or 0),
        "section_relation_entity_count": int(section_relation_index.get("entity_count") or 0),
        "topic_hub_count": len(CLUSTERS),
        "manual_hub_count": len(MANUAL_ENTITY_HUBS),
    }
    REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(
        run_guarded_script(
            main,
            __file__,
            launcher_hint="scripts/codex_python.ps1",
        )
    )
