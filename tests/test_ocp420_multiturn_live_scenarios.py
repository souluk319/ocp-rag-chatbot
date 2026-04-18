from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "manifests" / "ocp420_multiturn_live_scenarios.jsonl"


def _load_scenarios() -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class TestOcp420MultiturnLiveScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenarios = _load_scenarios()

    def test_manifest_has_five_scenarios_with_six_turns_each(self) -> None:
        self.assertEqual(5, len(self.scenarios))
        for scenario in self.scenarios:
            turns = scenario["turns"]
            self.assertEqual(6, len(turns), scenario["id"])
            self.assertEqual([1, 2, 3, 4, 5, 6], [turn["turn"] for turn in turns], scenario["id"])
            for turn in turns:
                self.assertTrue(str(turn["query"]).strip(), scenario["id"])
                self.assertTrue(str(turn["expected_topic"]).strip(), scenario["id"])
                self.assertTrue(turn["expected_book_slugs"], scenario["id"])
                self.assertIn("citation_required", turn, scenario["id"])
                self.assertIn("previous_turn_context_required", turn, scenario["id"])
                self.assertTrue(str(turn["corpus_target"]).strip(), scenario["id"])

    def test_manifest_satisfies_demo_mix_constraints(self) -> None:
        track_counts: dict[str, int] = {}
        goal_type_counts: dict[str, int] = {}
        for scenario in self.scenarios:
            track = str(scenario["track"])
            goal_type = str(scenario["goal_type"])
            track_counts[track] = track_counts.get(track, 0) + 1
            goal_type_counts[goal_type] = goal_type_counts.get(goal_type, 0) + 1

        self.assertGreaterEqual(track_counts.get("topic-retention", 0), 2)
        self.assertGreaterEqual(track_counts.get("topic-shift", 0), 1)
        self.assertGreaterEqual(goal_type_counts.get("procedure", 0), 1)
        self.assertGreaterEqual(goal_type_counts.get("concept-to-practice", 0), 1)


if __name__ == "__main__":
    unittest.main()
