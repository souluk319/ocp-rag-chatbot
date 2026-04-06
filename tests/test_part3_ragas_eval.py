from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag.answering.models import AnswerResult, Citation
from ocp_rag.answering.ragas_eval import (
    DEFAULT_OPENAI_EMBEDDING_MODEL,
    DEFAULT_OPENAI_JUDGE_MODEL,
    LANGCHAIN_OPENAI_AVAILABLE,
    OPENAI_SDK_AVAILABLE,
    RAGAS_AVAILABLE,
    build_openai_ragas_runtime,
    build_ragas_case_row,
    build_ragas_dataset,
    build_retrieved_contexts,
    load_openai_judge_config_from_env,
)


class RagasEvalTests(unittest.TestCase):
    def test_build_retrieved_contexts_renders_book_section_and_excerpt(self) -> None:
        result = AnswerResult(
            query="q",
            mode="ops",
            answer="답변: 테스트",
            rewritten_query="q",
            citations=[
                Citation(
                    index=1,
                    chunk_id="c1",
                    book_slug="support",
                    section="7.2.1. 노드 상태 확인",
                    anchor="a1",
                    source_url="https://example.com",
                    viewer_path="/docs/example",
                    excerpt="`oc adm top nodes` 명령을 사용합니다.",
                )
            ],
            cited_indices=[1],
            warnings=[],
            retrieval_trace={},
        )

        self.assertEqual(
            ["support | 7.2.1. 노드 상태 확인\n`oc adm top nodes` 명령을 사용합니다."],
            build_retrieved_contexts(result),
        )

    def test_build_ragas_case_row_accepts_legacy_aliases(self) -> None:
        row, metadata = build_ragas_case_row(
            {
                "id": "legacy-1",
                "question": "ETCD 백업 방법은?",
                "answer": "답변: 테스트",
                "contexts": ["ctx1", "ctx2"],
                "ground_truth": "cluster-backup.sh 사용",
            }
        )

        self.assertEqual("ETCD 백업 방법은?", row["user_input"])
        self.assertEqual("답변: 테스트", row["response"])
        self.assertEqual(["ctx1", "ctx2"], row["retrieved_contexts"])
        self.assertEqual("cluster-backup.sh 사용", row["reference"])
        self.assertEqual("precomputed", metadata["response_source"])

    def test_build_ragas_case_row_uses_generated_result_when_needed(self) -> None:
        generated = AnswerResult(
            query="질문",
            mode="ops",
            answer="답변: `oc adm top nodes` 를 사용합니다.",
            rewritten_query="질문",
            citations=[
                Citation(
                    index=1,
                    chunk_id="c1",
                    book_slug="support",
                    section="7.2.1. 노드 상태, 리소스 사용량 및 구성 확인",
                    anchor="a1",
                    source_url="https://example.com",
                    viewer_path="/docs/example",
                    excerpt="클러스터 내의 각 노드에 대한 CPU 및 메모리 사용량을 요약합니다.",
                )
            ],
            cited_indices=[1],
            warnings=["warning"],
            retrieval_trace={},
        )

        row, metadata = build_ragas_case_row(
            {
                "id": "generated-1",
                "query": "지금 클러스터 전체 노드 CPU랑 메모리 사용량을 한 번에 보려면 어떤 명령 써?",
                "reference": "`oc adm top nodes`",
            },
            generated_result=generated,
        )

        self.assertEqual("generated", metadata["response_source"])
        self.assertIn("support | 7.2.1.", row["retrieved_contexts"][0])
        self.assertEqual(["support"], metadata["cited_books"])

    def test_build_ragas_dataset_accepts_normalized_rows(self) -> None:
        if not RAGAS_AVAILABLE:
            self.skipTest("ragas is not installed in this environment")

        dataset = build_ragas_dataset(
            [
                {
                    "user_input": "질문",
                    "response": "답변",
                    "retrieved_contexts": ["ctx"],
                    "reference": "정답",
                }
            ]
        )

        self.assertEqual(1, len(dataset))

    def test_load_openai_judge_config_uses_defaults(self) -> None:
        config = load_openai_judge_config_from_env({"OPENAI_API_KEY": "test-key"})

        self.assertEqual("test-key", config.api_key)
        self.assertEqual(DEFAULT_OPENAI_JUDGE_MODEL, config.judge_model)
        self.assertEqual(DEFAULT_OPENAI_EMBEDDING_MODEL, config.embedding_model)

    def test_build_openai_ragas_runtime_builds_client_wrappers(self) -> None:
        if not RAGAS_AVAILABLE:
            self.skipTest("ragas is not installed in this environment")
        if not OPENAI_SDK_AVAILABLE:
            self.skipTest("openai is not installed in this environment")
        if not LANGCHAIN_OPENAI_AVAILABLE:
            self.skipTest("langchain_openai is not installed in this environment")

        config = load_openai_judge_config_from_env(
            {
                "OPENAI_API_KEY": "test-key",
                "OPENAI_JUDGE_MODEL": "gpt-5.2",
                "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
            }
        )

        llm, embeddings = build_openai_ragas_runtime(config)

        self.assertIsNotNone(llm)
        self.assertIsNotNone(embeddings)


if __name__ == "__main__":
    unittest.main()
