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
from play_book_studio.ingestion import source_discovery


class _FakeResponse:
    def __init__(self, *, text: str = "", json_payload: dict | None = None, url: str = "", status_code: int = 200) -> None:
        self._text = text
        self._json_payload = json_payload or {}
        self.url = url
        self.status_code = status_code
        self.encoding = "utf-8"
        self.apparent_encoding = "utf-8"

    @property
    def text(self) -> str:
        return self._text

    def json(self) -> dict:
        return self._json_payload

    def raise_for_status(self) -> None:
        return None


class SourceDiscoveryTests(unittest.TestCase):
    def test_build_source_dossier_collects_expected_candidates(self) -> None:
        settings = Settings(root_dir=ROOT)
        approval_report = {
            "books": [
                {
                    "book_slug": "machine_configuration",
                    "title": "Machine configuration",
                    "content_status": "translated_ko_draft",
                    "gap_action": "preferred next step is Korean translation or source substitution",
                    "fallback_detected": True,
                    "hangul_chunk_ratio": 0.0,
                }
            ]
        }
        gap_report = {
            "translation_first": [{"book_slug": "machine_configuration"}],
            "manual_review_first": [],
            "remaining_gaps": [],
        }

        def fake_get(url: str, provided_settings: Settings, **kwargs):
            self.assertIs(provided_settings, settings)
            if "docs.redhat.com/ko/" in url:
                return _FakeResponse(
                    text="<title>Machine configuration | OCP</title>이 콘텐츠는 선택한 언어로 제공되지 않습니다",
                    url=url,
                )
            if "docs.redhat.com/en/" in url:
                return _FakeResponse(
                    text="<title>Machine configuration | OCP</title>",
                    url=url,
                )
            if "git/trees" in url:
                return _FakeResponse(
                    json_payload={
                        "tree": [
                            {"type": "blob", "path": "machine_configuration/index.adoc"},
                            {"type": "blob", "path": "machine_configuration/modules/example.adoc"},
                        ]
                    },
                    url=url,
                )
            if "search/issues" in url:
                query = kwargs["params"]["q"]
                return _FakeResponse(
                    json_payload={
                        "items": [
                            {
                                "number": 101,
                                "title": f"candidate for {query}",
                                "state": "open",
                                "html_url": "https://github.com/openshift/openshift-docs/pull/101",
                                "pull_request": {},
                                "updated_at": "2026-04-10T00:00:00Z",
                            }
                        ]
                    },
                    url=url,
                )
            raise AssertionError(f"unexpected url: {url}")

        with (
            patch.object(source_discovery, "_get", side_effect=fake_get),
            patch.object(source_discovery, "build_source_approval_report", return_value=approval_report),
            patch.object(source_discovery, "build_corpus_gap_report", return_value=gap_report),
        ):
            dossier = source_discovery.build_source_dossier(settings, "machine_configuration")

        self.assertEqual("translated_ko_draft", dossier["current_status"]["content_status"])
        self.assertEqual("translation_first", dossier["current_status"]["gap_lane"])
        self.assertTrue(dossier["official_docs"]["ko"]["contains_language_fallback_banner"])
        self.assertEqual(
            ["machine_configuration/index.adoc", "machine_configuration/modules/example.adoc"],
            dossier["openshift_docs_repo_candidates"],
        )
        self.assertIn("machine_configuration", dossier["repo_search_terms"]["aliases"])
        self.assertEqual(1, len(dossier["issue_pr_candidates_exact_slug"]))
        self.assertTrue(dossier["issue_pr_candidates_exact_slug"][0]["pull_request"])

    def test_build_source_dossier_uses_installing_platform_alias_and_filters_noise(self) -> None:
        settings = Settings(root_dir=ROOT)
        approval_report = {
            "books": [
                {
                    "book_slug": "installing_on_any_platform",
                    "title": "Installing on any platform",
                    "content_status": "blocked",
                    "gap_action": "preferred next step is Korean translation or source substitution",
                    "fallback_detected": False,
                    "hangul_chunk_ratio": 0.0,
                }
            ]
        }
        gap_report = {
            "translation_first": [],
            "manual_review_first": [],
            "remaining_gaps": [{"book_slug": "installing_on_any_platform"}],
        }
        queries_seen: list[str] = []

        def fake_get(url: str, provided_settings: Settings, **kwargs):
            self.assertIs(provided_settings, settings)
            if "docs.redhat.com/ko/" in url:
                return _FakeResponse(
                    text="<title>Installing on any platform | OCP</title>이 콘텐츠는 선택한 언어로 제공되지 않습니다",
                    url=url,
                )
            if "docs.redhat.com/en/" in url:
                return _FakeResponse(
                    text="<title>Installing on any platform | OCP</title>",
                    url=url,
                )
            if "git/trees" in url:
                return _FakeResponse(
                    json_payload={
                        "tree": [
                            {"type": "blob", "path": "installing/installing_platform_agnostic/installing-platform-agnostic.adoc"},
                            {"type": "blob", "path": "installing/installing_platform_agnostic/_attributes"},
                            {"type": "blob", "path": "installing/installing_platform_agnostic/images"},
                            {"type": "blob", "path": "installing/install_config/configuring-firewall.adoc"},
                            {"type": "blob", "path": "modules/monitoring-support-policy-for-monitoring-operators.adoc"},
                        ]
                    },
                    url=url,
                )
            if "search/issues" in url:
                query = kwargs["params"]["q"]
                queries_seen.append(query)
                if "platform_agnostic" in query or "Installing on any platform" in query:
                    return _FakeResponse(
                        json_payload={
                            "items": [
                                {
                                    "number": 202,
                                    "title": "Installing on any platform alignment",
                                    "state": "open",
                                    "html_url": "https://github.com/openshift/openshift-docs/pull/202",
                                    "pull_request": {},
                                    "updated_at": "2026-04-10T00:00:00Z",
                                }
                            ]
                        },
                        url=url,
                    )
                return _FakeResponse(json_payload={"items": []}, url=url)
            raise AssertionError(f"unexpected url: {url}")

        with (
            patch.object(source_discovery, "_get", side_effect=fake_get),
            patch.object(source_discovery, "build_source_approval_report", return_value=approval_report),
            patch.object(source_discovery, "build_corpus_gap_report", return_value=gap_report),
        ):
            dossier = source_discovery.build_source_dossier(settings, "installing_on_any_platform")

        self.assertIn("installing/installing_platform_agnostic/installing-platform-agnostic.adoc", dossier["openshift_docs_repo_candidates"])
        self.assertIn("installing_platform_agnostic", " ".join(dossier["repo_search_terms"]["aliases"]))
        self.assertEqual(
            "installing/installing_platform_agnostic/installing-platform-agnostic.adoc",
            dossier["openshift_docs_repo_candidates"][0],
        )
        self.assertNotIn("installing/installing_platform_agnostic/images", dossier["openshift_docs_repo_candidates"])
        self.assertTrue(any("Installing on any platform" in query or "platform_agnostic" in query for query in queries_seen))
        self.assertEqual(1, len(dossier["issue_pr_candidates_exact_slug"]))
        self.assertEqual(202, dossier["issue_pr_candidates_exact_slug"][0]["number"])

    def test_write_source_dossier_writes_json(self) -> None:
        dossier = {"slug": "machine_configuration", "current_status": {"content_status": "translated_ko_draft"}}
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "machine_configuration.json"
            source_discovery.write_source_dossier(target, dossier)
            self.assertEqual(dossier, json.loads(target.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
