from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ScriptEntrypointTests(unittest.TestCase):
    def test_canonical_entrypoints_expose_help(self) -> None:
        script_names = (
            "audit_data_quality.py",
            "run_ingest.py",
            "validate_ingest_outputs.py",
            "run_retrieval_benchmark.py",
            "run_retrieval_eval.py",
            "run_retrieval_query.py",
            "run_retrieval_sanity.py",
            "run_retrieval_smoke.py",
            "run_answer.py",
            "run_answer_eval.py",
            "run_ragas_eval.py",
            "run_console.py",
        )

        for script_name in script_names:
            with self.subTest(script=script_name):
                completed = subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / script_name), "--help"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    completed.returncode,
                    0,
                    msg=f"{script_name} failed: {completed.stderr}",
                )
                self.assertIn("usage:", completed.stdout.lower())

    def test_legacy_part_entrypoints_are_removed(self) -> None:
        legacy_scripts = (
            "audit_part1_data_quality.py",
            "run_part1.py",
            "run_part2_benchmark.py",
            "run_part2_eval.py",
            "run_part2_retrieval.py",
            "run_part2_sanity.py",
            "run_part2_smoke.py",
            "run_part3_answer.py",
            "run_part3_eval.py",
            "run_part3_ragas_eval.py",
            "run_part4_ui.py",
            "validate_part1_outputs.py",
        )
        for script_name in legacy_scripts:
            with self.subTest(script=script_name):
                self.assertFalse((ROOT / "scripts" / script_name).exists())

    def test_legacy_part_packages_are_removed(self) -> None:
        legacy_packages = (
            "ocp_rag_part1",
            "ocp_rag_part2",
            "ocp_rag_part3",
            "ocp_rag_part4",
            "ocp_rag_v2.egg-info",
        )
        for package_name in legacy_packages:
            with self.subTest(package=package_name):
                self.assertFalse((ROOT / "src" / package_name).exists())


if __name__ == "__main__":
    unittest.main()
