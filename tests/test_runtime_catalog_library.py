from __future__ import annotations

import json
import tempfile
from pathlib import Path

from play_book_studio.config.settings import Settings
from play_book_studio.ingestion.runtime_catalog_library import (
    _project_materialized_derived_sections,
    _retain_non_official_non_derived_playbook_rows,
    _retain_non_official_rows,
)
from play_book_studio.ingestion.topic_playbooks import materialize_derived_playbooks


def test_retain_non_official_rows_keeps_manual_synthesis() -> None:
    rows = [
        {"book_slug": "overview", "source_type": "official_doc"},
        {"book_slug": "etcd", "source_type": "manual_synthesis"},
        {"book_slug": "custom", "source_type": "customer_pack"},
    ]

    retained = _retain_non_official_rows(rows)

    assert [row["book_slug"] for row in retained] == ["etcd", "custom"]


def test_retain_non_official_rows_drops_generated_derived_rows() -> None:
    rows = [
        {"book_slug": "overview", "source_type": "official_doc"},
        {"book_slug": "etcd", "source_type": "manual_synthesis"},
        {"book_slug": "nodes_operations_playbook", "source_type": "operation_playbook"},
    ]

    retained = _retain_non_official_rows(rows)

    assert [row["book_slug"] for row in retained] == ["etcd"]


def test_retain_non_official_non_derived_playbook_rows_drops_official_and_derived() -> None:
    rows = [
        {
            "book_slug": "overview",
            "source_metadata": {"source_type": "official_doc"},
        },
        {
            "book_slug": "etcd",
            "source_metadata": {"source_type": "manual_synthesis"},
        },
        {
            "book_slug": "overview_topic_playbook",
            "source_metadata": {"source_type": "topic_playbook"},
        },
    ]

    retained = _retain_non_official_non_derived_playbook_rows(rows)

    assert [row["book_slug"] for row in retained] == ["etcd"]


def test_project_materialized_derived_sections_preserves_cli_metadata() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        settings = Settings(root_dir=Path(tmpdir))
        settings.playbook_documents_path.parent.mkdir(parents=True, exist_ok=True)
        source_payload = {
            "canonical_model": "playbook_document_v1",
            "source_view_strategy": "playbook_ast_v1",
            "book_slug": "nodes",
            "title": "노드 운영 가이드",
            "version": "4.20",
            "locale": "ko",
            "source_uri": "https://example.com/nodes",
            "translation_status": "approved_ko",
            "review_status": "approved",
            "source_metadata": {
                "source_id": "manual_synthesis:nodes",
                "source_type": "manual_synthesis",
                "source_lane": "applied_playbook",
                "source_collection": "core",
                "product": "openshift",
                "version": "4.20",
                "trust_score": 0.92,
                "review_status": "approved",
                "access_groups": ["public"],
            },
            "sections": [
                {
                    "section_id": "nodes:overview",
                    "ordinal": 1,
                    "heading": "개요",
                    "level": 2,
                    "path": ["개요"],
                    "anchor": "overview",
                    "viewer_path": "/docs/ocp/4.20/ko/nodes/index.html#overview",
                    "semantic_role": "overview",
                    "blocks": [{"kind": "paragraph", "text": "노드 운영 기본 개요"}],
                },
                {
                    "section_id": "nodes:drain",
                    "ordinal": 2,
                    "heading": "노드 드레인 절차",
                    "level": 2,
                    "path": ["운영", "노드 드레인 절차"],
                    "anchor": "node-drain",
                    "viewer_path": "/docs/ocp/4.20/ko/nodes/index.html#node-drain",
                    "semantic_role": "procedure",
                    "blocks": [
                        {"kind": "paragraph", "text": "확인: Route 상태를 점검합니다."},
                        {"kind": "code", "language": "bash", "code": "oc adm drain node-0 --ignore-daemonsets"},
                    ],
                },
            ],
        }
        settings.playbook_documents_path.write_text(
            json.dumps(source_payload, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        settings.playbook_books_dir.mkdir(parents=True, exist_ok=True)
        (settings.playbook_books_dir / "nodes.json").write_text(
            json.dumps(source_payload, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        summary = materialize_derived_playbooks(settings)
        sections = _project_materialized_derived_sections(settings)

        assert summary["generated_count"] == 5
        operation_section = next(
            section
            for section in sections
            if section.book_slug == "nodes_operations_playbook" and section.anchor == "node-drain"
        )
        assert operation_section.source_type == "operation_playbook"
        assert operation_section.source_lane == "applied_playbook"
        assert operation_section.cli_commands == ("oc adm drain node-0 --ignore-daemonsets",)
        assert operation_section.verification_hints == (
            "확인: Route 상태를 점검합니다.",
            "oc adm drain node-0 --ignore-daemonsets",
        )
        assert operation_section.viewer_path.endswith("/nodes_operations_playbook/index.html#node-drain")
