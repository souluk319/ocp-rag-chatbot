from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from _support_answering import *  # noqa: F401,F403

class TestAnsweringPrompt(unittest.TestCase):
    def test_build_messages_includes_grounding_context(self) -> None:
        from play_book_studio.answering.context import assemble_context

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
        from play_book_studio.answering.context import assemble_context

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

    def test_build_messages_enforces_ops_command_answer_shape(self) -> None:
        messages = build_messages(
            query="특정 namespace에만 admin 권한 주려면 어떤 명령 써?",
            mode="ops",
            context_bundle=type("Bundle", (), {"prompt_context": "[1] ...", "citations": []})(),
            session_summary="",
        )

        self.assertIn("bare command만 던지지 말고", messages[0]["content"])
        self.assertIn("한 줄 설명 -> 코드 블록 -> 짧은 범위/예시", messages[1]["content"])

    def test_build_messages_adds_compare_shape_hint(self) -> None:
        messages = build_messages(
            query="오픈시프트와 쿠버네티스 차이를 세 줄로 설명해줘",
            mode="learn",
            context_bundle=type("Bundle", (), {"prompt_context": "[1] ...", "citations": []})(),
            session_summary="",
        )

        self.assertIn("공통 기반 1문장 -> 핵심 차이 2~3개", messages[1]["content"])

    def test_build_messages_adds_intro_shape_hint(self) -> None:
        messages = build_messages(
            query="오픈시프트가 뭐야?",
            mode="learn",
            context_bundle=type("Bundle", (), {"prompt_context": "[1] ...", "citations": []})(),
            session_summary="",
        )

        self.assertIn("정의 1문장 -> 핵심 역할/구성 2~3개", messages[1]["content"])

    def test_build_messages_adds_project_finalizer_shape_hint(self) -> None:
        messages = build_messages(
            query="프로젝트가 Terminating 상태에서 finalizers 정리는 어떻게 해?",
            mode="ops",
            context_bundle=type("Bundle", (), {"prompt_context": "[1] ...", "citations": []})(),
            session_summary="",
        )

        self.assertIn("상태/남은 리소스 확인 명령", messages[1]["content"])

    def test_build_messages_adds_operator_concept_shape_hint(self) -> None:
        messages = build_messages(
            query="Operator가 왜 필요한지 예시까지 설명해줘",
            mode="learn",
            context_bundle=type("Bundle", (), {"prompt_context": "[1] ...", "citations": []})(),
            session_summary="",
        )

        self.assertIn("정의 1문장", messages[1]["content"])
        self.assertIn("예시를 짧게", messages[1]["content"])

    def test_build_messages_expands_learn_mode_explanations(self) -> None:
        messages = build_messages(
            query="CrashLoopBackOff가 반복될 때 확인 순서를 설명해줘",
            mode="learn",
            context_bundle=type("Bundle", (), {"prompt_context": "[1] ...", "citations": []})(),
            session_summary="",
        )

        self.assertIn("필요한 흐름과 이유와 확인 포인트를 충분히 설명하라", messages[0]["content"])
        self.assertIn("단계마다 왜 필요한지와 무엇을 확인해야 하는지 1~2문장씩 덧붙일 것", messages[1]["content"])
        self.assertIn("단계마다 왜 필요한지와 무엇을 확인해야 하는지 1~2문장씩 덧붙일 것", messages[1]["content"])
        self.assertIn("[CODE], [/CODE], [TABLE], [/TABLE] 같은 내부 태그를 답변에 그대로 노출하지 말고", messages[0]["content"])
        self.assertIn("[CODE], [/CODE], [TABLE], [/TABLE] 같은 내부 태그를 답변에 그대로 쓰지 말 것", messages[1]["content"])
        self.assertIn("OOM은 가능한 원인 중 하나", messages[1]["content"])

    def test_build_messages_adds_pod_pending_shape_hint(self) -> None:
        messages = build_messages(
            query="Pod Pending일 때 어디부터 확인해야 해?",
            mode="learn",
            context_bundle=type("Bundle", (), {"prompt_context": "[1] ...", "citations": []})(),
            session_summary="",
        )

        self.assertIn("이벤트로 FailedScheduling 이유 확인", messages[1]["content"])
        self.assertIn("첫 단계는 Pod Events 확인", messages[1]["content"])
