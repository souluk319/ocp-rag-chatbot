from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_script_module(name: str, relative_path: str):
    script_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load script module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestRepoWideEvalMatching(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.retrieval_script = _load_script_module("run_retrieval_eval_test", "scripts/run_retrieval_eval.py")
        cls.multiturn_script = _load_script_module("run_ocp420_multiturn_eval_test", "scripts/run_ocp420_multiturn_eval.py")

    def test_retrieval_eval_normalizes_repo_wide_slug_to_legacy_expected_family(self) -> None:
        normalized = self.retrieval_script._normalize_book_slug_list(
            [
                "authentication__using_rbac",
                "networking__ingress_load_balancing__routes__creating_basic_routes",
                "installing__installing_bare_metal__bare_metal_postinstallation_configuration",
            ],
            expected_book_slugs=[
                "authentication_and_authorization",
                "ingress_and_load_balancing",
                "postinstallation_configuration",
            ],
            expected_book_families=[],
        )

        self.assertEqual(
            [
                "authentication_and_authorization",
                "ingress_and_load_balancing",
                "postinstallation_configuration",
            ],
            normalized,
        )

    def test_multiturn_eval_normalizes_repo_wide_slug_list_to_expected_book_set(self) -> None:
        normalized = self.multiturn_script._normalize_book_list(
            [
                "operators__user__olm_installing_operators_in_namespace",
                "machine_configuration__machine_config_node_disruption",
            ],
            expected_book_slugs=["operators", "machine_configuration"],
            expected_book_families=[],
        )

        self.assertEqual(
            ["operators", "machine_configuration"],
            normalized,
        )


if __name__ == "__main__":
    unittest.main()
