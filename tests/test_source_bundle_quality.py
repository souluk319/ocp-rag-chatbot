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
from play_book_studio.ingestion.manifest import write_manifest
from play_book_studio.ingestion.models import SourceManifestEntry
from play_book_studio.ingestion.source_bundle_quality import build_source_bundle_quality_report


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class SourceBundleQualityTests(unittest.TestCase):
    def test_build_source_bundle_quality_report_classifies_bundles(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            bronze_root = settings.bronze_dir / "source_bundles"

            translation_bundle = bronze_root / "machine_configuration"
            _write_json(
                translation_bundle / "bundle_manifest.json",
                {
                    "official_docs": {
                        "ko": {"contains_language_fallback_banner": True},
                        "en": {"artifact_path": "en/source.html", "content_length": 100},
                    },
                    "repo_artifacts": [{"repo_path": "machine_configuration/index.adoc"}],
                },
            )
            _write_json(
                translation_bundle / "dossier.json",
                {"current_status": {"content_status": "translated_ko_draft", "gap_lane": "translation_first"}},
            )
            _write_json(
                translation_bundle / "issue_pr_candidates.json",
                {"exact_slug": [{"number": 1}], "related_terms": [{"number": 2}]},
            )

            manual_bundle = bronze_root / "overview"
            _write_json(
                manual_bundle / "bundle_manifest.json",
                {
                    "official_docs": {
                        "ko": {"contains_language_fallback_banner": False},
                        "en": {},
                    },
                    "repo_artifacts": [{"repo_path": "operators/index.adoc"}],
                },
            )
            _write_json(
                manual_bundle / "dossier.json",
                {"current_status": {"content_status": "blocked", "gap_lane": "manual_review_first"}},
            )
            _write_json(
                manual_bundle / "issue_pr_candidates.json",
                {"exact_slug": [{"number": 3}], "related_terms": []},
            )

            weak_bundle = bronze_root / "installing_on_any_platform"
            _write_json(
                weak_bundle / "bundle_manifest.json",
                {
                    "official_docs": {
                        "ko": {"contains_language_fallback_banner": True},
                        "en": {},
                    },
                    "repo_artifacts": [],
                },
            )
            _write_json(
                weak_bundle / "dossier.json",
                {"current_status": {"content_status": "blocked", "gap_lane": "remaining_gap"}},
            )
            _write_json(
                weak_bundle / "issue_pr_candidates.json",
                {"exact_slug": [], "related_terms": [{"number": 4}]},
            )

            report = build_source_bundle_quality_report(settings)

            self.assertEqual(3, report["bundle_count"])
            self.assertEqual(1, report["counts"]["translation_ready"])
            self.assertEqual(1, report["counts"]["manual_review_ready"])
            self.assertEqual(1, report["counts"]["source_expansion_needed"])
            rows = {item["book_slug"]: item for item in report["bundles"]}
            self.assertEqual("translation_ready", rows["machine_configuration"]["readiness"])
            self.assertEqual("manual_review_ready", rows["overview"]["readiness"])
            self.assertEqual("source_expansion_needed", rows["installing_on_any_platform"]["readiness"])
            self.assertEqual(3, report["buyer_scope"]["raw_manual_count"])
            self.assertEqual(3, report["buyer_scope"]["promotion_queue_count"])
            self.assertEqual(1, report["buyer_scope"]["translation_ready_count"])
            self.assertEqual(1, report["buyer_scope"]["manual_review_ready_count"])
            self.assertEqual(1, report["buyer_scope"]["source_expansion_needed_count"])
            self.assertEqual(settings.active_pack_id, report["buyer_scope"]["pack_id"])
            self.assertEqual("4.20", report["buyer_scope"]["ocp_version"])
            self.assertEqual("ko", report["buyer_scope"]["docs_language"])
            self.assertEqual("bronze_bundle_readiness", report["buyer_scope"]["queue_scope"])
            self.assertIn("3 raw manuals remain in the bronze bundle readiness queue", report["buyer_scope"]["scope_verdict"])
            self.assertIn("topic playbook family is not emitted yet", report["buyer_scope"]["limits"][0])
            self.assertEqual(
                {
                    "operation_playbook": 0,
                    "policy_overlay_book": 0,
                    "synthesized_playbook": 0,
                    "topic_playbook": 0,
                    "troubleshooting_playbook": 0,
                },
                report["buyer_scope"]["derived_family_counts"],
            )
            self.assertEqual(0, report["approved_manifest_derived_playbook_count"])
            self.assertEqual(0, report["materialized_derived_playbook_count"])
            self.assertEqual(
                report["buyer_scope"]["approved_manifest_derived_family_counts"],
                report["approved_manifest_derived_family_counts"],
            )
            self.assertEqual(
                report["buyer_scope"]["materialized_derived_family_counts"],
                report["materialized_derived_family_counts"],
            )
            self.assertEqual(report["buyer_scope"]["derived_family_counts"], report["derived_family_counts"])

    def test_build_source_bundle_quality_report_exposes_manual_and_playable_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            bronze_root = settings.bronze_dir / "source_bundles"

            for slug in ("architecture", "etcd"):
                bundle = bronze_root / slug
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
                    bundle / "dossier.json",
                    {"current_status": {"content_status": "approved_ko", "gap_lane": "approved"}},
                )
                _write_json(
                    bundle / "issue_pr_candidates.json",
                    {"exact_slug": [], "related_terms": []},
                )

            catalog_entries = [
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

            report = build_source_bundle_quality_report(settings)

            self.assertEqual(2, report["buyer_scope"]["raw_manual_count"])
            self.assertEqual(1, report["buyer_scope"]["approved_manual_book_count"])
            self.assertEqual(6, report["buyer_scope"]["playable_book_count"])
            self.assertEqual(7, report["buyer_scope"]["playable_asset_count"])
            self.assertEqual(3.5, report["buyer_scope"]["playable_asset_multiplication"]["ratio_vs_raw_manual_count"])
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
                {
                    "operation_playbook": 0,
                    "policy_overlay_book": 0,
                    "synthesized_playbook": 0,
                    "topic_playbook": 0,
                    "troubleshooting_playbook": 0,
                },
                report["buyer_scope"]["approved_manifest_derived_family_counts"],
            )
            self.assertEqual(
                report["buyer_scope"]["materialized_derived_family_counts"],
                report["materialized_derived_family_counts"],
            )
            self.assertEqual(
                {
                    "manual_synthesis": 1,
                    "operation_playbook": 1,
                    "policy_overlay_book": 1,
                    "synthesized_playbook": 1,
                    "topic_playbook": 1,
                    "troubleshooting_playbook": 1,
                },
                report["buyer_scope"]["playable_family_counts"],
            )
            self.assertEqual(report["buyer_scope"]["derived_family_counts"], report["derived_family_counts"])
            self.assertEqual(
                "materialized",
                report["buyer_scope"]["derived_family_statuses"]["operation_playbook"]["status"],
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
            self.assertIn(
                "approved manifest derived 0",
                report["buyer_scope"]["scope_verdict"],
            )
            self.assertIn(
                "materialized derived 5 (operation_playbook 1, policy_overlay_book 1, synthesized_playbook 1, topic_playbook 1, troubleshooting_playbook 1)",
                report["buyer_scope"]["scope_verdict"],
            )

    def test_build_source_bundle_quality_report_prefers_translation_ready_when_en_html_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            bronze_root = settings.bronze_dir / "source_bundles"

            bundle = bronze_root / "web_console"
            _write_json(
                bundle / "bundle_manifest.json",
                {
                    "official_docs": {
                        "ko": {"contains_language_fallback_banner": False},
                        "en": {"artifact_path": "en/source.html", "content_length": 100},
                    },
                    "repo_artifacts": [{"repo_path": "web_console/index.adoc"}],
                },
            )
            _write_json(
                bundle / "dossier.json",
                {"current_status": {"content_status": "blocked", "gap_lane": "manual_review_first"}},
            )
            _write_json(
                bundle / "issue_pr_candidates.json",
                {"exact_slug": [], "related_terms": []},
            )

            report = build_source_bundle_quality_report(settings)

            self.assertEqual(1, report["counts"]["translation_ready"])
            row = report["bundles"][0]
            self.assertEqual("translation_ready", row["readiness"])
            self.assertIn("official EN translation", row["recommended_action"])

    def test_build_source_bundle_quality_report_marks_approved_bundle_as_already_promoted(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            bronze_root = settings.bronze_dir / "source_bundles"

            promoted_bundle = bronze_root / "machine_configuration"
            _write_json(
                promoted_bundle / "bundle_manifest.json",
                {
                    "official_docs": {
                        "ko": {"contains_language_fallback_banner": True},
                        "en": {"artifact_path": "en/source.html", "content_length": 100},
                    },
                    "repo_artifacts": [{"repo_path": "machine_configuration/index.adoc"}],
                },
            )
            _write_json(
                promoted_bundle / "dossier.json",
                {"current_status": {"content_status": "translated_ko_draft", "gap_lane": "translation_first"}},
            )
            _write_json(
                promoted_bundle / "issue_pr_candidates.json",
                {"exact_slug": [{"number": 1}], "related_terms": [{"number": 2}]},
            )

            write_manifest(
                settings.source_manifest_path,
                [
                    SourceManifestEntry(
                        ocp_version=settings.ocp_version,
                        docs_language=settings.docs_language,
                        book_slug="machine_configuration",
                        title="Machine configuration",
                        source_url="https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/machine_configuration/index",
                        resolved_source_url="https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/machine_configuration/index",
                        viewer_path="/docs/ocp/4.20/ko/machine_configuration/index.html",
                        high_value=True,
                        content_status="approved_ko",
                        approval_status="approved",
                    )
                ],
            )

            report = build_source_bundle_quality_report(settings)

            self.assertEqual(1, report["bundle_count"])
            self.assertEqual(1, report["counts"]["translation_ready"])
            self.assertEqual(0, report["counts"]["manual_review_ready"])
            self.assertEqual(0, report["counts"]["source_expansion_needed"])
            self.assertEqual(0, report["counts"]["already_promoted"])
            rows = {item["book_slug"]: item for item in report["bundles"]}
            self.assertEqual("translation_ready", rows["machine_configuration"]["readiness"])
            self.assertTrue(rows["machine_configuration"]["manifest_approved"])

    def test_build_source_bundle_quality_report_marks_clean_approved_bundle_as_already_promoted(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            bronze_root = settings.bronze_dir / "source_bundles"

            promoted_bundle = bronze_root / "etcd"
            _write_json(
                promoted_bundle / "bundle_manifest.json",
                {
                    "official_docs": {
                        "ko": {"contains_language_fallback_banner": False},
                        "en": {"artifact_path": "en/source.html", "content_length": 100},
                    },
                    "repo_artifacts": [{"repo_path": "etcd/index.adoc"}],
                },
            )
            _write_json(
                promoted_bundle / "dossier.json",
                {"current_status": {"content_status": "approved_ko", "gap_lane": ""}},
            )
            _write_json(
                promoted_bundle / "issue_pr_candidates.json",
                {"exact_slug": [{"number": 1}], "related_terms": []},
            )

            write_manifest(
                settings.source_manifest_path,
                [
                    SourceManifestEntry(
                        ocp_version=settings.ocp_version,
                        docs_language=settings.docs_language,
                        book_slug="etcd",
                        title="etcd",
                        source_url="https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/etcd/index",
                        resolved_source_url="https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/etcd/index",
                        viewer_path="/docs/ocp/4.20/ko/etcd/index.html",
                        high_value=True,
                        content_status="approved_ko",
                        approval_status="approved",
                    )
                ],
            )

            report = build_source_bundle_quality_report(settings)

            self.assertEqual(1, report["bundle_count"])
            self.assertEqual(1, report["counts"]["already_promoted"])
            rows = {item["book_slug"]: item for item in report["bundles"]}
            self.assertEqual("already_promoted", rows["etcd"]["readiness"])
            self.assertTrue(rows["etcd"]["manifest_approved"])

    def test_build_source_bundle_quality_report_accepts_curated_gold_override_with_fallback_banner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            bronze_root = settings.bronze_dir / "source_bundles"

            promoted_bundle = bronze_root / "backup_and_restore"
            _write_json(
                promoted_bundle / "bundle_manifest.json",
                {
                    "official_docs": {
                        "ko": {"contains_language_fallback_banner": True},
                        "en": {"artifact_path": "en/source.html", "content_length": 100},
                    },
                    "repo_artifacts": [{"repo_path": "backup_and_restore/index.adoc"}],
                },
            )
            _write_json(
                promoted_bundle / "dossier.json",
                {
                    "current_status": {
                        "content_status": "approved_ko",
                        "gap_lane": "approved",
                        "promotion_strategy": "curated_gold_manual_synthesis",
                    }
                },
            )
            _write_json(
                promoted_bundle / "issue_pr_candidates.json",
                {"exact_slug": [], "related_terms": []},
            )

            write_manifest(
                settings.source_manifest_path,
                [
                    SourceManifestEntry(
                        ocp_version=settings.ocp_version,
                        docs_language=settings.docs_language,
                        book_slug="backup_and_restore",
                        title="백업 및 복구 운영 플레이북",
                        source_url="https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/backup_and_restore/index",
                        resolved_source_url="https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/backup_and_restore/index",
                        viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html",
                        high_value=True,
                        content_status="approved_ko",
                        approval_status="approved",
                    )
                ],
            )

            report = build_source_bundle_quality_report(settings)

            self.assertEqual(1, report["bundle_count"])
            self.assertEqual(1, report["counts"]["already_promoted"])
            rows = {item["book_slug"]: item for item in report["bundles"]}
            self.assertEqual("already_promoted", rows["backup_and_restore"]["readiness"])
            self.assertEqual(
                "curated_gold_manual_synthesis",
                rows["backup_and_restore"]["promotion_strategy"],
            )

    def test_build_source_bundle_quality_report_accepts_translated_gold_override_with_fallback_banner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            bronze_root = settings.bronze_dir / "source_bundles"

            promoted_bundle = bronze_root / "monitoring"
            _write_json(
                promoted_bundle / "bundle_manifest.json",
                {
                    "official_docs": {
                        "ko": {"contains_language_fallback_banner": True},
                        "en": {"artifact_path": "en/source.html", "content_length": 100},
                    },
                    "repo_artifacts": [{"repo_path": "monitoring/index.adoc"}],
                },
            )
            _write_json(
                promoted_bundle / "dossier.json",
                {
                    "current_status": {
                        "content_status": "approved_ko",
                        "gap_lane": "approved",
                        "promotion_strategy": "translated_gold_manual_synthesis",
                    }
                },
            )
            _write_json(
                promoted_bundle / "issue_pr_candidates.json",
                {"exact_slug": [], "related_terms": []},
            )

            write_manifest(
                settings.source_manifest_path,
                [
                    SourceManifestEntry(
                        ocp_version=settings.ocp_version,
                        docs_language=settings.docs_language,
                        book_slug="monitoring",
                        title="모니터링",
                        source_url="https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/monitoring/index",
                        resolved_source_url="https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/monitoring/index",
                        viewer_path="/docs/ocp/4.20/ko/monitoring/index.html",
                        high_value=True,
                        content_status="approved_ko",
                        approval_status="approved",
                    )
                ],
            )

            report = build_source_bundle_quality_report(settings)

            self.assertEqual(1, report["bundle_count"])
            self.assertEqual(1, report["counts"]["already_promoted"])
            rows = {item["book_slug"]: item for item in report["bundles"]}
            self.assertEqual("already_promoted", rows["monitoring"]["readiness"])
            self.assertEqual(
                "translated_gold_manual_synthesis",
                rows["monitoring"]["promotion_strategy"],
            )


if __name__ == "__main__":
    unittest.main()
