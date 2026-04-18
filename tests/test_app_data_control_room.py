from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from _support_app_ui import SessionStore, _build_handler, _ingest_customer_pack
from play_book_studio.app.data_control_room import build_data_control_room_payload
from play_book_studio.config.settings import load_settings


class TestAppDataControlRoom(unittest.TestCase):
    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _write_jsonl(self, path: Path, rows: list[dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        body = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows)
        path.write_text(body, encoding="utf-8")

    def test_build_data_control_room_payload_summarizes_gold_corpus_and_manualbook(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text("ARTIFACTS_DIR=artifacts\n", encoding="utf-8")
            settings = load_settings(root)

            manifest_entry = {
                "book_slug": "architecture",
                "title": "아키텍처",
                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html",
                "content_status": "approved_ko",
                "review_status": "approved",
                "source_type": "official_doc",
                "source_lane": "official_ko",
                "legal_notice_url": "https://example.com/legal",
                "updated_at": "2026-04-11T09:00:00+09:00",
            }
            queue_manifest_entry = {
                "book_slug": "operators",
                "title": "오퍼레이터",
                "viewer_path": "/docs/ocp/4.20/ko/operators/index.html",
                "source_url": "https://example.com/operators",
                "content_status": "translated_ko_draft",
                "review_status": "needs_review",
                "source_type": "manual_synthesis",
                "source_lane": "applied_playbook",
                "legal_notice_url": "https://example.com/legal",
                "updated_at": "2026-04-11T09:05:00+09:00",
            }
            self._write_json(
                settings.source_manifest_path,
                {
                    "version": 2,
                    "count": 2,
                    "entries": [manifest_entry, queue_manifest_entry],
                },
            )

            self._write_json(
                root / "reports" / "build_logs" / "foundry_runs" / "profiles" / "morning_gate" / "latest.json",
                {
                    "run_at": "2026-04-11T09:30:00+09:00",
                    "job_results": [
                        {
                            "job_id": "source_approval",
                            "payload": {
                                "output_targets": {
                                    "approval_report_path": str(root / "reports" / "approval.json"),
                                    "translation_lane_report_path": str(root / "reports" / "translation_lane.json"),
                                }
                            },
                        },
                        {
                            "job_id": "runtime_smoke",
                            "payload": {
                                "probes": {
                                    "embedding": {"health_status": 200, "sample_embedding_ok": True},
                                }
                            },
                        },
                    ],
                    "verdict": {
                        "status": "release_ready",
                        "release_blocking": False,
                        "summary": {
                            "approved_runtime_count": 1,
                            "translation_ready_count": 0,
                            "manual_review_ready_count": 0,
                            "high_value_issue_count": 0,
                            "source_expansion_needed_count": 0,
                            "failed_validation_checks": [],
                            "failed_data_quality_checks": [],
                        },
                    },
                },
            )

            self._write_json(
                root / "reports" / "approval.json",
                {
                    "summary": {
                        "book_count": 2,
                        "approved_ko_count": 1,
                        "translated_ko_draft_count": 1,
                        "blocked_count": 0,
                    },
                    "books": [
                        {
                            "book_slug": "architecture",
                            "title": "아키텍처",
                            "content_status": "approved_ko",
                            "approval_status": "approved",
                            "review_status": "approved",
                            "source_type": "official_doc",
                            "source_lane": "official_ko",
                            "chunk_count": 2,
                            "section_count": 1,
                            "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html",
                            "source_url": "https://example.com/architecture",
                            "updated_at": "2026-04-11T09:00:00+09:00",
                            "translation_lane": {"runtime_eligible": True},
                        },
                        {
                            "book_slug": "operators",
                            "title": "Operators",
                            "content_status": "translated_ko_draft",
                            "approval_status": "needs_review",
                            "review_status": "needs_review",
                            "source_type": "manual_synthesis",
                            "source_lane": "applied_playbook",
                            "chunk_count": 0,
                            "section_count": 0,
                            "high_value": True,
                            "translation_lane": {"runtime_eligible": False},
                        },
                    ],
                },
            )
            self._write_json(
                root / "reports" / "translation_lane.json",
                {
                    "active_queue": [
                        {
                            "book_slug": "operators",
                            "title": "Operators",
                            "content_status": "translated_ko_draft",
                            "approval_status": "needs_review",
                            "review_status": "needs_review",
                        }
                    ]
                },
            )

            self._write_json(
                settings.retrieval_eval_report_path,
                {"overall": {"book_hit_at_1": 1.0, "book_hit_at_3": 1.0, "case_count": 4}},
            )
            self._write_json(
                settings.answer_eval_report_path,
                {"overall": {"pass_rate": 1.0, "avg_citation_precision": 0.75, "case_count": 4}},
            )
            self._write_json(
                settings.ragas_eval_report_path,
                {"overall": {"faithfulness": 0.8, "answer_relevancy": 0.7}},
            )
            self._write_json(
                settings.runtime_report_path,
                {
                    "app": {"pack_id": settings.active_pack_id},
                    "runtime": {"llm_model": "qwen"},
                    "probes": {"embedding": {"health_status": 200}},
                },
            )

            self._write_jsonl(
                settings.chunks_path,
                [
                    {
                        "book_slug": "architecture",
                        "book_title": "아키텍처",
                        "token_count": 100,
                        "chunk_type": "reference",
                        "anchor_id": "overview",
                        "review_status": "approved",
                        "source_type": "official_doc",
                        "source_lane": "official_ko",
                        "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                    },
                    {
                        "book_slug": "architecture",
                        "book_title": "아키텍처",
                        "token_count": 120,
                        "chunk_type": "procedure",
                        "anchor_id": "topology",
                        "cli_commands": ["oc get nodes"],
                        "review_status": "approved",
                        "source_type": "official_doc",
                        "source_lane": "official_ko",
                        "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#topology",
                    },
                ],
            )
            self._write_json(
                settings.playbook_books_dir / "architecture.json",
                {
                    "book_slug": "architecture",
                    "title": "아키텍처",
                    "translation_status": "approved_ko",
                    "review_status": "approved",
                    "legal_notice_url": "https://example.com/legal",
                    "anchor_map": {
                        "overview": "/docs/ocp/4.20/ko/architecture/index.html#overview"
                    },
                    "source_metadata": {
                        "source_type": "official_doc",
                        "source_lane": "official_ko",
                        "updated_at": "2026-04-11T09:00:00+09:00",
                    },
                    "sections": [
                        {
                            "semantic_role": "overview",
                            "blocks": [
                                {"kind": "paragraph", "text": "개요"},
                                {"kind": "code", "text": "oc get nodes"},
                            ],
                        }
                    ],
                },
            )

            payload = build_data_control_room_payload(root)

            self.assertEqual("release_ready", payload["summary"]["gate_status"])
            self.assertEqual("release_ready", payload["gate"]["status"])
            self.assertEqual(2, payload["summary"]["known_book_count"])
            self.assertEqual(2, payload["summary"]["known_books_count"])
            self.assertEqual(1, payload["summary"]["gold_book_count"])
            self.assertEqual(2, payload["summary"]["raw_manual_count"])
            self.assertEqual(1, payload["summary"]["queue_count"])
            self.assertEqual(1, payload["summary"]["active_queue_count"])
            self.assertEqual(2, payload["summary"]["chunk_count"])
            self.assertEqual(1, payload["summary"]["corpus_book_count"])
            self.assertEqual(1, payload["summary"]["core_corpus_book_count"])
            self.assertEqual(1, payload["summary"]["manualbook_count"])
            self.assertEqual(1, payload["summary"]["core_manualbook_count"])
            self.assertEqual(0, payload["summary"]["topic_playbook_count"])
            self.assertEqual(0, payload["summary"]["operation_playbook_count"])
            self.assertEqual(0, payload["summary"]["troubleshooting_playbook_count"])
            self.assertEqual(0, payload["summary"]["policy_overlay_book_count"])
            self.assertEqual(0, payload["summary"]["synthesized_playbook_count"])
            self.assertEqual(1, len(payload["gold_books"]))
            self.assertEqual("architecture", payload["gold_books"][0]["book_slug"])
            self.assertEqual(1, len(payload["grading"]["queue_books"]))
            self.assertEqual("operators", payload["grading"]["queue_books"][0]["book_slug"])
            self.assertEqual(1.0, payload["evaluations"]["retrieval"]["book_hit_at_1"])
            self.assertEqual(1.0, payload["evaluations"]["answer"]["pass_rate"])
            self.assertEqual(2, len(payload["known_books"]))
            self.assertEqual("operators", payload["known_books"][1]["book_slug"])
            self.assertEqual(
                "/docs/ocp/4.20/ko/operators/index.html",
                payload["known_books"][1]["viewer_path"],
            )
            self.assertEqual(
                "https://example.com/operators",
                payload["known_books"][1]["source_url"],
            )
            self.assertEqual(1, len(payload["active_queue"]))
            self.assertEqual("operators", payload["active_queue"][0]["book_slug"])
            self.assertEqual(2, len(payload["corpus_book_status"]))
            self.assertEqual("Silver", payload["corpus_book_status"][1]["grade"])
            self.assertEqual(0, payload["corpus_book_status"][1]["chunk_count"])
            self.assertEqual("https://example.com/operators", payload["corpus_book_status"][1]["source_url"])
            self.assertFalse(payload["corpus_book_status"][1]["materialized"])
            self.assertEqual(2, len(payload["manualbook_status"]))
            self.assertEqual("operators", payload["manualbook_status"][1]["book_slug"])
            self.assertEqual(0, payload["manualbook_status"][1]["section_count"])
            self.assertEqual("https://example.com/operators", payload["manualbook_status"][1]["source_url"])
            self.assertFalse(payload["manualbook_status"][1]["materialized"])
            self.assertEqual(2, payload["manual_book_library"]["total_count"])
            self.assertEqual(2, payload["manual_book_library"]["core_count"])
            self.assertEqual(0, payload["manual_book_library"]["extra_count"])
            self.assertEqual(
                ["architecture", "operators"],
                [book["book_slug"] for book in payload["manual_book_library"]["books"]],
            )
            self.assertEqual(0, payload["playbook_library"]["total_count"])
            self.assertEqual(0, payload["playbook_library"]["family_count"])
            self.assertFalse(payload["source_of_truth"]["chunks"]["drift_detected"])
            self.assertTrue(payload["materialization"]["logical_counts_match"])
            self.assertFalse(payload["materialization"]["counts_match"])
            self.assertEqual(1, payload["materialization"]["materialized_corpus_book_count"])
            self.assertEqual(1, payload["materialization"]["materialized_manualbook_book_count"])
            self.assertEqual(0, payload["materialization"]["extra_corpus_book_count"])
            self.assertEqual(0, payload["materialization"]["extra_manualbook_book_count"])
            self.assertEqual(0, payload["materialization"]["materialized_policy_overlay_book_count"])
            self.assertEqual(0, payload["materialization"]["materialized_synthesized_playbook_count"])
            self.assertEqual(["operators"], payload["materialization"]["missing_corpus_books"])
            self.assertEqual(["operators"], payload["materialization"]["missing_manualbook_books"])
            self.assertEqual("not_emitted", payload["derived_playbook_families"]["policy_overlay_book"]["status"])
            self.assertEqual("not_emitted", payload["derived_playbook_families"]["synthesized_playbook"]["status"])
            self.assertEqual("source_approval_report", payload["canonical_grade_source"]["name"])
            self.assertEqual(1, payload["source_of_truth_drift"]["status_alignment"]["approved_runtime_count"])
            self.assertIn("reports", payload)
            self.assertIn("recent_report_paths", payload)

    def test_build_data_control_room_payload_prefers_current_corpus_report_when_gate_snapshot_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text("ARTIFACTS_DIR=artifacts\n", encoding="utf-8")
            settings = load_settings(root)

            entries = [
                {
                    "book_slug": "architecture",
                    "title": "아키텍처",
                    "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html",
                    "content_status": "approved_ko",
                    "review_status": "approved",
                    "source_type": "official_doc",
                    "source_lane": "official_ko",
                    "updated_at": "2026-04-11T09:00:00+09:00",
                },
                {
                    "book_slug": "operators",
                    "title": "오퍼레이터",
                    "viewer_path": "/docs/ocp/4.20/ko/operators/index.html",
                    "content_status": "approved_ko",
                    "review_status": "approved",
                    "source_type": "manual_synthesis",
                    "source_lane": "applied_playbook",
                    "updated_at": "2026-04-11T09:05:00+09:00",
                },
            ]
            self._write_json(
                settings.source_manifest_path,
                {"version": 2, "count": 2, "entries": entries},
            )

            gate_approval_path = root / "reports" / "approval_stale.json"
            gate_translation_path = root / "reports" / "translation_stale.json"
            self._write_json(
                root / "reports" / "build_logs" / "foundry_runs" / "profiles" / "morning_gate" / "latest.json",
                {
                    "run_at": "2026-04-11T09:30:00+09:00",
                    "job_results": [
                        {
                            "job_id": "source_approval",
                            "payload": {
                                "output_targets": {
                                    "approval_report_path": str(gate_approval_path),
                                    "translation_lane_report_path": str(gate_translation_path),
                                }
                            },
                        }
                    ],
                    "verdict": {
                        "status": "release_ready",
                        "release_blocking": False,
                        "summary": {"approved_runtime_count": 1},
                    },
                },
            )
            self._write_json(
                gate_approval_path,
                {
                    "summary": {"book_count": 3, "approved_ko_count": 1, "blocked_count": 2},
                    "books": [
                        {
                            "book_slug": "architecture",
                            "title": "아키텍처",
                            "content_status": "approved_ko",
                            "approval_status": "approved",
                            "review_status": "approved",
                            "source_type": "official_doc",
                            "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html",
                        },
                        {
                            "book_slug": "operators",
                            "title": "오퍼레이터",
                            "content_status": "blocked",
                            "approval_status": "needs_review",
                            "review_status": "needs_review",
                            "source_type": "manual_synthesis",
                            "viewer_path": "/docs/ocp/4.20/ko/operators/index.html",
                        },
                        {
                            "book_slug": "storage",
                            "title": "스토리지",
                            "content_status": "blocked",
                            "approval_status": "needs_review",
                            "review_status": "needs_review",
                            "source_type": "official_doc",
                            "viewer_path": "/docs/ocp/4.20/ko/storage/index.html",
                        },
                    ],
                },
            )
            self._write_json(gate_translation_path, {"active_queue": [{"book_slug": "operators"}]})

            self._write_json(
                settings.source_approval_report_path,
                {
                    "summary": {"book_count": 3, "approved_ko_count": 2, "blocked_count": 1},
                    "books": [
                        {
                            "book_slug": "architecture",
                            "title": "아키텍처",
                            "content_status": "approved_ko",
                            "approval_status": "approved",
                            "review_status": "approved",
                            "source_type": "official_doc",
                            "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html",
                        },
                        {
                            "book_slug": "operators",
                            "title": "오퍼레이터",
                            "content_status": "approved_ko",
                            "approval_status": "approved",
                            "review_status": "approved",
                            "source_type": "manual_synthesis",
                            "viewer_path": "/docs/ocp/4.20/ko/operators/index.html",
                        },
                        {
                            "book_slug": "storage",
                            "title": "스토리지",
                            "content_status": "blocked",
                            "approval_status": "needs_review",
                            "review_status": "needs_review",
                            "source_type": "official_doc",
                            "viewer_path": "/docs/ocp/4.20/ko/storage/index.html",
                        },
                    ],
                },
            )
            self._write_json(
                settings.translation_lane_report_path,
                {"summary": {"active_queue_count": 1}, "active_queue": [{"book_slug": "storage"}]},
            )

            self._write_jsonl(
                settings.chunks_path,
                [
                    {"book_slug": "architecture", "book_title": "아키텍처", "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview"},
                    {"book_slug": "operators", "book_title": "오퍼레이터", "viewer_path": "/docs/ocp/4.20/ko/operators/index.html#overview"},
                ],
            )
            self._write_json(
                settings.playbook_books_dir / "architecture.json",
                {
                    "book_slug": "architecture",
                    "title": "아키텍처",
                    "translation_status": "approved_ko",
                    "review_status": "approved",
                    "source_metadata": {"source_type": "official_doc", "source_lane": "official_ko"},
                    "sections": [{"blocks": [{"kind": "paragraph", "text": "개요"}]}],
                },
            )
            self._write_json(
                settings.playbook_books_dir / "operators.json",
                {
                    "book_slug": "operators",
                    "title": "오퍼레이터",
                    "translation_status": "approved_ko",
                    "review_status": "approved",
                    "source_metadata": {"source_type": "manual_synthesis", "source_lane": "applied_playbook"},
                    "sections": [{"blocks": [{"kind": "paragraph", "text": "절차"}]}],
                },
            )

            payload = build_data_control_room_payload(root)

            self.assertEqual(str(settings.source_approval_report_path), payload["canonical_grade_source"]["path"])
            self.assertEqual(2, payload["summary"]["approved_runtime_count"])
            self.assertEqual(2, payload["summary"]["gold_book_count"])
            self.assertEqual(2, len(payload["gold_books"]))
            self.assertEqual(3, payload["summary"]["known_book_count"])
            self.assertEqual(
                ["gate_approved_runtime_count_vs_source_approval_approved_ko_count"],
                payload["source_of_truth_drift"]["status_alignment"]["mismatches"],
            )

    def test_build_data_control_room_payload_separates_extra_playable_books_from_runtime_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text("ARTIFACTS_DIR=artifacts\n", encoding="utf-8")
            settings = load_settings(root)

            manifest_entry = {
                "book_slug": "architecture",
                "title": "아키텍처",
                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html",
                "content_status": "approved_ko",
                "review_status": "approved",
                "source_type": "official_doc",
                "source_lane": "official_ko",
                "updated_at": "2026-04-11T09:00:00+09:00",
            }
            self._write_json(
                settings.source_manifest_path,
                {"version": 2, "count": 1, "entries": [manifest_entry]},
            )
            self._write_json(
                root / "reports" / "build_logs" / "foundry_runs" / "profiles" / "morning_gate" / "latest.json",
                {
                    "job_results": [
                        {
                            "job_id": "source_approval",
                            "payload": {
                                "output_targets": {
                                    "approval_report_path": str(root / "reports" / "approval.json"),
                                    "translation_lane_report_path": str(root / "reports" / "translation_lane.json"),
                                }
                            },
                        }
                    ],
                    "verdict": {
                        "status": "release_ready",
                        "release_blocking": False,
                        "summary": {"approved_runtime_count": 1},
                    }
                },
            )
            self._write_json(
                root / "reports" / "approval.json",
                {
                    "summary": {"book_count": 1, "approved_ko_count": 1, "blocked_count": 0},
                    "books": [
                        {
                            "book_slug": "architecture",
                            "title": "아키텍처",
                            "content_status": "approved_ko",
                            "approval_status": "approved",
                            "review_status": "approved",
                            "source_type": "official_doc",
                            "source_lane": "official_ko",
                            "translation_lane": {"runtime_eligible": True},
                        }
                    ],
                },
            )
            self._write_json(root / "reports" / "translation_lane.json", {"active_queue": []})
            self._write_json(settings.retrieval_eval_report_path, {"overall": {}})
            self._write_json(settings.answer_eval_report_path, {"overall": {}})
            self._write_json(settings.ragas_eval_report_path, {"overall": {}})
            self._write_json(settings.runtime_report_path, {"app": {}, "runtime": {}, "probes": {}})

            self._write_jsonl(
                settings.chunks_path,
                [
                    {"book_slug": "architecture", "book_title": "아키텍처", "token_count": 10, "chunk_type": "reference"},
                    {"book_slug": "backup_and_restore", "book_title": "백업", "token_count": 12, "chunk_type": "procedure"},
                ],
            )
            self._write_json(
                settings.playbook_books_dir / "architecture.json",
                {
                    "book_slug": "architecture",
                    "title": "아키텍처",
                    "translation_status": "approved_ko",
                    "review_status": "approved",
                    "source_metadata": {"source_type": "official_doc", "source_lane": "official_ko"},
                    "sections": [{"semantic_role": "overview", "blocks": [{"kind": "paragraph", "text": "개요"}]}],
                    "anchor_map": {},
                },
            )
            self._write_json(
                settings.playbook_books_dir / "backup_and_restore.json",
                {
                    "book_slug": "backup_and_restore",
                    "title": "백업",
                    "translation_status": "approved_ko",
                    "review_status": "approved",
                    "source_metadata": {"source_type": "manual_synthesis", "source_lane": "applied_playbook"},
                    "sections": [{"semantic_role": "procedure", "blocks": [{"kind": "code", "text": "cluster-backup.sh"}]}],
                    "anchor_map": {},
                },
            )
            self._write_json(
                settings.playbook_books_dir / "backup_restore_control_plane.json",
                {
                    "book_slug": "backup_restore_control_plane",
                    "title": "컨트롤 플레인 백업/복구 플레이북",
                    "translation_status": "approved_ko",
                    "review_status": "approved",
                    "source_metadata": {"source_type": "topic_playbook", "source_lane": "applied_playbook"},
                    "sections": [{"semantic_role": "procedure", "blocks": [{"kind": "code", "text": "restore.sh"}]}],
                    "anchor_map": {},
                },
            )
            self._write_json(
                settings.playbook_books_dir / "backup_restore_operations.json",
                {
                    "book_slug": "backup_restore_operations",
                    "title": "컨트롤 플레인 백업 운영 플레이북",
                    "translation_status": "approved_ko",
                    "review_status": "approved",
                    "source_metadata": {"source_type": "operation_playbook", "source_lane": "applied_playbook"},
                    "sections": [{"semantic_role": "procedure", "blocks": [{"kind": "code", "text": "cluster-backup.sh"}]}],
                    "anchor_map": {},
                },
            )
            self._write_json(
                settings.playbook_books_dir / "backup_restore_recovery_troubleshooting.json",
                {
                    "book_slug": "backup_restore_recovery_troubleshooting",
                    "title": "컨트롤 플레인 복구 트러블슈팅 플레이북",
                    "translation_status": "approved_ko",
                    "review_status": "approved",
                    "source_metadata": {"source_type": "troubleshooting_playbook", "source_lane": "applied_playbook"},
                    "sections": [{"semantic_role": "procedure", "blocks": [{"kind": "code", "text": "restore.sh"}]}],
                    "anchor_map": {},
                },
            )
            self._write_json(
                settings.playbook_books_dir / "backup_restore_policy_overlay.json",
                {
                    "book_slug": "backup_restore_policy_overlay",
                    "title": "컨트롤 플레인 백업 정책 오버레이 북",
                    "translation_status": "approved_ko",
                    "review_status": "approved",
                    "source_metadata": {"source_type": "policy_overlay_book", "source_lane": "applied_playbook"},
                    "sections": [{"semantic_role": "reference", "blocks": [{"kind": "paragraph", "text": "보존 정책"}]}],
                    "anchor_map": {},
                },
            )
            self._write_json(
                settings.playbook_books_dir / "backup_restore_synthesized_playbook.json",
                {
                    "book_slug": "backup_restore_synthesized_playbook",
                    "title": "컨트롤 플레인 백업 종합 플레이북",
                    "translation_status": "approved_ko",
                    "review_status": "approved",
                    "source_metadata": {"source_type": "synthesized_playbook", "source_lane": "applied_playbook"},
                    "sections": [{"semantic_role": "procedure", "blocks": [{"kind": "code", "text": "cluster-backup.sh && restore.sh"}]}],
                    "anchor_map": {},
                },
            )

            payload = build_data_control_room_payload(root)

            self.assertEqual(1, payload["summary"]["corpus_book_count"])
            self.assertEqual(1, payload["summary"]["core_corpus_book_count"])
            self.assertEqual(1, payload["summary"]["manualbook_count"])
            self.assertEqual(1, payload["summary"]["core_manualbook_count"])
            self.assertEqual(1, payload["summary"]["topic_playbook_count"])
            self.assertEqual(1, payload["summary"]["operation_playbook_count"])
            self.assertEqual(1, payload["summary"]["troubleshooting_playbook_count"])
            self.assertEqual(1, payload["summary"]["policy_overlay_book_count"])
            self.assertEqual(1, payload["summary"]["synthesized_playbook_count"])
            self.assertEqual(5, payload["summary"]["derived_playbook_count"])
            self.assertEqual(7, payload["summary"]["playable_asset_count"])
            self.assertEqual(1, payload["summary"]["extra_corpus_book_count"])
            self.assertEqual(1, payload["summary"]["extra_manualbook_count"])
            self.assertTrue(payload["materialization"]["logical_counts_match"])
            self.assertTrue(payload["materialization"]["counts_match"])
            self.assertEqual(1, payload["materialization"]["core_corpus_book_count"])
            self.assertEqual(1, payload["materialization"]["core_manualbook_book_count"])
            self.assertEqual(5, payload["materialization"]["derived_playbook_book_count"])
            self.assertEqual(1, payload["materialization"]["materialized_operation_playbook_count"])
            self.assertEqual(1, payload["materialization"]["materialized_troubleshooting_playbook_count"])
            self.assertEqual(1, payload["materialization"]["materialized_policy_overlay_book_count"])
            self.assertEqual(1, payload["materialization"]["materialized_synthesized_playbook_count"])
            self.assertEqual(7.0, payload["materialization"]["playable_asset_multiplication"]["ratio_vs_raw_manual_count"])
            self.assertEqual(1, payload["materialization"]["extra_corpus_book_count"])
            self.assertEqual(1, payload["materialization"]["extra_manualbook_book_count"])
            self.assertEqual(["backup_and_restore"], payload["materialization"]["extra_corpus_books"])
            self.assertEqual(["backup_and_restore"], payload["materialization"]["extra_manualbook_books"])
            self.assertEqual(["architecture"], [book["book_slug"] for book in payload["manualbook_status"]])
            self.assertEqual(["architecture"], [book["book_slug"] for book in payload["corpus_book_status"]])
            self.assertEqual(["backup_and_restore"], [book["book_slug"] for book in payload["extra_manualbook_status"]])
            self.assertEqual(["backup_and_restore"], [book["book_slug"] for book in payload["extra_corpus_book_status"]])
            self.assertEqual(["backup_restore_control_plane"], [book["book_slug"] for book in payload["topic_playbook_status"]])
            self.assertEqual(["backup_restore_operations"], [book["book_slug"] for book in payload["operation_playbook_status"]])
            self.assertEqual(
                ["backup_restore_recovery_troubleshooting"],
                [book["book_slug"] for book in payload["troubleshooting_playbook_status"]],
            )
            self.assertEqual(
                ["backup_restore_policy_overlay"],
                [book["book_slug"] for book in payload["policy_overlay_book_status"]],
            )
            self.assertEqual(
                ["backup_restore_synthesized_playbook"],
                [book["book_slug"] for book in payload["synthesized_playbook_status"]],
            )
            self.assertEqual(
                "materialized",
                payload["derived_playbook_families"]["operation_playbook"]["status"],
            )
            self.assertEqual(
                "materialized",
                payload["derived_playbook_families"]["policy_overlay_book"]["status"],
            )
            self.assertEqual(
                "materialized",
                payload["derived_playbook_families"]["synthesized_playbook"]["status"],
            )
            self.assertEqual(2, payload["manual_book_library"]["total_count"])
            self.assertEqual(1, payload["manual_book_library"]["core_count"])
            self.assertEqual(1, payload["manual_book_library"]["extra_count"])
            self.assertEqual(
                ["architecture", "backup_and_restore"],
                [book["book_slug"] for book in payload["manual_book_library"]["books"]],
            )
            self.assertEqual(5, payload["playbook_library"]["total_count"])
            self.assertEqual(5, payload["playbook_library"]["family_count"])
            self.assertEqual(
                {
                    "topic_playbook",
                    "operation_playbook",
                    "troubleshooting_playbook",
                    "policy_overlay_book",
                    "synthesized_playbook",
                },
                {family["family"] for family in payload["playbook_library"]["families"]},
            )

    def test_build_data_control_room_payload_includes_customer_pack_books_in_library(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text("ARTIFACTS_DIR=artifacts\n", encoding="utf-8")
            source_md = root / "customer-runbook.md"
            source_md.write_text(
                "# 운영 런북\n\n## etcd 백업\n\n```bash\ncluster-backup.sh /backup\n```\n\n## 검증\n\n백업 파일을 점검합니다.\n",
                encoding="utf-8",
            )

            normalized = _ingest_customer_pack(
                root,
                {
                    "source_type": "md",
                    "uri": str(source_md),
                    "title": "운영 런북",
                },
            )
            payload = build_data_control_room_payload(root)

            self.assertEqual("normalized", normalized["status"])
            self.assertEqual(1, payload["manual_book_library"]["total_count"])
            self.assertEqual(0, payload["manual_book_library"]["core_count"])
            self.assertEqual(1, payload["manual_book_library"]["extra_count"])
            self.assertEqual(1, payload["summary"]["extra_manualbook_count"])
            self.assertEqual(1, payload["summary"]["user_library_book_count"])
            self.assertEqual(5, payload["summary"]["derived_playbook_count"])
            self.assertEqual(6, payload["summary"]["playable_asset_count"])
            self.assertEqual([str(normalized["draft_id"])], [book["book_slug"] for book in payload["extra_manualbook_status"]])
            self.assertEqual(
                [str(normalized["draft_id"])],
                [book["book_slug"] for book in payload["user_library_books"]["books"]],
            )
            self.assertEqual(
                f"/playbooks/customer-packs/{normalized['draft_id']}/index.html",
                payload["manual_book_library"]["books"][0]["viewer_path"],
            )
            self.assertEqual(5, payload["playbook_library"]["total_count"])
            self.assertEqual(5, payload["playbook_library"]["family_count"])
            self.assertEqual(
                {
                    "topic_playbook",
                    "operation_playbook",
                    "troubleshooting_playbook",
                    "policy_overlay_book",
                    "synthesized_playbook",
                },
                {family["family"] for family in payload["playbook_library"]["families"]},
            )

    def test_build_data_control_room_payload_fails_closed_for_missing_product_rehearsal(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text("ARTIFACTS_DIR=artifacts\n", encoding="utf-8")
            settings = load_settings(root)
            self._write_json(settings.source_manifest_path, {"version": 2, "count": 0, "entries": []})
            self._write_json(
                root / "reports" / "build_logs" / "foundry_runs" / "profiles" / "morning_gate" / "latest.json",
                {"verdict": {"status": "blocked", "release_blocking": True, "summary": {}}},
            )
            self._write_json(
                root / "reports" / "build_logs" / "release_candidate_freeze_packet.json",
                {"status": "ok"},
            )
            self._write_json(settings.retrieval_eval_report_path, {"overall": {}})
            self._write_json(settings.answer_eval_report_path, {"overall": {}})
            self._write_json(settings.ragas_eval_report_path, {"overall": {}})
            self._write_json(settings.runtime_report_path, {"app": {}, "runtime": {}, "probes": {}})

            payload = build_data_control_room_payload(root)

        self.assertEqual("missing", payload["product_rehearsal"]["status"])
        self.assertIsNone(payload["product_rehearsal"]["critical_scenario_pass_rate"])
        self.assertIsNone(payload["summary"]["product_gate_pass_rate"])
        self.assertIsNone(payload["release_candidate_freeze"]["product_gate_pass_rate"])

    def test_handler_exposes_data_control_room_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text("ARTIFACTS_DIR=artifacts\n", encoding="utf-8")
            settings = load_settings(root)
            self._write_json(settings.source_manifest_path, {"version": 2, "count": 0, "entries": []})
            self._write_json(
                root / "reports" / "build_logs" / "foundry_runs" / "profiles" / "morning_gate" / "latest.json",
                {"verdict": {"status": "blocked", "release_blocking": True, "summary": {}}},
            )

            class _FakeAnswerer:
                def __init__(self, settings) -> None:
                    self.settings = settings

            captured: dict[str, object] = {}
            handler_cls = _build_handler(
                answerer=_FakeAnswerer(settings),
                store=SessionStore(),
                root_dir=root,
            )
            handler = object.__new__(handler_cls)
            handler._send_json = lambda payload, status=None: captured.update(payload=payload, status=status)

            handler._handle_data_control_room("")

            payload = captured["payload"]
            assert isinstance(payload, dict)
            self.assertIn("summary", payload)
            self.assertIn("gate", payload)
            self.assertIn("grading", payload)
            self.assertIn("gold_books", payload)
            self.assertIn("corpus_book_status", payload)
            self.assertIn("manualbook_status", payload)
            self.assertIn("manual_book_library", payload)
            self.assertIn("playbook_library", payload)
            self.assertIn("policy_overlay_book_status", payload)
            self.assertIn("synthesized_playbook_status", payload)
            self.assertEqual("blocked", payload["summary"]["gate_status"])
            self.assertTrue(payload["gate"]["release_blocking"])

    def test_build_data_control_room_payload_uses_shared_official_runtime_registry(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text("ARTIFACTS_DIR=artifacts\n", encoding="utf-8")
            settings = load_settings(root)

            self._write_json(
                settings.source_manifest_path,
                {
                    "entries": [
                        {
                            "book_slug": "architecture",
                            "title": "Architecture",
                            "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html",
                            "source_url": "https://example.com/architecture",
                            "source_lane": "official_ko",
                            "source_type": "official_doc",
                            "approval_state": "approved",
                            "publication_state": "active",
                            "content_status": "approved_ko",
                        }
                    ]
                },
            )
            self._write_json(
                root / "data" / "wiki_runtime_books" / "active_manifest.json",
                {
                    "generated_at_utc": "2026-04-17T11:00:00+00:00",
                    "active_group": "full_rebuild",
                    "entries": [
                        {
                            "slug": "support",
                            "title": "Support",
                            "source_candidate_path": str(root / "support.md"),
                            "runtime_path": str(root / "runtime" / "support.md"),
                        }
                    ],
                },
            )
            self._write_jsonl(
                settings.playbook_documents_path,
                [
                    {
                        "book_slug": "backup_restore_operations",
                        "title": "Backup Restore Operations",
                        "source_uri": "https://example.com/backup_restore_operations",
                        "review_status": "approved",
                        "section_count": 3,
                        "source_metadata": {
                            "source_type": "operation_playbook",
                            "source_lane": "applied_playbook",
                            "approval_state": "approved",
                            "publication_state": "published",
                        },
                    }
                ],
            )

            payload = build_data_control_room_payload(root)

        self.assertEqual(3, payload["summary"]["approved_wiki_runtime_book_count"])
        self.assertEqual(
            {"architecture", "backup_restore_operations", "support"},
            {book["book_slug"] for book in payload["approved_wiki_runtime_books"]["books"]},
        )
        self.assertEqual(
            {
                "/docs/ocp/4.20/ko/architecture/index.html",
                "/docs/ocp/4.20/ko/backup_restore_operations/index.html",
                "/playbooks/wiki-runtime/active/support/index.html",
            },
            {book["viewer_path"] for book in payload["approved_wiki_runtime_books"]["books"]},
        )
        self.assertEqual(
            {
                "architecture": "Silver",
                "backup_restore_operations": "Bronze",
                "support": "Gold",
            },
            {
                book["book_slug"]: book["grade"]
                for book in payload["approved_wiki_runtime_books"]["books"]
            },
        )
        self.assertEqual(
            {
                "architecture": "latest_pipeline_output",
                "backup_restore_operations": "derived_runtime_output",
                "support": "active_runtime",
            },
            {
                book["book_slug"]: book["review_status"]
                for book in payload["approved_wiki_runtime_books"]["books"]
            },
        )
