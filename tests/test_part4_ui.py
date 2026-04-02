from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part2.models import SessionContext
from ocp_rag_part3.models import AnswerResult, Citation
from ocp_rag_part4.server import (
    _citation_href,
    _derive_next_context,
    _viewer_path_to_local_html,
)


def _citation(index: int, *, anchor: str = "overview") -> Citation:
    return Citation(
        index=index,
        chunk_id=f"chunk-{index}",
        book_slug="architecture",
        section="OpenShift 아키텍처 개요",
        anchor=anchor,
        source_url="https://example.com/architecture/index",
        viewer_path="/docs/ocp/4.20/ko/architecture/index.html#overview",
        excerpt="OpenShift 아키텍처 개요",
    )


class Part4UiTests(unittest.TestCase):
    def test_citation_href_prefers_internal_viewer_path(self) -> None:
        href = _citation_href(_citation(1, anchor="overview-anchor"))

        self.assertEqual(
            "/docs/ocp/4.20/ko/architecture/index.html#overview",
            href,
        )

    def test_derive_next_context_updates_topic_when_grounded(self) -> None:
        result = AnswerResult(
            query="OpenShift 아키텍처 설명",
            mode="learn",
            answer="답변: 아키텍처 설명 [1]",
            rewritten_query="OpenShift 아키텍처 설명",
            citations=[_citation(1)],
            cited_indices=[1],
        )

        updated = _derive_next_context(
            SessionContext(mode="learn", current_topic="기존 주제", ocp_version="4.20"),
            query="OpenShift 아키텍처 설명",
            mode="learn",
            result=result,
        )

        self.assertEqual("learn", updated.mode)
        self.assertEqual("OpenShift 아키텍처 개요", updated.current_topic)
        self.assertIsNone(updated.unresolved_question)

    def test_derive_next_context_marks_unresolved_when_no_citations(self) -> None:
        result = AnswerResult(
            query="로그는 어디서 봐?",
            mode="ops",
            answer="답변: 지금은 어떤 로그를 말씀하시는지 불명확합니다. 애플리케이션 로그를 보시려는 건가요?",
            rewritten_query="로그는 어디서 봐?",
            citations=[],
        )

        updated = _derive_next_context(
            SessionContext(mode="ops", ocp_version="4.20"),
            query="로그는 어디서 봐?",
            mode="ops",
            result=result,
        )

        self.assertEqual("로그는 어디서 봐?", updated.unresolved_question)

    def test_viewer_path_maps_to_local_raw_html(self) -> None:
        target = _viewer_path_to_local_html(
            ROOT,
            "/docs/ocp/4.20/ko/architecture/index.html#overview",
        )

        self.assertIsNotNone(target)
        self.assertEqual("architecture.html", target.name)


if __name__ == "__main__":
    unittest.main()
