from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import Settings
from play_book_studio.ingestion import source_bundle


class _FakeResponse:
    def __init__(self, text: str, url: str) -> None:
        self._text = text
        self.url = url
        self.status_code = 200
        self.encoding = "utf-8"
        self.apparent_encoding = "utf-8"

    @property
    def text(self) -> str:
        return self._text

    def raise_for_status(self) -> None:
        return None


class SourceBundleTests(unittest.TestCase):
    def test_raw_github_content_url(self) -> None:
        self.assertEqual(
            "https://raw.githubusercontent.com/openshift/openshift-docs/main/backup_and_restore/index.adoc",
            source_bundle.raw_github_content_url("/backup_and_restore/index.adoc"),
        )

    def test_selected_repo_candidates_prefers_real_docs(self) -> None:
        dossier = {
            "openshift_docs_repo_candidates": [
                "backup_and_restore/application_backup_and_restore/aws-sts/images",
                "backup_and_restore/application_backup_and_restore/aws-sts/modules",
                "backup_and_restore/application_backup_and_restore/aws-sts/_attributes",
                "backup_and_restore/application_backup_and_restore/aws-sts/oadp-aws-sts.adoc",
                "backup_and_restore/application_backup_and_restore/aws-sts/notes.txt",
            ]
        }
        self.assertEqual(
            [
                "backup_and_restore/application_backup_and_restore/aws-sts/_attributes",
                "backup_and_restore/application_backup_and_restore/aws-sts/oadp-aws-sts.adoc",
                "backup_and_restore/application_backup_and_restore/aws-sts/notes.txt",
            ],
            source_bundle._selected_repo_candidates(dossier, 10),
        )

    def test_harvest_source_bundle_writes_expected_artifacts(self) -> None:
        dossier = {
            "slug": "backup_and_restore",
            "official_docs": {
                "ko": {"url": "https://docs.redhat.com/ko/doc", "contains_language_fallback_banner": True},
                "en": {"url": "https://docs.redhat.com/en/doc", "contains_language_fallback_banner": False},
            },
            "openshift_docs_repo_candidates": [
                "backup_and_restore/index.adoc",
                "backup_and_restore/modules/example.adoc",
            ],
            "issue_pr_candidates_exact_slug": [{"number": 101}],
            "issue_pr_candidates_related_terms": [{"number": 202}],
        }

        def fake_get(url: str, settings: Settings, **kwargs):
            self.assertIsInstance(settings, Settings)
            return _FakeResponse(f"payload for {url}", url)

        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            with (
                patch.object(source_bundle, "build_source_dossier", return_value=dossier),
                patch.object(source_bundle, "_get", side_effect=fake_get),
            ):
                manifest = source_bundle.harvest_source_bundle(settings, "backup_and_restore", max_repo_files=2)

            bundle_root = Path(manifest["bundle_root"])
            self.assertTrue((bundle_root / "dossier.json").exists())
            self.assertTrue((bundle_root / "official_docs" / "ko" / "source.html").exists())
            self.assertTrue((bundle_root / "official_docs" / "en" / "source.html").exists())
            self.assertTrue((bundle_root / "openshift_docs_repo" / "backup_and_restore" / "index.adoc").exists())
            self.assertTrue((bundle_root / "issue_pr_candidates.json").exists())
            self.assertTrue((bundle_root / "bundle_manifest.json").exists())
            self.assertEqual(2, len(manifest["repo_artifacts"]))
            issue_payload = json.loads((bundle_root / "issue_pr_candidates.json").read_text(encoding="utf-8"))
            self.assertEqual([{"number": 101}], issue_payload["exact_slug"])


if __name__ == "__main__":
    unittest.main()
