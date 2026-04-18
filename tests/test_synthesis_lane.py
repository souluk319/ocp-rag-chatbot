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
from play_book_studio.ingestion.manifest import write_manifest, read_manifest
from play_book_studio.ingestion.models import SourceManifestEntry
from play_book_studio.ingestion.synthesis_lane import write_synthesis_lane_outputs


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class SynthesisLaneTests(unittest.TestCase):
    def test_write_synthesis_lane_outputs_promotes_translation_and_builds_working_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            catalog_entries = [
                SourceManifestEntry(
                    book_slug="architecture",
                    title="아키텍처",
                    source_url="https://example.com/architecture",
                    resolved_source_url="https://example.com/architecture",
                    viewer_path="/docs/ocp/4.20/ko/architecture/index.html",
                    high_value=True,
                    content_status="approved_ko",
                    citation_eligible=True,
                    approval_status="approved",
                ),
                SourceManifestEntry(
                    book_slug="backup_and_restore",
                    title="Backup and restore",
                    source_url="https://example.com/ko/backup_and_restore",
                    resolved_source_url="https://example.com/ko/backup_and_restore",
                    viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html",
                    high_value=True,
                    content_status="blocked",
                    approval_status="needs_review",
                ),
                SourceManifestEntry(
                    book_slug="operators",
                    title="Operators",
                    source_url="https://example.com/ko/operators",
                    resolved_source_url="https://example.com/ko/operators",
                    viewer_path="/docs/ocp/4.20/ko/operators/index.html",
                    high_value=True,
                    content_status="blocked",
                    approval_status="needs_review",
                ),
            ]
            write_manifest(settings.source_catalog_path, catalog_entries)
            write_manifest(settings.source_manifest_path, [catalog_entries[0]])

            backup_bundle = settings.bronze_dir / "source_bundles" / "backup_and_restore"
            _write_json(
                backup_bundle / "bundle_manifest.json",
                {
                    "official_docs": {
                        "ko": {"contains_language_fallback_banner": True},
                        "en": {"artifact_path": "en/source.html", "content_length": 200},
                    },
                    "repo_artifacts": [{"repo_path": "backup_and_restore/index.adoc"}],
                },
            )
            _write_json(
                backup_bundle / "dossier.json",
                {
                    "current_status": {"content_status": "blocked", "gap_lane": "translation_first"},
                    "official_docs": {
                        "en": {"url": "https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html-single/backup_and_restore/index"}
                    },
                },
            )
            _write_json(
                backup_bundle / "issue_pr_candidates.json",
                {"exact_slug": [], "related_terms": []},
            )

            operators_bundle = settings.bronze_dir / "source_bundles" / "operators"
            _write_json(
                operators_bundle / "bundle_manifest.json",
                {
                    "official_docs": {
                        "ko": {"contains_language_fallback_banner": False},
                        "en": {},
                    },
                    "repo_artifacts": [{"repo_path": "operators/index.adoc"}],
                },
            )
            _write_json(
                operators_bundle / "dossier.json",
                {"current_status": {"content_status": "blocked", "gap_lane": "manual_review_first"}},
            )
            _write_json(
                operators_bundle / "issue_pr_candidates.json",
                {"exact_slug": [], "related_terms": []},
            )

            report_path = settings.root_dir / "reports" / "build_logs" / "synthesis_lane_report.json"
            report = write_synthesis_lane_outputs(settings)

            self.assertEqual(1, report["summary"]["translation_ready_count"])
            self.assertEqual(1, report["summary"]["manual_review_ready_count"])
            self.assertEqual(2, report["summary"]["corpus_working_count"])

            translated_entries = read_manifest(settings.translation_draft_manifest_path)
            self.assertEqual(["backup_and_restore"], [entry.book_slug for entry in translated_entries])
            self.assertEqual("translated_ko_draft", translated_entries[0].content_status)
            self.assertEqual("https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html-single/backup_and_restore/index", translated_entries[0].translation_source_url)
            self.assertEqual("official_en_fallback", translated_entries[0].source_lane)

            working_entries = read_manifest(settings.corpus_working_manifest_path)
            self.assertEqual(["architecture", "backup_and_restore"], [entry.book_slug for entry in working_entries])

            written_report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(["operators"], [item["book_slug"] for item in written_report["manual_review_ready"]])
            self.assertEqual(3, written_report["buyer_scope"]["raw_manual_count"])
            self.assertEqual(1, written_report["buyer_scope"]["approved_manual_book_count"])
            self.assertEqual(0, written_report["buyer_scope"]["playable_book_count"])
            self.assertEqual(2, written_report["buyer_scope"]["promotion_queue_count"])
            self.assertEqual("buyer_playable_review", written_report["buyer_scope"]["queue_scope"])
            self.assertEqual(1, written_report["buyer_scope"]["translation_ready_count"])
            self.assertEqual(1, written_report["buyer_scope"]["manual_review_ready_count"])
            self.assertIn("2 books remain in the buyer-visible review queue", written_report["buyer_scope"]["scope_verdict"])
            self.assertEqual("needs_queue_visibility", written_report["buyer_scope"]["pack_scope_status"])
            self.assertEqual(
                {
                    "operation_playbook": 0,
                    "policy_overlay_book": 0,
                    "synthesized_playbook": 0,
                    "topic_playbook": 0,
                    "troubleshooting_playbook": 0,
                },
                written_report["buyer_scope"]["derived_family_counts"],
            )
            self.assertEqual(0, written_report["buyer_scope"]["approved_manifest_derived_playbook_count"])
            self.assertEqual(0, written_report["buyer_scope"]["materialized_derived_playbook_count"])
            self.assertEqual(
                written_report["buyer_scope"]["approved_manifest_derived_family_counts"],
                written_report["approved_manifest_derived_family_counts"],
            )
            self.assertEqual(
                written_report["buyer_scope"]["materialized_derived_family_counts"],
                written_report["materialized_derived_family_counts"],
            )
            self.assertEqual(written_report["buyer_scope"]["derived_family_counts"], written_report["derived_family_counts"])
            self.assertEqual(0, written_report["summary"]["derived_playbook_count"])
            self.assertEqual(0, written_report["summary"]["approved_manifest_derived_playbook_count"])
            self.assertEqual(0, written_report["summary"]["materialized_derived_playbook_count"])
            self.assertEqual(0, written_report["summary"]["topic_playbook_count"])
            self.assertEqual(0, written_report["summary"]["operation_playbook_count"])
            self.assertEqual(0, written_report["summary"]["troubleshooting_playbook_count"])
            self.assertEqual(0, written_report["summary"]["policy_overlay_book_count"])
            self.assertEqual(0, written_report["summary"]["synthesized_playbook_count"])

    def test_write_synthesis_lane_outputs_surfaces_materialized_topic_playbooks_in_buyer_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            catalog_entries = [
                SourceManifestEntry(
                    book_slug="backup_and_restore",
                    title="Backup and restore",
                    source_url="https://example.com/backup_and_restore",
                    resolved_source_url="https://example.com/backup_and_restore",
                    viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html",
                    high_value=True,
                    content_status="approved_ko",
                    approval_status="approved",
                    citation_eligible=True,
                    source_type="manual_synthesis",
                    source_lane="applied_playbook",
                ),
            ]
            write_manifest(settings.source_catalog_path, catalog_entries)
            write_manifest(settings.source_manifest_path, catalog_entries)
            settings.playbook_documents_path.parent.mkdir(parents=True, exist_ok=True)
            settings.playbook_documents_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "book_slug": "backup_restore_control_plane",
                                "title": "컨트롤 플레인 백업/복구 플레이북",
                                "translation_status": "approved_ko",
                                "review_status": "approved",
                                "source_metadata": {
                                    "source_type": "topic_playbook",
                                    "source_lane": "applied_playbook",
                                },
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "book_slug": "backup_restore_operations",
                                "title": "컨트롤 플레인 백업 운영 플레이북",
                                "translation_status": "approved_ko",
                                "review_status": "approved",
                                "source_metadata": {
                                    "source_type": "operation_playbook",
                                    "source_lane": "applied_playbook",
                                },
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "book_slug": "backup_restore_recovery_troubleshooting",
                                "title": "컨트롤 플레인 복구 트러블슈팅 플레이북",
                                "translation_status": "approved_ko",
                                "review_status": "approved",
                                "source_metadata": {
                                    "source_type": "troubleshooting_playbook",
                                    "source_lane": "applied_playbook",
                                },
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "book_slug": "backup_restore_policy_overlay",
                                "title": "컨트롤 플레인 정책 오버레이 북",
                                "translation_status": "approved_ko",
                                "review_status": "approved",
                                "source_metadata": {
                                    "source_type": "policy_overlay_book",
                                    "source_lane": "applied_playbook",
                                },
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "book_slug": "backup_restore_synthesized_playbook",
                                "title": "컨트롤 플레인 합성 플레이북",
                                "translation_status": "approved_ko",
                                "review_status": "approved",
                                "source_metadata": {
                                    "source_type": "synthesized_playbook",
                                    "source_lane": "applied_playbook",
                                },
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            settings.playbook_books_dir.mkdir(parents=True, exist_ok=True)
            (settings.playbook_books_dir / "backup_restore_control_plane.json").write_text(
                json.dumps(
                    {
                        "book_slug": "backup_restore_control_plane",
                        "title": "컨트롤 플레인 백업/복구 플레이북",
                        "source_metadata": {"source_type": "topic_playbook"},
                        "sections": [],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (settings.playbook_books_dir / "backup_restore_operations.json").write_text(
                json.dumps(
                    {
                        "book_slug": "backup_restore_operations",
                        "title": "컨트롤 플레인 백업 운영 플레이북",
                        "source_metadata": {"source_type": "operation_playbook"},
                        "sections": [],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (settings.playbook_books_dir / "backup_restore_recovery_troubleshooting.json").write_text(
                json.dumps(
                    {
                        "book_slug": "backup_restore_recovery_troubleshooting",
                        "title": "컨트롤 플레인 복구 트러블슈팅 플레이북",
                        "source_metadata": {"source_type": "troubleshooting_playbook"},
                        "sections": [],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (settings.playbook_books_dir / "backup_restore_policy_overlay.json").write_text(
                json.dumps(
                    {
                        "book_slug": "backup_restore_policy_overlay",
                        "title": "컨트롤 플레인 정책 오버레이 북",
                        "source_metadata": {"source_type": "policy_overlay_book"},
                        "sections": [],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (settings.playbook_books_dir / "backup_restore_synthesized_playbook.json").write_text(
                json.dumps(
                    {
                        "book_slug": "backup_restore_synthesized_playbook",
                        "title": "컨트롤 플레인 합성 플레이북",
                        "source_metadata": {"source_type": "synthesized_playbook"},
                        "sections": [],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            report = write_synthesis_lane_outputs(settings)

            self.assertEqual(6, report["buyer_scope"]["playable_book_count"])
            self.assertEqual(6, report["buyer_scope"]["playable_asset_count"])
            self.assertEqual(0, report["buyer_scope"]["approved_manifest_derived_playbook_count"])
            self.assertEqual(5, report["buyer_scope"]["materialized_derived_playbook_count"])
            self.assertEqual(1, report["buyer_scope"]["topic_playbook_count"])
            self.assertEqual(1, report["buyer_scope"]["operation_playbook_count"])
            self.assertEqual(1, report["buyer_scope"]["troubleshooting_playbook_count"])
            self.assertEqual(1, report["buyer_scope"]["policy_overlay_book_count"])
            self.assertEqual(1, report["buyer_scope"]["synthesized_playbook_count"])
            self.assertEqual(5, report["buyer_scope"]["derived_playbook_count"])
            self.assertEqual(
                {
                    "operation_playbook": 1,
                    "policy_overlay_book": 1,
                    "synthesized_playbook": 1,
                    "topic_playbook": 1,
                    "troubleshooting_playbook": 1,
                },
                report["buyer_scope"]["derived_family_counts"],
            )
            self.assertEqual(
                ["backup_restore_control_plane"],
                report["buyer_scope"]["topic_playbook_slugs"],
            )
            self.assertEqual(
                ["backup_restore_operations"],
                report["buyer_scope"]["operation_playbook_slugs"],
            )
            self.assertEqual(
                ["backup_restore_recovery_troubleshooting"],
                report["buyer_scope"]["troubleshooting_playbook_slugs"],
            )
            self.assertEqual(
                ["backup_restore_policy_overlay"],
                report["buyer_scope"]["policy_overlay_book_slugs"],
            )
            self.assertEqual(
                ["backup_restore_synthesized_playbook"],
                report["buyer_scope"]["synthesized_playbook_slugs"],
            )
            self.assertEqual(
                "materialized",
                report["buyer_scope"]["derived_family_statuses"]["troubleshooting_playbook"]["status"],
            )
            self.assertEqual(
                report["buyer_scope"]["approved_manifest_derived_family_counts"],
                report["approved_manifest_derived_family_counts"],
            )
            self.assertEqual(
                report["buyer_scope"]["materialized_derived_family_counts"],
                report["materialized_derived_family_counts"],
            )
            self.assertEqual(report["buyer_scope"]["derived_family_counts"], report["derived_family_counts"])
            self.assertEqual(5, report["summary"]["derived_playbook_count"])
            self.assertEqual(0, report["summary"]["approved_manifest_derived_playbook_count"])
            self.assertEqual(5, report["summary"]["materialized_derived_playbook_count"])
            self.assertEqual(1, report["summary"]["topic_playbook_count"])
            self.assertEqual(1, report["summary"]["operation_playbook_count"])
            self.assertEqual(1, report["summary"]["troubleshooting_playbook_count"])
            self.assertEqual(1, report["summary"]["policy_overlay_book_count"])
            self.assertEqual(1, report["summary"]["synthesized_playbook_count"])
            self.assertIn(
                "approved manifest derived 0",
                report["buyer_scope"]["scope_verdict"],
            )
            self.assertIn(
                "materialized derived 5 (operation_playbook 1, policy_overlay_book 1, synthesized_playbook 1, topic_playbook 1, troubleshooting_playbook 1)",
                report["buyer_scope"]["scope_verdict"],
            )

    def test_write_synthesis_lane_outputs_requeues_manual_review_books_even_if_previously_approved(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            catalog_entries = [
                SourceManifestEntry(
                    book_slug="etcd",
                    title="etcd 백업 및 복구 플레이북",
                    source_url="https://example.com/etcd",
                    resolved_source_url="https://example.com/etcd",
                    viewer_path="/docs/ocp/4.20/ko/etcd/index.html",
                    high_value=True,
                    content_status="approved_ko",
                    approval_status="approved",
                    citation_eligible=True,
                    source_type="manual_synthesis",
                    source_lane="applied_playbook",
                ),
                SourceManifestEntry(
                    book_slug="operators",
                    title="Operators",
                    source_url="https://example.com/operators",
                    resolved_source_url="https://example.com/operators",
                    viewer_path="/docs/ocp/4.20/ko/operators/index.html",
                    high_value=True,
                    content_status="blocked",
                    approval_status="needs_review",
                ),
            ]
            write_manifest(settings.source_catalog_path, catalog_entries)
            write_manifest(settings.source_manifest_path, [catalog_entries[0]])

            for slug in ("etcd", "operators"):
                bundle = settings.bronze_dir / "source_bundles" / slug
                _write_json(
                    bundle / "bundle_manifest.json",
                    {
                        "official_docs": {
                            "ko": {"contains_language_fallback_banner": False},
                            "en": {},
                        },
                        "repo_artifacts": [{"repo_path": f"{slug}/index.adoc"}],
                    },
                )
                _write_json(
                    bundle / "issue_pr_candidates.json",
                    {"exact_slug": [], "related_terms": []},
                )

            _write_json(
                settings.bronze_dir / "source_bundles" / "etcd" / "dossier.json",
                {"current_status": {"content_status": "blocked", "gap_lane": "manual_review_first"}},
            )
            _write_json(
                settings.bronze_dir / "source_bundles" / "operators" / "dossier.json",
                {"current_status": {"content_status": "blocked", "gap_lane": "manual_review_first"}},
            )

            report_path = settings.root_dir / "reports" / "build_logs" / "synthesis_lane_report.json"
            report = write_synthesis_lane_outputs(settings)

            self.assertEqual(0, report["summary"]["approved_runtime_count"])
            self.assertEqual(2, report["summary"]["manual_review_ready_count"])
            self.assertEqual(
                ["etcd", "operators"],
                [item["book_slug"] for item in report["manual_review_ready"]],
            )

    def test_write_synthesis_lane_outputs_removes_stale_promoted_books_from_approved_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            catalog_entries = [
                SourceManifestEntry(
                    book_slug="machine_configuration",
                    title="Machine configuration",
                    source_url="https://example.com/machine_configuration",
                    resolved_source_url="https://example.com/machine_configuration",
                    viewer_path="/docs/ocp/4.20/ko/machine_configuration/index.html",
                    high_value=True,
                    content_status="blocked",
                    approval_status="needs_review",
                ),
                SourceManifestEntry(
                    book_slug="architecture",
                    title="아키텍처",
                    source_url="https://example.com/architecture",
                    resolved_source_url="https://example.com/architecture",
                    viewer_path="/docs/ocp/4.20/ko/architecture/index.html",
                    high_value=True,
                    content_status="approved_ko",
                    approval_status="approved",
                    citation_eligible=True,
                ),
            ]
            write_manifest(settings.source_catalog_path, catalog_entries)
            write_manifest(
                settings.source_manifest_path,
                [
                    SourceManifestEntry(
                        book_slug="machine_configuration",
                        title="Machine configuration",
                        source_url="https://example.com/machine_configuration",
                        resolved_source_url="https://example.com/machine_configuration",
                        viewer_path="/docs/ocp/4.20/ko/machine_configuration/index.html",
                        high_value=True,
                        content_status="approved_ko",
                        approval_status="approved",
                        citation_eligible=True,
                    ),
                    catalog_entries[1],
                ],
            )

            bundle = settings.bronze_dir / "source_bundles" / "machine_configuration"
            _write_json(
                bundle / "bundle_manifest.json",
                {
                    "official_docs": {
                        "ko": {"contains_language_fallback_banner": True},
                        "en": {"artifact_path": "en/source.html", "content_length": 200},
                    },
                    "repo_artifacts": [{"repo_path": "machine_configuration/index.adoc"}],
                },
            )
            _write_json(
                bundle / "dossier.json",
                {
                    "current_status": {
                        "content_status": "translated_ko_draft",
                        "gap_lane": "translation_first",
                    },
                    "official_docs": {
                        "en": {
                            "url": "https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html-single/machine_configuration/index"
                        }
                    },
                },
            )
            _write_json(
                bundle / "issue_pr_candidates.json",
                {"exact_slug": [], "related_terms": []},
            )

            report = write_synthesis_lane_outputs(settings)

            self.assertEqual(1, report["summary"]["approved_runtime_count"])
            self.assertEqual(1, report["summary"]["translation_ready_count"])
            working_entries = read_manifest(settings.corpus_working_manifest_path)
            self.assertEqual(
                ["architecture", "machine_configuration"],
                [entry.book_slug for entry in working_entries],
            )
            translated_entries = read_manifest(settings.translation_draft_manifest_path)
            self.assertEqual(["machine_configuration"], [entry.book_slug for entry in translated_entries])

    def test_write_synthesis_lane_outputs_keeps_manual_synthesis_with_heading_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            catalog_entries = [
                SourceManifestEntry(
                    book_slug="monitoring",
                    title="모니터링 운영 플레이북",
                    source_url="https://example.com/monitoring",
                    resolved_source_url="https://example.com/monitoring",
                    viewer_path="/docs/ocp/4.20/ko/monitoring/index.html",
                    high_value=True,
                    content_status="approved_ko",
                    approval_status="approved",
                    citation_eligible=True,
                    source_type="manual_synthesis",
                    source_lane="applied_playbook",
                    review_status="approved",
                ),
            ]
            write_manifest(settings.source_catalog_path, catalog_entries)
            write_manifest(settings.source_manifest_path, catalog_entries)
            _write_json(
                settings.playbook_books_dir / "monitoring.json",
                {
                    "book_slug": "monitoring",
                    "title": "Monitoring",
                    "translation_status": "approved_ko",
                    "source_metadata": {
                        "source_type": "manual_synthesis",
                        "source_lane": "applied_playbook",
                    },
                    "sections": [
                        {
                            "heading": "Overview",
                            "semantic_role": "procedure",
                            "blocks": [],
                        }
                    ],
                },
            )

            report = write_synthesis_lane_outputs(settings)

            self.assertEqual(1, report["summary"]["approved_runtime_count"])
            self.assertEqual(0, report["summary"]["manual_review_ready_count"])
            self.assertEqual([], report["manual_review_ready"])
            working_entries = read_manifest(settings.corpus_working_manifest_path)
            self.assertEqual(["monitoring"], [entry.book_slug for entry in working_entries])


if __name__ == "__main__":
    unittest.main()
