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

            manual_bundle = bronze_root / "operators"
            _write_json(
                manual_bundle / "bundle_manifest.json",
                {
                    "official_docs": {
                        "ko": {"contains_language_fallback_banner": False},
                        "en": {"artifact_path": "en/source.html", "content_length": 100},
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
                        "en": {"artifact_path": "en/source.html", "content_length": 100},
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
            self.assertEqual("manual_review_ready", rows["operators"]["readiness"])
            self.assertEqual("source_expansion_needed", rows["installing_on_any_platform"]["readiness"])


if __name__ == "__main__":
    unittest.main()
