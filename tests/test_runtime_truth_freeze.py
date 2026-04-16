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

from play_book_studio.runtime_truth_freeze import audit_runtime_truth


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class RuntimeTruthFreezeTests(unittest.TestCase):
    def test_audit_runtime_truth_passes_for_consistent_active_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            candidate_path = root / "data" / "gold_candidate_books" / "full_rebuild" / "overview.md"
            runtime_path = root / "data" / "wiki_runtime_books" / "full_rebuild" / "overview.md"
            candidate_path.parent.mkdir(parents=True, exist_ok=True)
            runtime_path.parent.mkdir(parents=True, exist_ok=True)
            markdown = "# 개요\n\n## 소개\n\n본문\n"
            candidate_path.write_text(markdown, encoding="utf-8")
            runtime_path.write_text(markdown, encoding="utf-8")

            _write_json(
                root / "data" / "wiki_runtime_books" / "full_rebuild_manifest.json",
                {
                    "generated_at_utc": "2026-04-16T12:59:58+00:00",
                    "entries": [
                        {
                            "slug": "overview",
                            "source_candidate_path": str(candidate_path),
                            "runtime_path": str(runtime_path),
                        }
                    ],
                },
            )
            _write_json(
                root / "data" / "wiki_runtime_books" / "active_manifest.json",
                {
                    "generated_at_utc": "2026-04-16T13:00:19+00:00",
                    "active_group": "full_rebuild",
                    "source_manifest_path": str(root / "data" / "wiki_runtime_books" / "full_rebuild_manifest.json"),
                    "entries": [
                        {
                            "slug": "overview",
                            "source_candidate_path": str(candidate_path),
                            "runtime_path": str(runtime_path),
                        }
                    ],
                },
            )
            _write_json(
                root / "manifests" / "ocp420_source_first_full_rebuild_manifest.json",
                {
                    "entries": [
                        {
                            "book_slug": "overview",
                            "source_relative_path": "overview/index.adoc",
                            "rebuild_target_paths": {
                                "wiki_runtime_md": "data/wiki_runtime_books/full_rebuild/overview.md",
                            },
                        }
                    ]
                },
            )
            _write_json(
                root / "reports" / "build_logs" / "ocp420_one_click_runtime_report.json",
                {
                    "status": "ok",
                    "step_results": [{"step_id": "one", "returncode": 0}],
                    "smoke": {
                        "runtime_viewer_has_title": True,
                        "runtime_viewer_has_networking_hub": True,
                        "runtime_viewer_has_related_sections": True,
                        "storage_viewer_has_topic_hub": True,
                        "proxy_hub_has_related_figures": True,
                        "proxy_hub_has_related_sections": True,
                        "nodes_viewer_has_figure": True,
                        "architecture_viewer_has_figure": True,
                        "architecture_figure_viewer_has_parent_book": True,
                        "architecture_figure_viewer_has_related_section": True,
                    },
                },
            )

            report = audit_runtime_truth(root)

        self.assertEqual("ok", report["status"])
        self.assertTrue(report["metrics"]["canonical_truth_owner_uniqueness_verified"])
        self.assertEqual(1, report["metrics"]["canonical_truth_owner_count_per_book"])
        self.assertEqual(0, report["metrics"]["legacy_anchor_unresolved_count"])
        self.assertEqual(0, report["metrics"]["one_click_rebuild_exit_code"])

    def test_audit_runtime_truth_fails_when_duplicate_slug_and_anchor_drift_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            candidate_path = root / "data" / "gold_candidate_books" / "full_rebuild" / "overview.md"
            runtime_path = root / "data" / "wiki_runtime_books" / "full_rebuild" / "overview.md"
            candidate_path.parent.mkdir(parents=True, exist_ok=True)
            runtime_path.parent.mkdir(parents=True, exist_ok=True)
            candidate_path.write_text("# 개요\n\n## 소개\n", encoding="utf-8")
            runtime_path.write_text("# 개요\n\n## 변경된 소개\n", encoding="utf-8")

            _write_json(
                root / "data" / "wiki_runtime_books" / "full_rebuild_manifest.json",
                {
                    "entries": [
                        {
                            "slug": "overview",
                            "source_candidate_path": str(candidate_path),
                            "runtime_path": str(runtime_path),
                        }
                    ],
                },
            )
            _write_json(
                root / "data" / "wiki_runtime_books" / "active_manifest.json",
                {
                    "generated_at_utc": "2026-04-16T13:00:19+00:00",
                    "active_group": "full_rebuild",
                    "source_manifest_path": str(root / "data" / "wiki_runtime_books" / "full_rebuild_manifest.json"),
                    "entries": [
                        {
                            "slug": "overview",
                            "source_candidate_path": str(candidate_path),
                            "runtime_path": str(runtime_path),
                        },
                        {
                            "slug": "overview",
                            "source_candidate_path": str(candidate_path),
                            "runtime_path": str(runtime_path),
                        },
                    ],
                },
            )
            _write_json(
                root / "manifests" / "ocp420_source_first_full_rebuild_manifest.json",
                {"entries": []},
            )
            _write_json(
                root / "reports" / "build_logs" / "ocp420_one_click_runtime_report.json",
                {
                    "status": "fail",
                    "step_results": [{"step_id": "one", "returncode": 1}],
                    "smoke": {"runtime_viewer_has_title": False},
                },
            )

            report = audit_runtime_truth(root)

        self.assertEqual("fail", report["status"])
        self.assertFalse(report["metrics"]["canonical_truth_owner_uniqueness_verified"])
        self.assertGreater(report["metrics"]["owner_confusion_count"], 0)
        self.assertGreater(report["metrics"]["legacy_anchor_unresolved_count"], 0)
        self.assertEqual(1, report["metrics"]["one_click_rebuild_exit_code"])


if __name__ == "__main__":
    unittest.main()
