from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part2.models import SessionContext
from ocp_rag_part3.models import AnswerResult, Citation, ConfidenceResult
from ocp_rag_part4.server import (
    INDEX_HTML_PATH,
    ChatSession,
    _build_chat_payload,
    _citation_href,
    _citation_payload,
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
    def test_static_ui_mentions_internal_docs_and_core_actions(self) -> None:
        html = INDEX_HTML_PATH.read_text(encoding="utf-8")

        self.assertIn("OCP 운영/교육 가이드 챗봇", html)
        self.assertIn("질문 보내기", html)
        self.assertIn("세션 초기화", html)
        self.assertIn("내부 문서", html)
        self.assertIn("질문을 정리하고 있습니다", html)
        self.assertIn("이어서 물어볼 질문", html)
        self.assertIn("confidence-panel", html)
        self.assertIn("검토 필요", html)

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
        self.assertEqual(["OpenShift Container Platform"], updated.open_entities)
        self.assertEqual("개념 설명", updated.user_goal)
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

    def test_viewer_path_maps_to_local_viewer_html(self) -> None:
        target = _viewer_path_to_local_html(
            ROOT,
            "/docs/ocp/4.20/ko/architecture/index.html#overview",
        )

        self.assertIsNotNone(target)
        self.assertEqual("index.html", target.name)
        self.assertEqual("architecture", target.parent.name)

    def test_citation_payload_includes_language_policy_metadata(self) -> None:
        payload = _citation_payload(
            _citation(1),
            {
                "architecture": {
                    "language_status": "ko_first",
                    "recommended_action": "keep",
                    "translation_priority": "none",
                }
            },
        )

        self.assertEqual("/docs/ocp/4.20/ko/architecture/index.html#overview", payload["href"])
        self.assertEqual("한국어 우선", payload["language_policy"]["badge"])

    def test_chat_payload_exposes_confidence_result(self) -> None:
        result = AnswerResult(
            query="OpenShift 아키텍처를 설명해줘",
            mode="learn",
            answer="답변: OpenShift 아키텍처 개요입니다. [1]",
            rewritten_query="OpenShift 아키텍처를 설명해줘",
            citations=[_citation(1)],
            cited_indices=[1],
            confidence=ConfidenceResult(
                score=0.61,
                level="medium",
                reason="답변은 가능하지만 세부 절차는 출처를 함께 보는 편이 안전합니다.",
                degraded=False,
            ),
        )

        payload = _build_chat_payload(
            session=ChatSession(session_id="session-1"),
            result=result,
            language_policy_map={},
        )

        self.assertEqual("medium", payload["confidence"]["level"])
        self.assertAlmostEqual(0.61, payload["confidence"]["score"])


if __name__ == "__main__":
    unittest.main()
