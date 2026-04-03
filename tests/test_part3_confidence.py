from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part2.models import RetrievalHit
from ocp_rag_part3.confidence import calculate_confidence
from ocp_rag_part3.models import Citation


def _hit(chunk_id: str, book_slug: str, text: str, score: float) -> RetrievalHit:
    return RetrievalHit(
        chunk_id=chunk_id,
        book_slug=book_slug,
        chapter=book_slug,
        section="section",
        anchor="section",
        source_url="https://example.com",
        viewer_path="/docs/example.html#section",
        text=text,
        source="hybrid",
        raw_score=score,
        fused_score=score,
    )


def _citation(index: int, book_slug: str) -> Citation:
    return Citation(
        index=index,
        chunk_id=f"chunk-{index}",
        book_slug=book_slug,
        section="section",
        anchor="section",
        source_url="https://example.com",
        viewer_path="/docs/example.html#section",
        excerpt="excerpt",
    )


class ConfidenceTests(unittest.TestCase):
    def test_confidence_none_without_hits(self) -> None:
        result = calculate_confidence("로그는 어디서 봐?", [], [], [])

        self.assertEqual("none", result.level)
        self.assertTrue(result.degraded)

    def test_confidence_high_with_consistent_support(self) -> None:
        result = calculate_confidence(
            "etcd 백업은 어떻게 해?",
            [
                _hit("chunk-1", "etcd", "etcd backup snapshot 절차와 주의점", 0.021),
                _hit("chunk-2", "etcd", "etcd backup snapshot 복구 전 확인사항", 0.0205),
                _hit("chunk-3", "etcd", "etcd backup 운영 가이드", 0.0202),
            ],
            [_citation(1, "etcd"), _citation(2, "etcd")],
            [],
        )

        self.assertIn(result.level, {"high", "medium"})
        self.assertFalse(result.degraded)


if __name__ == "__main__":
    unittest.main()
