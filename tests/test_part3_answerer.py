from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.settings import Settings
from ocp_rag_part2.models import RetrievalHit, RetrievalResult, SessionContext
from ocp_rag_part3.answerer import (
    Part3Answerer,
    normalize_answer_text,
    summarize_session_context,
)
from ocp_rag_part3.llm import LLMClient
from ocp_rag_part3.prompt import build_messages


class _FakeRetriever:
    def retrieve(self, query, context, top_k, candidate_k):  # noqa: ANN001
        hit = RetrievalHit(
            chunk_id="chunk-1",
            book_slug="architecture",
            chapter="architecture",
            section="OpenShift 아키텍처 개요",
            anchor="overview",
            source_url="https://example.com/architecture",
            viewer_path="/docs/architecture.html#overview",
            text="OpenShift 아키텍처는 컨트롤 플레인과 작업자 노드로 구성됩니다.",
            source="hybrid",
            raw_score=1.0,
            fused_score=1.0,
        )
        return RetrievalResult(
            query=query,
            normalized_query=query,
            rewritten_query=query,
            top_k=top_k,
            candidate_k=candidate_k,
            context=(context or SessionContext()).to_dict(),
            hits=[hit],
            trace={"warnings": []},
        )


class _FakeLLMClient:
    def generate(self, messages):  # noqa: ANN001
        self.messages = messages
        return "### 답변\nOpenShift는 컨트롤 플레인과 작업자 노드로 구성됩니다. [1]"


class _FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self.payload


class Part3AnswererTests(unittest.TestCase):
    def test_build_messages_includes_grounding_context(self) -> None:
        from ocp_rag_part3.context import assemble_context

        hit = RetrievalHit(
            chunk_id="chunk-1",
            book_slug="architecture",
            chapter="architecture",
            section="개요",
            anchor="overview",
            source_url="https://example.com/architecture",
            viewer_path="/docs/architecture.html#overview",
            text="OpenShift 아키텍처 개요",
            source="hybrid",
            raw_score=1.0,
            fused_score=1.0,
        )
        bundle = assemble_context([hit])
        messages = build_messages(
            query="아키텍처 설명",
            mode="learn",
            context_bundle=bundle,
            session_summary="- 현재 주제: OpenShift 아키텍처",
        )

        self.assertEqual("system", messages[0]["role"])
        self.assertIn("[1] book=architecture", messages[1]["content"])
        self.assertIn("질문: 아키텍처 설명", messages[1]["content"])
        self.assertIn("세션 맥락:", messages[1]["content"])

    def test_build_messages_hardens_follow_up_constraints(self) -> None:
        from ocp_rag_part3.context import assemble_context

        hit = RetrievalHit(
            chunk_id="chunk-1",
            book_slug="etcd",
            chapter="etcd",
            section="복원",
            anchor="restore",
            source_url="https://example.com/etcd",
            viewer_path="/docs/etcd.html#restore",
            text="etcd 복원 절차",
            source="hybrid",
            raw_score=1.0,
            fused_score=1.0,
        )
        bundle = assemble_context([hit])
        messages = build_messages(
            query="그거 어떻게 해?",
            mode="ops",
            context_bundle=bundle,
            session_summary="- 현재 주제: etcd 복원",
        )

        self.assertIn("이전 대화 맥락은 해석 힌트일 뿐", messages[0]["content"])
        self.assertIn("follow-up이라도 현재 검색 근거가 약하면 단정하지 말고 확인 질문을 할 것", messages[1]["content"])
        self.assertIn("이전 맥락 때문에 현재 근거와 맞지 않는 대상을 끌어오지 말 것", messages[1]["content"])

    def test_build_messages_forces_brief_clarification_in_ambiguous_cases(self) -> None:
        messages = build_messages(
            query="로그는 어디서 봐?",
            mode="ops",
            context_bundle=type("Bundle", (), {"prompt_context": "", "citations": []})(),
            session_summary="",
        )

        self.assertIn("지금은 <불명확한 점>이 불명확합니다. <짧은 확인 질문>?", messages[0]["content"])
        self.assertIn("질문이 애매한 경우 '근거가 없습니다'로만 끝내지 말 것", messages[1]["content"])

    def test_answerer_returns_citations_and_used_indices(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_FakeRetriever(),
            llm_client=_FakeLLMClient(),
        )

        result = answerer.answer("OpenShift 아키텍처를 설명해줘", mode="learn")

        self.assertEqual([1], result.cited_indices)
        self.assertEqual("architecture", result.citations[0].book_slug)
        self.assertFalse(result.warnings)
        self.assertTrue(result.answer.startswith("답변:"))

    def test_normalize_answer_text_enforces_single_answer_prefix(self) -> None:
        normalized = normalize_answer_text("### 답변\n안녕하세요\nOpenShift 설명입니다. [1]")

        self.assertEqual("답변: OpenShift 설명입니다. [1]", normalized)

    def test_summarize_session_context_flattens_follow_up_hints(self) -> None:
        summary = summarize_session_context(
            SessionContext(
                mode="ops",
                current_topic="etcd 백업",
                open_entities=["etcd"],
                unresolved_question="복원 절차",
                ocp_version="4.20",
            )
        )

        self.assertIn("현재 주제: etcd 백업", summary)
        self.assertIn("열린 엔터티: etcd", summary)
        self.assertIn("미해결 질문: 복원 절차", summary)

    def test_llm_client_parses_chat_completions_response(self) -> None:
        settings = Settings(root_dir=ROOT)
        settings.llm_endpoint = "http://llm.local/v1"
        settings.llm_model = "demo-model"

        client = LLMClient(settings)

        import requests
        from unittest.mock import patch

        with patch.object(
            requests,
            "post",
            return_value=_FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": "답변: 테스트입니다. [1]",
                            }
                        }
                    ]
                }
            ),
        ) as mocked_post:
            content = client.generate([{"role": "user", "content": "질문"}])

        self.assertEqual("답변: 테스트입니다. [1]", content)
        self.assertEqual(
            "http://llm.local/v1/chat/completions",
            mocked_post.call_args.args[0],
        )
        self.assertFalse(mocked_post.call_args.kwargs["json"]["reasoning"])
        self.assertFalse(
            mocked_post.call_args.kwargs["json"]["chat_template_kwargs"]["enable_thinking"]
        )


if __name__ == "__main__":
    unittest.main()
