from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.answering.models import AnswerResult, Citation
from play_book_studio.app.session_flow import derive_next_context
from play_book_studio.retrieval.models import SessionContext

MANIFEST_PATH = ROOT / "manifests" / "demo_multiturn_scenarios.jsonl"


def _load_scenarios() -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _citation_for(turn: dict[str, object], *, index: int = 1) -> Citation:
    book_slug = str((turn.get("expected_book_slugs") or ["overview"])[0])
    topic = str(turn["expected_topic"])
    anchor = f"scenario-{turn['turn']}"
    return Citation(
        index=index,
        chunk_id=f"chunk-{index}",
        book_slug=book_slug,
        section=topic,
        anchor=anchor,
        source_url=f"https://example.com/{book_slug}",
        viewer_path=f"/docs/ocp/4.20/ko/{book_slug}/index.html#{anchor}",
        excerpt=topic,
    )


def _answer_result_for(turn: dict[str, object], *, mode: str) -> AnswerResult:
    citation = _citation_for(turn)
    return AnswerResult(
        query=str(turn["query"]),
        mode=mode,
        answer=f"답변: {turn['expected_topic']} [1]",
        rewritten_query=str(turn["query"]),
        citations=[citation],
        cited_indices=[1],
    )


class TestDemoMultiturnScenarios(unittest.TestCase):
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

    def test_topic_retention_scenarios_keep_single_topic(self) -> None:
        retention = [item for item in self.scenarios if item["track"] == "topic-retention"]
        self.assertEqual(4, len(retention))

        for scenario in retention:
            context = SessionContext(mode=str(scenario["mode"]), ocp_version="4.20")
            observed_topics: list[str] = []
            for turn in scenario["turns"]:
                result = _answer_result_for(turn, mode=str(scenario["mode"]))
                context = derive_next_context(
                    context,
                    query=str(turn["query"]),
                    mode=str(scenario["mode"]),
                    result=result,
                )
                observed_topics.append(context.current_topic or "")
                self.assertEqual(turn["expected_topic"], context.current_topic, scenario["id"])
                self.assertIsNone(context.unresolved_question, scenario["id"])

            self.assertEqual(
                {str(scenario["turns"][0]["expected_topic"])},
                set(observed_topics),
                scenario["id"],
            )

    def test_topic_shift_scenario_resets_topic_on_new_question(self) -> None:
        shift = [item for item in self.scenarios if item["track"] == "topic-shift"]
        self.assertEqual(1, len(shift))
        scenario = shift[0]

        context = SessionContext(mode=str(scenario["mode"]), ocp_version="4.20")
        observed_topics: list[str] = []
        for turn in scenario["turns"]:
            result = _answer_result_for(turn, mode=str(scenario["mode"]))
            context = derive_next_context(
                context,
                query=str(turn["query"]),
                mode=str(scenario["mode"]),
                result=result,
            )
            observed_topics.append(context.current_topic or "")
            self.assertEqual(turn["expected_topic"], context.current_topic)
            self.assertIsNone(context.unresolved_question)

        self.assertEqual("OpenShift 아키텍처", observed_topics[0])
        self.assertEqual("Route와 Ingress 비교", observed_topics[2])
        self.assertEqual("2.1.5.2. 클러스터의 모든 심각한 경고 해결", observed_topics[4])
        self.assertGreater(len(set(observed_topics)), 1)


if __name__ == "__main__":
    unittest.main()
