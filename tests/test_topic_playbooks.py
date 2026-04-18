from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import Settings
from play_book_studio.ingestion.topic_playbooks import (
    approved_materialized_derived_playbooks,
    approved_materialized_topic_playbooks,
    materialize_derived_playbooks,
    materialize_topic_playbooks,
)


class TopicPlaybookTests(unittest.TestCase):
    def test_materialize_topic_playbooks_derives_focused_backup_asset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            settings.playbook_documents_path.parent.mkdir(parents=True, exist_ok=True)
            settings.playbook_documents_path.write_text(
                json.dumps(
                    {
                        "canonical_model": "playbook_document_v1",
                        "source_view_strategy": "playbook_ast_v1",
                        "book_slug": "backup_and_restore",
                        "title": "Backup and restore",
                        "version": "4.20",
                        "locale": "ko",
                        "source_uri": "https://example.com/backup",
                        "translation_status": "approved_ko",
                        "review_status": "approved",
                        "source_metadata": {
                            "source_id": "manual_synthesis:backup_and_restore",
                            "source_type": "manual_synthesis",
                            "source_lane": "applied_playbook",
                        },
                        "sections": [
                            {
                                "section_id": "backup_and_restore:overview",
                                "section_key": "backup_and_restore:overview",
                                "ordinal": 1,
                                "heading": "개요",
                                "anchor": "overview",
                                "semantic_role": "overview",
                                "path": ["개요"],
                                "section_path": ["개요"],
                                "blocks": [{"kind": "paragraph", "text": "백업과 복구 전략 개요"}],
                            },
                            {
                                "section_id": "backup_and_restore:backup",
                                "section_key": "backup_and_restore:backup",
                                "ordinal": 2,
                                "heading": "etcd 백업 절차",
                                "anchor": "etcd-backup",
                                "semantic_role": "procedure",
                                "path": ["운영", "etcd 백업 절차"],
                                "section_path": ["운영", "etcd 백업 절차"],
                                "blocks": [
                                    {"kind": "paragraph", "text": "백업 전 확인"},
                                    {"kind": "code", "code": "cluster-backup.sh /backup"},
                                ],
                            },
                            {
                                "section_id": "backup_and_restore:restore",
                                "section_key": "backup_and_restore:restore",
                                "ordinal": 3,
                                "heading": "quorum 복원",
                                "anchor": "quorum-restore",
                                "semantic_role": "procedure",
                                "path": ["운영", "quorum 복원"],
                                "section_path": ["운영", "quorum 복원"],
                                "blocks": [{"kind": "code", "code": "quorum-restore.sh"}],
                            },
                        ],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            settings.playbook_books_dir.mkdir(parents=True, exist_ok=True)
            (settings.playbook_books_dir / "backup_and_restore.json").write_text(
                settings.playbook_documents_path.read_text(encoding="utf-8").strip() + "\n",
                encoding="utf-8",
            )

            summary = materialize_topic_playbooks(settings)

            self.assertIn("backup_restore_control_plane", summary["generated_slugs"])
            topic_rows = approved_materialized_topic_playbooks(settings)
            self.assertEqual(["backup_restore_control_plane"], [row["book_slug"] for row in topic_rows])
            topic_book = json.loads(
                (settings.playbook_books_dir / "backup_restore_control_plane.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual("topic_playbook", topic_book["source_metadata"]["source_type"])
            self.assertEqual("backup_and_restore", topic_book["source_metadata"]["derived_from_book_slug"])
            self.assertEqual("컨트롤 플레인 백업/복구 플레이북", topic_book["title"])
            self.assertIn("/docs/ocp/4.20/ko/backup_restore_control_plane/index.html#etcd-backup", topic_book["anchor_map"].values())
            self.assertFalse((settings.playbook_books_dir / "backup_and_restore_topic_playbook.json").exists())

    def test_materialize_derived_playbooks_skips_generic_manual_synthesis_without_curated_spec(self) -> None:
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
                },
                "sections": [
                    {
                        "section_id": "nodes:overview",
                        "section_key": "nodes:overview",
                        "ordinal": 1,
                        "heading": "개요",
                        "anchor": "overview",
                        "semantic_role": "overview",
                        "path": ["개요"],
                        "section_path": ["개요"],
                        "blocks": [{"kind": "paragraph", "text": "노드 운영 기본 개요"}],
                    },
                    {
                        "section_id": "nodes:drain",
                        "section_key": "nodes:drain",
                        "ordinal": 2,
                        "heading": "노드 드레인 절차",
                        "anchor": "node-drain",
                        "semantic_role": "procedure",
                        "path": ["운영", "노드 드레인 절차"],
                        "section_path": ["운영", "노드 드레인 절차"],
                        "blocks": [
                            {"kind": "paragraph", "text": "드레인 전 확인"},
                            {"kind": "code", "code": "oc adm drain node-0 --ignore-daemonsets"},
                        ],
                    },
                    {
                        "section_id": "nodes:debug",
                        "section_key": "nodes:debug",
                        "ordinal": 3,
                        "heading": "노드 장애 복구",
                        "anchor": "node-recovery",
                        "semantic_role": "reference",
                        "path": ["장애 대응", "노드 장애 복구"],
                        "section_path": ["장애 대응", "노드 장애 복구"],
                        "blocks": [
                            {"kind": "paragraph", "text": "노드 장애 징후"},
                            {"kind": "code", "code": "oc debug node/node-0"},
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

            derived_rows = approved_materialized_derived_playbooks(settings)
            self.assertEqual(0, summary["generated_count"])
            self.assertEqual({}, summary["family_counts"])
            self.assertEqual([], derived_rows)
            self.assertFalse((settings.playbook_books_dir / "nodes_topic_playbook.json").exists())
            self.assertFalse((settings.playbook_books_dir / "nodes_operations_playbook.json").exists())
            self.assertFalse((settings.playbook_books_dir / "nodes_policy_overlay_book.json").exists())
            self.assertFalse((settings.playbook_books_dir / "nodes_synthesized_playbook.json").exists())
            self.assertFalse((settings.playbook_books_dir / "nodes_troubleshooting_playbook.json").exists())

    def test_materialize_derived_playbooks_skips_generic_official_doc_without_curated_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            settings.playbook_documents_path.parent.mkdir(parents=True, exist_ok=True)
            source_payload = {
                "canonical_model": "playbook_document_v1",
                "source_view_strategy": "playbook_ast_v1",
                "book_slug": "advanced_networking",
                "title": "고급 네트워킹",
                "version": "4.20",
                "locale": "ko",
                "source_uri": "https://example.com/advanced-networking",
                "translation_status": "approved_ko",
                "review_status": "approved",
                "source_metadata": {
                    "source_id": "official_doc:advanced_networking",
                    "source_type": "official_doc",
                    "source_lane": "official_ko",
                },
                "sections": [
                    {
                        "section_id": "advanced_networking:overview",
                        "section_key": "advanced_networking:overview",
                        "ordinal": 1,
                        "heading": "고급 네트워킹 개요",
                        "anchor": "overview",
                        "semantic_role": "overview",
                        "path": ["개요"],
                        "section_path": ["개요"],
                        "blocks": [{"kind": "paragraph", "text": "고급 네트워킹 개요"}],
                    },
                    {
                        "section_id": "advanced_networking:egress",
                        "section_key": "advanced_networking:egress",
                        "ordinal": 2,
                        "heading": "egress IP 운영 절차",
                        "anchor": "egress-ip-ops",
                        "semantic_role": "procedure",
                        "path": ["운영", "egress IP 운영 절차"],
                        "section_path": ["운영", "egress IP 운영 절차"],
                        "blocks": [{"kind": "code", "code": "oc get egressip"}],
                    },
                    {
                        "section_id": "advanced_networking:policy",
                        "section_key": "advanced_networking:policy",
                        "ordinal": 3,
                        "heading": "지원 제한과 보안 고려 사항",
                        "anchor": "support-policy",
                        "semantic_role": "reference",
                        "path": ["제한", "지원 제한과 보안 고려 사항"],
                        "section_path": ["제한", "지원 제한과 보안 고려 사항"],
                        "blocks": [{"kind": "paragraph", "text": "지원 제한과 보안 고려 사항"}],
                    },
                ],
            }
            settings.playbook_documents_path.write_text(
                json.dumps(source_payload, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            settings.playbook_books_dir.mkdir(parents=True, exist_ok=True)
            (settings.playbook_books_dir / "advanced_networking.json").write_text(
                json.dumps(source_payload, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            summary = materialize_derived_playbooks(settings)

            derived_rows = approved_materialized_derived_playbooks(settings)
            self.assertEqual(0, summary["generated_count"])
            self.assertEqual({}, summary["family_counts"])
            self.assertEqual([], derived_rows)
            self.assertFalse(
                (settings.playbook_books_dir / "advanced_networking_topic_playbook.json").exists()
            )

    def test_materialize_derived_playbooks_prunes_stale_outputs_when_manual_loses_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            settings.playbook_documents_path.parent.mkdir(parents=True, exist_ok=True)
            approved_payload = {
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
                },
                "sections": [
                    {
                        "section_id": "nodes:overview",
                        "section_key": "nodes:overview",
                        "ordinal": 1,
                        "heading": "개요",
                        "anchor": "overview",
                        "semantic_role": "overview",
                        "path": ["개요"],
                        "section_path": ["개요"],
                        "blocks": [{"kind": "paragraph", "text": "노드 운영 기본 개요"}],
                    },
                    {
                        "section_id": "nodes:drain",
                        "section_key": "nodes:drain",
                        "ordinal": 2,
                        "heading": "노드 드레인 절차",
                        "anchor": "node-drain",
                        "semantic_role": "procedure",
                        "path": ["운영", "노드 드레인 절차"],
                        "section_path": ["운영", "노드 드레인 절차"],
                        "blocks": [{"kind": "code", "code": "oc adm drain node-0 --ignore-daemonsets"}],
                    },
                ],
            }
            settings.playbook_documents_path.write_text(
                json.dumps(approved_payload, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            settings.playbook_books_dir.mkdir(parents=True, exist_ok=True)
            (settings.playbook_books_dir / "nodes.json").write_text(
                json.dumps(approved_payload, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            materialize_derived_playbooks(settings)

            stale_payload = dict(approved_payload)
            stale_payload["translation_status"] = "draft"
            stale_payload["review_status"] = "review_pending"
            settings.playbook_documents_path.write_text(
                json.dumps(stale_payload, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            (settings.playbook_books_dir / "nodes.json").write_text(
                json.dumps(stale_payload, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            summary = materialize_derived_playbooks(settings)
            derived_rows = approved_materialized_derived_playbooks(settings)

            self.assertEqual(0, summary["generated_count"])
            self.assertEqual([], derived_rows)
            self.assertFalse((settings.playbook_books_dir / "nodes_topic_playbook.json").exists())
            self.assertFalse((settings.playbook_books_dir / "nodes_operations_playbook.json").exists())
            self.assertFalse((settings.playbook_books_dir / "nodes_policy_overlay_book.json").exists())
            self.assertFalse((settings.playbook_books_dir / "nodes_synthesized_playbook.json").exists())
            self.assertFalse(
                (settings.playbook_books_dir / "nodes_troubleshooting_playbook.json").exists()
            )

    def test_approved_materialized_derived_playbooks_filters_requested_family_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            settings.playbook_documents_path.parent.mkdir(parents=True, exist_ok=True)
            source_payload = {
                "canonical_model": "playbook_document_v1",
                "source_view_strategy": "playbook_ast_v1",
                "book_slug": "backup_and_restore",
                "title": "백업 및 복구 운영 가이드",
                "version": "4.20",
                "locale": "ko",
                "source_uri": "https://example.com/backup_and_restore",
                "translation_status": "approved_ko",
                "review_status": "approved",
                "source_metadata": {
                    "source_id": "manual_synthesis:backup_and_restore",
                    "source_type": "manual_synthesis",
                    "source_lane": "applied_playbook",
                },
                "sections": [
                    {
                        "section_id": "backup_and_restore:overview",
                        "section_key": "backup_and_restore:overview",
                        "ordinal": 1,
                        "heading": "개요",
                        "anchor": "overview",
                        "semantic_role": "overview",
                        "path": ["개요"],
                        "section_path": ["개요"],
                        "blocks": [{"kind": "paragraph", "text": "백업 및 복구 운영 개요"}],
                    },
                    {
                        "section_id": "backup_and_restore:backup",
                        "section_key": "backup_and_restore:backup",
                        "ordinal": 2,
                        "heading": "etcd 백업 절차",
                        "anchor": "etcd-backup",
                        "semantic_role": "procedure",
                        "path": ["운영", "etcd 백업 절차"],
                        "section_path": ["운영", "etcd 백업 절차"],
                        "blocks": [{"kind": "code", "code": "cluster-backup.sh /backup"}],
                    },
                ],
            }
            settings.playbook_documents_path.write_text(
                json.dumps(source_payload, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            settings.playbook_books_dir.mkdir(parents=True, exist_ok=True)
            (settings.playbook_books_dir / "backup_and_restore.json").write_text(
                json.dumps(source_payload, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            materialize_derived_playbooks(settings)

            operation_rows = approved_materialized_derived_playbooks(
                settings,
                families=("operation_playbook",),
            )
            troubleshooting_rows = approved_materialized_derived_playbooks(
                settings,
                families=("troubleshooting_playbook",),
            )

            self.assertEqual(["backup_restore_operations"], [row["book_slug"] for row in operation_rows])
            self.assertEqual(
                ["backup_restore_recovery_troubleshooting"],
                [row["book_slug"] for row in troubleshooting_rows],
            )

    def test_materialize_derived_playbooks_keeps_lineage_metadata_per_family(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            settings.playbook_documents_path.parent.mkdir(parents=True, exist_ok=True)
            source_payload = {
                "canonical_model": "playbook_document_v1",
                "source_view_strategy": "playbook_ast_v1",
                "book_slug": "etcd",
                "title": "etcd 운영 가이드",
                "version": "4.20",
                "locale": "ko",
                "source_uri": "https://example.com/etcd",
                "translation_status": "approved_ko",
                "review_status": "approved",
                "source_metadata": {
                    "source_id": "manual_synthesis:etcd",
                    "source_type": "manual_synthesis",
                    "source_lane": "applied_playbook",
                },
                "sections": [
                    {
                        "section_id": "etcd:overview",
                        "section_key": "etcd:overview",
                        "ordinal": 1,
                        "heading": "개요",
                        "anchor": "overview",
                        "semantic_role": "overview",
                        "path": ["개요"],
                        "section_path": ["개요"],
                        "blocks": [{"kind": "paragraph", "text": "etcd 운영 개요"}],
                    },
                    {
                        "section_id": "etcd:restore",
                        "section_key": "etcd:restore",
                        "ordinal": 2,
                        "heading": "quorum restore",
                        "anchor": "quorum-restore",
                        "semantic_role": "procedure",
                        "path": ["운영", "quorum restore"],
                        "section_path": ["운영", "quorum restore"],
                        "blocks": [{"kind": "code", "code": "quorum-restore.sh"}],
                    },
                ],
            }
            settings.playbook_documents_path.write_text(
                json.dumps(source_payload, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            settings.playbook_books_dir.mkdir(parents=True, exist_ok=True)
            (settings.playbook_books_dir / "etcd.json").write_text(
                json.dumps(source_payload, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            materialize_derived_playbooks(settings)

            topic_book = json.loads(
                (settings.playbook_books_dir / "etcd_backup_restore.json").read_text(encoding="utf-8")
            )
            troubleshooting_book = json.loads(
                (settings.playbook_books_dir / "etcd_quorum_troubleshooting.json").read_text(encoding="utf-8")
            )

            self.assertEqual("topic_playbook", topic_book["source_metadata"]["derived_family"])
            self.assertEqual("topic_playbook", topic_book["source_metadata"]["source_type"])
            self.assertEqual(
                "manual_synthesis:etcd:topic_playbook:etcd_backup_restore",
                topic_book["source_metadata"]["source_id"],
            )
            self.assertEqual(
                "troubleshooting_playbook",
                troubleshooting_book["source_metadata"]["derived_family"],
            )
            self.assertEqual(
                "manual_synthesis:etcd:troubleshooting_playbook:etcd_quorum_troubleshooting",
                troubleshooting_book["source_metadata"]["source_id"],
            )

    def test_approved_materialized_topic_playbooks_returns_topic_family_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            settings.playbook_documents_path.parent.mkdir(parents=True, exist_ok=True)
            source_payload = {
                "canonical_model": "playbook_document_v1",
                "source_view_strategy": "playbook_ast_v1",
                "book_slug": "backup_and_restore",
                "title": "백업 및 복구 운영 가이드",
                "version": "4.20",
                "locale": "ko",
                "source_uri": "https://example.com/backup_and_restore",
                "translation_status": "approved_ko",
                "review_status": "approved",
                "source_metadata": {
                    "source_id": "manual_synthesis:backup_and_restore",
                    "source_type": "manual_synthesis",
                    "source_lane": "applied_playbook",
                },
                "sections": [
                    {
                        "section_id": "backup_and_restore:overview",
                        "section_key": "backup_and_restore:overview",
                        "ordinal": 1,
                        "heading": "개요",
                        "anchor": "overview",
                        "semantic_role": "overview",
                        "path": ["개요"],
                        "section_path": ["개요"],
                        "blocks": [{"kind": "paragraph", "text": "백업 및 복구 운영 개요"}],
                    },
                    {
                        "section_id": "backup_and_restore:backup",
                        "section_key": "backup_and_restore:backup",
                        "ordinal": 2,
                        "heading": "etcd 백업 절차",
                        "anchor": "etcd-backup",
                        "semantic_role": "procedure",
                        "path": ["운영", "etcd 백업 절차"],
                        "section_path": ["운영", "etcd 백업 절차"],
                        "blocks": [{"kind": "code", "code": "cluster-backup.sh /backup"}],
                    },
                ],
            }
            settings.playbook_documents_path.write_text(
                json.dumps(source_payload, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            settings.playbook_books_dir.mkdir(parents=True, exist_ok=True)
            (settings.playbook_books_dir / "backup_and_restore.json").write_text(
                json.dumps(source_payload, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            materialize_derived_playbooks(settings)

            topic_rows = approved_materialized_topic_playbooks(settings)

            self.assertEqual(["backup_restore_control_plane"], [row["book_slug"] for row in topic_rows])
            self.assertEqual("topic_playbook", topic_rows[0]["source_metadata"]["source_type"])
