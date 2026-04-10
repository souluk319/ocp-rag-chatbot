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
                        "en": {"artifact_path": "en/source.html", "content_length": 200},
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
            report = write_synthesis_lane_outputs(settings, report_path=report_path)

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


if __name__ == "__main__":
    unittest.main()
