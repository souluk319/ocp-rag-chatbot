from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import Settings
from play_book_studio.ingestion.foundry_orchestrator import (
    JOB_RUNNERS,
    _run_source_approval,
    _gold_manual_synthesis_entries,
    build_release_verdict,
    load_foundry_profiles,
    run_foundry_profile,
    run_foundry_profile_with_retry,
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class FoundryOrchestratorTests(unittest.TestCase):
    def test_run_source_approval_does_not_readd_reader_grade_failed_manual_synthesis(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = Settings(root_dir=root)
            source_catalog_entries = [
                {
                    "product_slug": "openshift_container_platform",
                    "ocp_version": "4.20",
                    "docs_language": "ko",
                    "source_kind": "html-single",
                    "book_slug": "monitoring",
                    "title": "Monitoring",
                    "source_url": "https://example.com/monitoring",
                    "resolved_source_url": "https://example.com/monitoring",
                    "resolved_language": "ko",
                    "viewer_path": "/docs/ocp/4.20/ko/monitoring/index.html",
                    "high_value": True,
                    "source_fingerprint": "fp-monitoring",
                }
            ]
            _write_json(
                settings.source_catalog_path,
                {
                    "version": 1,
                    "source": "test",
                    "count": 1,
                    "entries": source_catalog_entries,
                },
            )
            _write_json(
                settings.source_manifest_path,
                {
                    "version": 1,
                    "source": "test",
                    "count": 1,
                    "entries": [
                        {
                            **source_catalog_entries[0],
                            "title": "모니터링 운영 플레이북",
                            "content_status": "approved_ko",
                            "approval_status": "approved",
                            "review_status": "approved",
                            "source_type": "manual_synthesis",
                            "source_lane": "applied_playbook",
                            "translation_stage": "approved_ko",
                        }
                    ],
                },
            )
            settings.normalized_docs_path.write_text("", encoding="utf-8")
            settings.chunks_path.write_text("", encoding="utf-8")
            settings.playbook_documents_path.write_text(
                json.dumps(
                    {
                        "book_slug": "monitoring",
                        "title": "모니터링 운영 플레이북",
                        "translation_status": "approved_ko",
                        "review_status": "approved",
                        "version": "4.20",
                        "locale": "ko",
                        "source_uri": "https://example.com/monitoring",
                        "source_metadata": {
                            "source_type": "manual_synthesis",
                            "source_lane": "applied_playbook",
                        },
                        "anchor_map": {"overview": "/docs/ocp/4.20/ko/monitoring/index.html#overview"},
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            _write_json(
                settings.playbook_books_dir / "monitoring.json",
                {
                    "book_slug": "monitoring",
                    "title": "Monitoring",
                    "translation_status": "approved_ko",
                    "sections": [
                        {
                            "heading": "Overview",
                            "semantic_role": "unknown",
                            "blocks": [],
                        }
                    ],
                },
            )

            payload = _run_source_approval(settings, root / "reports" / "build_logs" / "foundry_runs", "demo")

            self.assertEqual(0, payload["approved_manifest_count"])
            self.assertEqual([], payload["approved_book_slugs"])
            approved_manifest = json.loads(settings.source_manifest_path.read_text(encoding="utf-8"))
            self.assertEqual([], approved_manifest["entries"])

    def test_run_source_approval_materializes_topic_playbooks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = Settings(root_dir=root)
            source_catalog_entries = [
                {
                    "product_slug": "openshift_container_platform",
                    "ocp_version": "4.20",
                    "docs_language": "ko",
                    "source_kind": "html-single",
                    "book_slug": "backup_and_restore",
                    "title": "Backup and restore",
                    "source_url": "https://example.com/backup_and_restore",
                    "resolved_source_url": "https://example.com/backup_and_restore",
                    "resolved_language": "ko",
                    "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html",
                    "high_value": True,
                    "source_fingerprint": "fp-backup",
                }
            ]
            _write_json(
                settings.source_catalog_path,
                {"version": 1, "source": "test", "count": 1, "entries": source_catalog_entries},
            )
            _write_json(
                settings.source_manifest_path,
                {
                    "version": 1,
                    "source": "test",
                    "count": 1,
                    "entries": [
                        {
                            **source_catalog_entries[0],
                            "content_status": "approved_ko",
                            "approval_status": "approved",
                            "review_status": "approved",
                            "citation_eligible": True,
                            "source_type": "manual_synthesis",
                            "source_lane": "applied_playbook",
                            "translation_stage": "approved_ko",
                        }
                    ],
                },
            )
            settings.normalized_docs_path.write_text("", encoding="utf-8")
            settings.chunks_path.write_text("", encoding="utf-8")
            settings.playbook_documents_path.write_text(
                json.dumps(
                    {
                        "book_slug": "backup_and_restore",
                        "title": "Backup and restore",
                        "translation_status": "approved_ko",
                        "review_status": "approved",
                        "version": "4.20",
                        "locale": "ko",
                        "source_uri": "https://example.com/backup_and_restore",
                        "source_metadata": {
                            "source_id": "manual_synthesis:backup_and_restore",
                            "source_type": "manual_synthesis",
                            "source_lane": "applied_playbook",
                        },
                        "anchor_map": {"overview": "/docs/ocp/4.20/ko/backup_and_restore/index.html#overview"},
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
                                "blocks": [{"kind": "paragraph", "text": "백업 개요"}],
                            },
                            {
                                "section_id": "backup_and_restore:backup",
                                "section_key": "backup_and_restore:backup",
                                "ordinal": 2,
                                "heading": "백업 절차",
                                "anchor": "backup-procedure",
                                "semantic_role": "procedure",
                                "path": ["운영", "백업 절차"],
                                "section_path": ["운영", "백업 절차"],
                                "blocks": [{"kind": "code", "code": "cluster-backup.sh /backup"}],
                            },
                        ],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            _write_json(
                settings.playbook_books_dir / "backup_and_restore.json",
                {
                    "book_slug": "backup_and_restore",
                    "title": "Backup and restore",
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
                            "blocks": [{"kind": "paragraph", "text": "백업 개요"}],
                        },
                        {
                            "section_id": "backup_and_restore:backup",
                            "section_key": "backup_and_restore:backup",
                            "ordinal": 2,
                            "heading": "백업 절차",
                            "anchor": "backup-procedure",
                            "semantic_role": "procedure",
                            "path": ["운영", "백업 절차"],
                            "section_path": ["운영", "백업 절차"],
                            "blocks": [{"kind": "code", "code": "cluster-backup.sh /backup"}],
                        },
                    ],
                },
            )

            payload = _run_source_approval(settings, root / "reports" / "build_logs" / "foundry_runs", "demo")

            self.assertEqual(1, payload["topic_playbook_summary"]["generated_count"])
            self.assertIn("backup_restore_control_plane", payload["topic_playbook_summary"]["generated_slugs"])
            self.assertEqual(1, payload["operation_playbook_summary"]["generated_count"])
            self.assertIn("backup_restore_operations", payload["operation_playbook_summary"]["generated_slugs"])
            self.assertEqual(1, payload["policy_overlay_book_summary"]["generated_count"])
            self.assertIn("backup_and_restore_policy_overlay_book", payload["policy_overlay_book_summary"]["generated_slugs"])
            self.assertEqual(1, payload["synthesized_playbook_summary"]["generated_count"])
            self.assertIn("backup_and_restore_synthesized_playbook", payload["synthesized_playbook_summary"]["generated_slugs"])
            self.assertEqual(1, payload["troubleshooting_playbook_summary"]["generated_count"])
            self.assertIn(
                "backup_restore_recovery_troubleshooting",
                payload["troubleshooting_playbook_summary"]["generated_slugs"],
            )
            self.assertEqual(5, payload["derived_playbook_count"])
            self.assertEqual(
                "materialized",
                payload["derived_family_statuses"]["operation_playbook"]["status"],
            )
            self.assertEqual(
                "materialized",
                payload["derived_family_statuses"]["policy_overlay_book"]["status"],
            )
            self.assertEqual(
                "materialized",
                payload["derived_family_statuses"]["synthesized_playbook"]["status"],
            )
            self.assertTrue((settings.playbook_books_dir / "backup_restore_control_plane.json").exists())
            self.assertTrue((settings.playbook_books_dir / "backup_restore_operations.json").exists())
            self.assertTrue((settings.playbook_books_dir / "backup_and_restore_policy_overlay_book.json").exists())
            self.assertTrue((settings.playbook_books_dir / "backup_and_restore_synthesized_playbook.json").exists())
            self.assertTrue(
                (settings.playbook_books_dir / "backup_restore_recovery_troubleshooting.json").exists()
            )

    def test_load_foundry_profiles_reads_hourly_and_daily_routines(self) -> None:
        profiles = load_foundry_profiles(Settings(root_dir=ROOT))

        self.assertIn("runtime_smoke_hourly", profiles)
        self.assertIn("morning_gate", profiles)
        self.assertEqual("hourly", profiles["runtime_smoke_hourly"].cadence)
        self.assertEqual(15, profiles["runtime_smoke_hourly"].minute)
        self.assertEqual(1, profiles["runtime_smoke_hourly"].interval_hours)
        self.assertEqual("08:30", profiles["morning_gate"].time)

    def test_build_release_verdict_marks_needs_promotion_for_remaining_queues(self) -> None:
        verdict = build_release_verdict(
            [
                {
                    "job_id": "source_approval",
                    "status": "ok",
                    "payload": {"summary": {"high_value_issue_count": 1}},
                },
                {
                    "job_id": "source_bundle_quality",
                    "status": "ok",
                    "payload": {"counts": {"source_expansion_needed": 0}},
                },
                {
                    "job_id": "synthesis_lane",
                    "status": "ok",
                    "payload": {"summary": {"approved_runtime_count": 28, "translation_ready_count": 1, "manual_review_ready_count": 0}},
                },
                {
                    "job_id": "validation_gate",
                    "status": "ok",
                    "payload": {
                        "checks": {
                            "raw_html_covers_expected_subset": True,
                            "artifact_books_match_expected_subset": True,
                            "chunks_have_unique_ids": True,
                            "bm25_matches_chunks": True,
                            "qdrant_matches_chunks_by_count": True,
                            "qdrant_matches_chunks_by_ids": True,
                            "qdrant_books_match_chunks": True,
                            "required_keys_present": True,
                            "manifest_metadata_complete": True,
                            "normalized_metadata_complete": True,
                            "chunk_metadata_complete": True,
                            "playbook_metadata_complete": True,
                            "parsed_lineage_complete": True,
                            "security_boundary_complete": True,
                            "no_empty_chunk_texts": True,
                            "no_legal_notice_chunks": True,
                        }
                    },
                },
            ]
        )

        self.assertEqual("needs_promotion", verdict["status"])
        self.assertTrue(verdict["release_blocking"])
        self.assertIn("translation_ready_remaining", verdict["reasons"])

    def test_build_release_verdict_marks_blocked_for_validation_or_runtime_failures(self) -> None:
        verdict = build_release_verdict(
            [
                {
                    "job_id": "source_approval",
                    "status": "ok",
                    "payload": {"summary": {"high_value_issue_count": 0}},
                },
                {
                    "job_id": "source_bundle_quality",
                    "status": "ok",
                    "payload": {"counts": {"source_expansion_needed": 0}},
                },
                {
                    "job_id": "synthesis_lane",
                    "status": "ok",
                    "payload": {"summary": {"approved_runtime_count": 29, "translation_ready_count": 0, "manual_review_ready_count": 0}},
                },
                {
                    "job_id": "validation_gate",
                    "status": "ok",
                    "payload": {
                        "checks": {
                            "raw_html_covers_expected_subset": False,
                            "artifact_books_match_expected_subset": False,
                            "chunks_have_unique_ids": True,
                            "bm25_matches_chunks": True,
                            "qdrant_matches_chunks_by_count": True,
                            "qdrant_matches_chunks_by_ids": True,
                            "qdrant_books_match_chunks": True,
                            "required_keys_present": True,
                            "manifest_metadata_complete": True,
                            "normalized_metadata_complete": True,
                            "chunk_metadata_complete": True,
                            "playbook_metadata_complete": True,
                            "parsed_lineage_complete": True,
                            "security_boundary_complete": True,
                            "no_empty_chunk_texts": True,
                            "no_legal_notice_chunks": True,
                        }
                    },
                },
                {
                    "job_id": "runtime_smoke",
                    "status": "ok",
                    "payload": {
                        "probes": {
                            "local_ui": {"health_status": 500},
                            "llm": {"models_status": 200},
                            "embedding": {"models_status": 200},
                            "qdrant": {"collection_present": True},
                        }
                    },
                },
            ]
        )

        self.assertEqual("blocked", verdict["status"])
        self.assertTrue(verdict["release_blocking"])
        self.assertTrue(any(reason.startswith("validation_failed") for reason in verdict["reasons"]))
        self.assertTrue(any(reason.startswith("runtime_smoke_failed") for reason in verdict["reasons"]))

    def test_build_release_verdict_blocks_when_parsed_or_security_checks_fail(self) -> None:
        verdict = build_release_verdict(
            [
                {
                    "job_id": "source_approval",
                    "status": "ok",
                    "payload": {"summary": {"high_value_issue_count": 0}},
                },
                {
                    "job_id": "source_bundle_quality",
                    "status": "ok",
                    "payload": {"counts": {"source_expansion_needed": 0}},
                },
                {
                    "job_id": "synthesis_lane",
                    "status": "ok",
                    "payload": {"summary": {"approved_runtime_count": 29, "translation_ready_count": 0, "manual_review_ready_count": 0}},
                },
                {
                    "job_id": "validation_gate",
                    "status": "ok",
                    "payload": {
                        "checks": {
                            "raw_html_covers_expected_subset": True,
                            "artifact_books_match_expected_subset": True,
                            "chunks_have_unique_ids": True,
                            "bm25_matches_chunks": True,
                            "qdrant_matches_chunks_by_count": True,
                            "qdrant_matches_chunks_by_ids": True,
                            "qdrant_books_match_chunks": True,
                            "required_keys_present": True,
                            "manifest_metadata_complete": True,
                            "normalized_metadata_complete": True,
                            "chunk_metadata_complete": True,
                            "playbook_metadata_complete": True,
                            "parsed_lineage_complete": False,
                            "security_boundary_complete": False,
                            "no_empty_chunk_texts": True,
                            "no_legal_notice_chunks": True,
                        }
                    },
                },
                {
                    "job_id": "runtime_smoke",
                    "status": "ok",
                    "payload": {
                        "probes": {
                            "local_ui": {"health_status": 200},
                            "llm": {"models_status": 200},
                            "embedding": {"models_status": 200},
                            "qdrant": {"collection_present": True},
                        }
                    },
                },
            ]
        )

        self.assertEqual("blocked", verdict["status"])
        self.assertTrue(verdict["release_blocking"])
        self.assertIn(
            "validation_failed:parsed_lineage_complete,security_boundary_complete",
            verdict["reasons"],
        )

    def test_run_foundry_profile_writes_job_reports_and_latest_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_json(
                root / "pipelines" / "foundry_routines.json",
                {
                    "timezone": "Asia/Seoul",
                    "jobs": {
                        "source_approval": {
                            "name": "Source Approval",
                            "stage": "approval",
                            "stop_on_failure": True,
                        },
                        "validation_gate": {
                            "name": "Validation Gate",
                            "stage": "judge",
                            "stop_on_failure": True,
                        },
                    },
                    "profiles": [
                        {
                            "id": "demo",
                            "name": "Demo",
                            "description": "demo profile",
                            "schedule": {
                                "cadence": "daily",
                                "days": ["Mon"],
                                "time": "09:00",
                            },
                            "jobs": ["source_approval", "validation_gate"],
                        }
                    ],
                },
            )
            settings = Settings(root_dir=root)

            fake_runners = {
                "source_approval": lambda _settings, _report_dir, _profile_id: {
                    "summary": {"high_value_issue_count": 0}
                },
                "validation_gate": lambda _settings, _report_dir, _profile_id: {
                    "checks": {
                        "raw_html_covers_expected_subset": True,
                        "artifact_books_match_expected_subset": True,
                        "chunks_have_unique_ids": True,
                        "bm25_matches_chunks": True,
                        "qdrant_matches_chunks_by_count": True,
                            "qdrant_matches_chunks_by_ids": True,
                            "qdrant_books_match_chunks": True,
                            "required_keys_present": True,
                            "manifest_metadata_complete": True,
                            "normalized_metadata_complete": True,
                            "chunk_metadata_complete": True,
                            "playbook_metadata_complete": True,
                            "parsed_lineage_complete": True,
                            "security_boundary_complete": True,
                            "no_empty_chunk_texts": True,
                            "no_legal_notice_chunks": True,
                        }
                },
            }
            with patch.dict(JOB_RUNNERS, fake_runners, clear=True):
                report = run_foundry_profile(settings, "demo")

            self.assertEqual("release_ready", report["verdict"]["status"])
            self.assertTrue(Path(report["report_path"]).exists())
            self.assertTrue((root / "reports" / "build_logs" / "foundry_runs" / "source_approval" / "latest.json").exists())
            self.assertTrue((root / "reports" / "build_logs" / "foundry_runs" / "validation_gate" / "latest.json").exists())

    def test_run_foundry_profile_includes_delta_against_previous_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_json(
                root / "pipelines" / "foundry_routines.json",
                {
                    "timezone": "Asia/Seoul",
                    "jobs": {
                        "source_approval": {"name": "Source Approval", "stage": "approval", "stop_on_failure": True},
                        "source_bundle_quality": {"name": "Source Bundle Quality", "stage": "bronze_quality", "stop_on_failure": True},
                        "synthesis_lane": {"name": "Synthesis Lane", "stage": "planning", "stop_on_failure": True},
                        "validation_gate": {"name": "Validation Gate", "stage": "judge", "stop_on_failure": True},
                    },
                    "profiles": [
                        {
                            "id": "demo",
                            "name": "Demo",
                            "description": "demo profile",
                            "schedule": {"cadence": "daily", "days": ["Mon"], "time": "09:00"},
                            "jobs": ["source_approval", "source_bundle_quality", "synthesis_lane", "validation_gate"],
                        }
                    ],
                },
            )
            settings = Settings(root_dir=root)
            state = {"run": 0}

            def fake_source_approval(_settings, _report_dir, _profile_id):
                if state["run"] == 0:
                    return {
                        "summary": {"high_value_issue_count": 1},
                        "approved_book_slugs": ["overview", "architecture"],
                    }
                return {
                    "summary": {"high_value_issue_count": 0},
                    "approved_book_slugs": ["overview", "architecture", "etcd"],
                }

            def fake_source_bundle_quality(_settings, _report_dir, _profile_id):
                return {"counts": {"source_expansion_needed": 0}}

            def fake_synthesis_lane(_settings, _report_dir, _profile_id):
                if state["run"] == 0:
                    return {
                        "summary": {
                            "approved_runtime_count": 28,
                            "translation_ready_count": 1,
                            "manual_review_ready_count": 0,
                        },
                        "translation_ready": [{"book_slug": "etcd"}],
                        "manual_review_ready": [],
                    }
                return {
                    "summary": {
                        "approved_runtime_count": 29,
                        "translation_ready_count": 0,
                        "manual_review_ready_count": 0,
                    },
                    "translation_ready": [],
                    "manual_review_ready": [],
                }

            def fake_validation_gate(_settings, _report_dir, _profile_id):
                return {
                    "checks": {
                        "raw_html_covers_expected_subset": True,
                        "artifact_books_match_expected_subset": True,
                        "chunks_have_unique_ids": True,
                        "bm25_matches_chunks": True,
                        "qdrant_matches_chunks_by_count": True,
                        "qdrant_matches_chunks_by_ids": True,
                        "qdrant_books_match_chunks": True,
                        "required_keys_present": True,
                        "manifest_metadata_complete": True,
                        "normalized_metadata_complete": True,
                        "chunk_metadata_complete": True,
                        "playbook_metadata_complete": True,
                        "parsed_lineage_complete": True,
                        "security_boundary_complete": True,
                        "no_empty_chunk_texts": True,
                        "no_legal_notice_chunks": True,
                    }
                }

            with patch.dict(
                JOB_RUNNERS,
                {
                    "source_approval": fake_source_approval,
                    "source_bundle_quality": fake_source_bundle_quality,
                    "synthesis_lane": fake_synthesis_lane,
                    "validation_gate": fake_validation_gate,
                },
                clear=True,
            ):
                first_report = run_foundry_profile(settings, "demo")
                self.assertFalse(first_report["delta"]["has_previous_run"])
                state["run"] = 1
                second_report = run_foundry_profile(settings, "demo")

            self.assertTrue(second_report["delta"]["has_previous_run"])
            self.assertEqual("needs_promotion", second_report["delta"]["verdict_change"]["before"])
            self.assertEqual("release_ready", second_report["delta"]["verdict_change"]["after"])
            self.assertEqual(["etcd"], second_report["delta"]["promoted_books"])
            self.assertEqual(
                1,
                second_report["delta"]["summary_deltas"]["approved_runtime_count"]["delta"],
            )
            self.assertEqual(
                -1,
                second_report["delta"]["summary_deltas"]["translation_ready_count"]["delta"],
            )
            self.assertTrue(Path(second_report["delta_report_path"]).exists())
            self.assertTrue(Path(second_report["profile_report_path"]).exists())
            self.assertTrue(
                (root / "reports" / "build_logs" / "foundry_runs" / "profiles" / "demo" / "latest.json").exists()
            )
            self.assertTrue(
                (root / "reports" / "build_logs" / "foundry_runs" / "deltas" / "demo" / "latest.json").exists()
            )

    def test_run_foundry_profile_with_retry_retries_runtime_probe_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_json(
                root / "pipelines" / "foundry_routines.json",
                {
                    "timezone": "Asia/Seoul",
                    "jobs": {
                        "source_approval": {"name": "Source Approval", "stage": "approval", "stop_on_failure": True},
                        "source_bundle_quality": {"name": "Source Bundle Quality", "stage": "bronze_quality", "stop_on_failure": True},
                        "synthesis_lane": {"name": "Synthesis Lane", "stage": "planning", "stop_on_failure": True},
                        "validation_gate": {"name": "Validation Gate", "stage": "judge", "stop_on_failure": True},
                        "runtime_smoke": {"name": "Runtime Smoke", "stage": "runtime", "stop_on_failure": True},
                    },
                    "profiles": [
                        {
                            "id": "demo",
                            "name": "Demo",
                            "description": "demo profile",
                            "schedule": {"cadence": "daily", "days": ["Mon"], "time": "09:00"},
                            "jobs": [
                                "source_approval",
                                "source_bundle_quality",
                                "synthesis_lane",
                                "validation_gate",
                                "runtime_smoke",
                            ],
                        }
                    ],
                },
            )
            settings = Settings(root_dir=root)
            runtime_attempts = {"count": 0}

            def fake_source_approval(_settings, _report_dir, _profile_id):
                return {
                    "summary": {"high_value_issue_count": 0},
                    "approved_book_slugs": ["overview"],
                }

            def fake_source_bundle_quality(_settings, _report_dir, _profile_id):
                return {"counts": {"source_expansion_needed": 0}}

            def fake_synthesis_lane(_settings, _report_dir, _profile_id):
                return {
                    "summary": {
                        "approved_runtime_count": 29,
                        "translation_ready_count": 0,
                        "manual_review_ready_count": 0,
                    },
                    "translation_ready": [],
                    "manual_review_ready": [],
                }

            def fake_validation_gate(_settings, _report_dir, _profile_id):
                return {
                    "checks": {
                        "raw_html_covers_expected_subset": True,
                        "artifact_books_match_expected_subset": True,
                        "chunks_have_unique_ids": True,
                        "bm25_matches_chunks": True,
                        "qdrant_matches_chunks_by_count": True,
                        "qdrant_matches_chunks_by_ids": True,
                        "qdrant_books_match_chunks": True,
                        "required_keys_present": True,
                        "manifest_metadata_complete": True,
                        "normalized_metadata_complete": True,
                        "chunk_metadata_complete": True,
                        "playbook_metadata_complete": True,
                        "parsed_lineage_complete": True,
                        "security_boundary_complete": True,
                        "no_empty_chunk_texts": True,
                        "no_legal_notice_chunks": True,
                    }
                }

            def fake_runtime_smoke(_settings, _report_dir, _profile_id):
                runtime_attempts["count"] += 1
                if runtime_attempts["count"] == 1:
                    return {
                        "probes": {
                            "local_ui": {"health_status": 500},
                            "llm": {"models_status": 200},
                            "embedding": {"models_status": 200},
                            "qdrant": {"collection_present": True},
                        }
                    }
                return {
                    "probes": {
                        "local_ui": {"health_status": 200},
                        "llm": {"models_status": 200},
                        "embedding": {"models_status": 200},
                        "qdrant": {"collection_present": True},
                    }
                }

            with patch.dict(
                JOB_RUNNERS,
                {
                    "source_approval": fake_source_approval,
                    "source_bundle_quality": fake_source_bundle_quality,
                    "synthesis_lane": fake_synthesis_lane,
                    "validation_gate": fake_validation_gate,
                    "runtime_smoke": fake_runtime_smoke,
                },
                clear=True,
            ):
                report = run_foundry_profile_with_retry(
                    settings,
                    "demo",
                    retries=1,
                    retry_delay_seconds=0,
                    sleep_fn=lambda _seconds: None,
                )

            self.assertEqual("release_ready", report["verdict"]["status"])
            self.assertEqual(2, runtime_attempts["count"])
            self.assertEqual(2, report["retry"]["attempt_count"])

    def test_gold_manual_synthesis_entries_restore_approved_curated_books(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            settings.playbook_documents_path.parent.mkdir(parents=True, exist_ok=True)
            row = {
                "book_slug": "etcd",
                "title": "etcd 백업 및 복구 플레이북",
                "version": "4.20",
                "locale": "ko",
                "source_uri": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/etcd/index",
                "translation_status": "approved_ko",
                "translation_stage": "approved_ko",
                "translation_source_uri": "https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html-single/etcd/index",
                "translation_source_language": "en",
                "translation_source_fingerprint": "fingerprint-etcd",
                "review_status": "approved",
                "anchor_map": {
                    "etcd-operations-overview": "/docs/ocp/4.20/ko/etcd/index.html#etcd-operations-overview"
                },
                "source_metadata": {
                    "source_type": "manual_synthesis",
                    "source_lane": "applied_playbook",
                    "source_collection": "core",
                    "original_title": "Backing up and restoring etcd data / Disaster recovery",
                    "trust_score": 0.98,
                },
            }
            settings.playbook_documents_path.write_text(
                json.dumps(row, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            entries = _gold_manual_synthesis_entries(settings)

            self.assertEqual(1, len(entries))
            self.assertEqual("etcd", entries[0].book_slug)
            self.assertEqual("manual_synthesis", entries[0].source_type)
            self.assertEqual("approved", entries[0].approval_status)
            self.assertEqual("/docs/ocp/4.20/ko/etcd/index.html", entries[0].viewer_path)

    def test_approved_runtime_rebuild_runs_full_ingestion_against_active_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            fake_log = SimpleNamespace(
                to_dict=lambda: {
                    "stage": "done",
                    "normalized_count": 23,
                    "chunk_count": 100,
                    "qdrant_upserted_count": 100,
                }
            )

            with patch(
                "play_book_studio.ingestion.foundry_orchestrator.run_ingestion_pipeline",
                return_value=fake_log,
            ) as mocked_run:
                payload = JOB_RUNNERS["approved_runtime_rebuild"](
                    settings,
                    settings.root_dir / "reports",
                    "demo",
                )

            mocked_run.assert_called_once_with(
                settings,
                refresh_manifest=False,
                collect_subset="all",
                process_subset="all",
                skip_embeddings=False,
                skip_qdrant=False,
            )
            self.assertEqual("done", payload["stage"])
            self.assertEqual(str(settings.playbook_books_dir), payload["output_targets"]["playbook_books_dir"])
            self.assertEqual(settings.qdrant_collection, payload["output_targets"]["qdrant_collection"])


if __name__ == "__main__":
    unittest.main()
