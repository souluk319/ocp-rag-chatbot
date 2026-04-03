from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.settings import load_settings
from ocp_rag_part3.ragas_eval import (
    build_ragas_dataset,
    build_ragas_metrics,
    build_ragas_samples,
    judge_config_from_settings,
    summarize_ragas_rows,
)


class Part3RagasEvalTests(unittest.TestCase):
    def test_judge_config_requires_openai_api_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            old_key = os.environ.get("OPENAI_API_KEY")
            old_ragas_key = os.environ.get("RAGAS_OPENAI_API_KEY")
            try:
                os.environ.pop("OPENAI_API_KEY", None)
                os.environ.pop("RAGAS_OPENAI_API_KEY", None)
                settings = load_settings(root)
                with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY"):
                    judge_config_from_settings(settings)
            finally:
                if old_key is None:
                    os.environ.pop("OPENAI_API_KEY", None)
                else:
                    os.environ["OPENAI_API_KEY"] = old_key
                if old_ragas_key is None:
                    os.environ.pop("RAGAS_OPENAI_API_KEY", None)
                else:
                    os.environ["RAGAS_OPENAI_API_KEY"] = old_ragas_key

    def test_build_ragas_samples_uses_reference_answers_and_citation_excerpts(self) -> None:
        cases = [
            {
                "id": "case-1",
                "query": "etcd backup?",
                "reference_answer": "reference one",
            },
            {
                "id": "case-2",
                "query": "skip me",
            },
        ]
        details = [
            {
                "id": "case-1",
                "answer_text": "답변: backup [1]",
                "final_citations": [
                    {"excerpt": "first context"},
                    {"excerpt": "second context"},
                ],
            },
            {
                "id": "case-2",
                "answer_text": "답변: skip",
                "final_citations": [{"excerpt": "ignored"}],
            },
        ]

        samples, golden_cases, product_rows = build_ragas_samples(cases, details)

        self.assertEqual(1, len(samples))
        self.assertEqual("etcd backup?", samples[0]["user_input"])
        self.assertEqual("reference one", samples[0]["reference"])
        self.assertEqual(["first context", "second context"], samples[0]["retrieved_contexts"])
        self.assertEqual("case-1", golden_cases[0]["id"])
        self.assertEqual("case-1", product_rows[0]["id"])

    def test_build_ragas_dataset_wraps_samples_into_evaluation_dataset(self) -> None:
        dataset = build_ragas_dataset(
            [
                {
                    "user_input": "q",
                    "response": "a",
                    "retrieved_contexts": ["c1", "c2"],
                    "reference": "r",
                }
            ]
        )

        self.assertEqual(1, len(dataset.samples))
        self.assertEqual("q", dataset.samples[0].user_input)

    def test_summarize_ragas_rows_averages_available_scores(self) -> None:
        summary = summarize_ragas_rows(
            [
                {"faithfulness": 0.8, "answer_relevance": 0.7},
                {"faithfulness": 0.6, "answer_relevance": None},
            ],
            ["faithfulness", "answer_relevance"],
        )

        self.assertEqual(0.7, summary["faithfulness"])
        self.assertEqual(0.7, summary["answer_relevance"])

    def test_build_ragas_metrics_returns_expected_metric_names(self) -> None:
        metrics, metric_names = build_ragas_metrics(
            judge_config_from_settings(
                self._settings_with_fake_openai_key()
            )
        )

        self.assertEqual(4, len(metrics))
        self.assertEqual(
            ["faithfulness", "answer_relevance", "context_precision", "context_recall"],
            metric_names,
        )

    def _settings_with_fake_openai_key(self):
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        root = Path(tempdir.name)
        old_key = os.environ.get("OPENAI_API_KEY")
        self.addCleanup(self._restore_env, "OPENAI_API_KEY", old_key)
        os.environ["OPENAI_API_KEY"] = "test-key"
        return load_settings(root)

    @staticmethod
    def _restore_env(key: str, value: str | None) -> None:
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


if __name__ == "__main__":
    unittest.main()
