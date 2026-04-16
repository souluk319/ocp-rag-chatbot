from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scripts import prepare_execution_harness


class PrepareExecutionHarnessTests(unittest.TestCase):
    def test_major_task_requires_explorer_and_worker_or_reviewer(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            args = [
                "prepare_execution_harness.py",
                "--task-id",
                "major-task-missing-lanes",
                "--shell",
                "powershell",
                "--cwd",
                tmpdir,
                "--python-path",
                str(Path(tmpdir) / ".venv" / "Scripts" / "python.exe"),
                "--worktree-path",
                tmpdir,
                "--lane-id",
                "main",
                "--role",
                "main",
                "--major-task",
                "--companion-lane",
                "explorer:explorer",
                "--write-scope",
                "src/play_book_studio/retrieval/*",
            ]
            with patch.object(sys, "argv", args):
                with self.assertRaises(SystemExit) as exc_info:
                    prepare_execution_harness.main()

        self.assertIn(
            "major task requires companion lanes including explorer and worker or reviewer",
            str(exc_info.exception),
        )

    def test_major_task_creates_companion_lane_skeletons(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            args = [
                "prepare_execution_harness.py",
                "--task-id",
                "major-task-lanes",
                "--shell",
                "powershell",
                "--cwd",
                tmpdir,
                "--python-path",
                str(root / ".venv" / "Scripts" / "python.exe"),
                "--worktree-path",
                tmpdir,
                "--lane-id",
                "main",
                "--role",
                "main",
                "--major-task",
                "--companion-lane",
                "explorer:explorer",
                "--companion-lane",
                "reviewer:reviewer",
                "--write-scope",
                "src/play_book_studio/retrieval/*",
                "--output",
                "artifacts/retrieval/retrieval_eval_report.json",
                "--validate",
                "python -m unittest tests.test_prepare_execution_harness",
            ]
            with patch.object(sys, "argv", args):
                exit_code = prepare_execution_harness.main()

            self.assertEqual(0, exit_code)

            main_manifest = json.loads(
                (
                    root
                    / "reports"
                    / "execution_harness"
                    / "major-task-lanes"
                    / "main"
                    / "manifest.json"
                ).read_text(encoding="utf-8")
            )
            self.assertTrue(main_manifest["major_task"])
            self.assertTrue(main_manifest["parallel_execution_required"])
            self.assertEqual(
                [
                    {"lane_id": "explorer", "role": "explorer"},
                    {"lane_id": "reviewer", "role": "reviewer"},
                ],
                main_manifest["companion_lanes"],
            )

            explorer_manifest = json.loads(
                (
                    root
                    / "reports"
                    / "execution_harness"
                    / "major-task-lanes"
                    / "explorer"
                    / "manifest.json"
                ).read_text(encoding="utf-8")
            )
            reviewer_manifest = json.loads(
                (
                    root
                    / "reports"
                    / "execution_harness"
                    / "major-task-lanes"
                    / "reviewer"
                    / "manifest.json"
                ).read_text(encoding="utf-8")
            )

            self.assertEqual("reserved", explorer_manifest["status"])
            self.assertEqual("reserved", reviewer_manifest["status"])
            self.assertEqual("reserved-by-main", explorer_manifest["write_scope"])
            self.assertEqual("reserved-by-main", reviewer_manifest["write_scope"])
            self.assertEqual("main", explorer_manifest["reserved_by_lane"])
            self.assertEqual("main", reviewer_manifest["reserved_by_lane"])


if __name__ == "__main__":
    unittest.main()
