from __future__ import annotations

import json
import tempfile
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from _support_app_ui import (
    AnswerResult,
    ChatSession,
    SessionContext,
    Turn,
    _citation,
    _build_turn_diagnosis,
    _derive_next_context,
    _suggest_follow_up_questions,
    _write_recent_chat_session_snapshot,
)

class TestAppSessionFlow(unittest.TestCase):
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

        self.assertEqual("chat", updated.mode)
        self.assertEqual("OpenShift 아키텍처", updated.current_topic)
        self.assertEqual("OpenShift 아키텍처 설명", updated.user_goal)
        self.assertIsNone(updated.unresolved_question)

    def test_derive_next_context_preserves_rich_user_goal_for_follow_up_reference(self) -> None:
        result = AnswerResult(
            query="그럼 5개에서 10개로 변경하려면?",
            mode="ops",
            answer="답변: `oc scale` 명령으로 replicas를 10으로 바꾸면 됩니다. [1]",
            rewritten_query="OCP 4.20 | 사용자 목표 실행 중인 Deployment의 복제본(Replicas) 개수를 3개에서 5개로 변경하려면 어떻게 해야 해? | 그럼 5개에서 10개로 변경하려면?",
            citations=[_citation(1, section="Deployments")],
            cited_indices=[1],
        )

        updated = _derive_next_context(
            SessionContext(
                mode="ops",
                user_goal="실행 중인 Deployment의 복제본(Replicas) 개수를 3개에서 5개로 변경하려면 어떻게 해야 해?",
                current_topic="Deployment replicas",
                ocp_version="4.20",
            ),
            query="그럼 5개에서 10개로 변경하려면?",
            mode="ops",
            result=result,
        )

        self.assertEqual(
            "실행 중인 Deployment의 복제본(Replicas) 개수를 3개에서 5개로 변경하려면 어떻게 해야 해?",
            updated.user_goal,
        )
        self.assertEqual("Deployments", updated.current_topic)
        self.assertIsNone(updated.unresolved_question)

    def test_derive_next_context_tracks_deployment_scaling_topic(self) -> None:
        result = AnswerResult(
            query="실행 중인 Deployment의 복제본(Replicas) 개수를 3개에서 5개로 변경하려면 어떻게 해야 해?",
            mode="ops",
            answer="답변: `oc scale` 명령을 사용합니다. [1]",
            rewritten_query="실행 중인 Deployment의 복제본(Replicas) 개수를 3개에서 5개로 변경하려면 어떻게 해야 해?",
            citations=[_citation(1, section="2.6.1.124. oc scale", book_slug="cli_tools")],
            cited_indices=[1],
        )

        updated = _derive_next_context(
            SessionContext(mode="ops", ocp_version="4.20"),
            query="실행 중인 Deployment의 복제본(Replicas) 개수를 3개에서 5개로 변경하려면 어떻게 해야 해?",
            mode="ops",
            result=result,
        )

        self.assertEqual("Deployment 스케일링", updated.current_topic)
        self.assertEqual(["Deployment", "replicas"], updated.open_entities)
        self.assertEqual(
            "실행 중인 Deployment의 복제본(Replicas) 개수를 3개에서 5개로 변경하려면 어떻게 해야 해?",
            updated.user_goal,
        )

    def test_derive_next_context_tracks_route_ingress_compare_topic(self) -> None:
        result = AnswerResult(
            query="OpenShift에서 Route와 Ingress 차이를 운영 관점에서 설명해줘",
            mode="learn",
            answer="답변: Route와 Ingress는 노출 방식이 다릅니다. [1]",
            rewritten_query="OpenShift에서 Route와 Ingress 차이를 운영 관점에서 설명해줘",
            citations=[
                _citation(
                    1,
                    section="1.3.1. Ingress 및 Route 오브젝트를 사용하여 애플리케이션 노출",
                    book_slug="networking_overview",
                )
            ],
            cited_indices=[1],
        )

        updated = _derive_next_context(
            SessionContext(mode="learn", ocp_version="4.20"),
            query="OpenShift에서 Route와 Ingress 차이를 운영 관점에서 설명해줘",
            mode="learn",
            result=result,
        )

        self.assertEqual("Route와 Ingress 비교", updated.current_topic)
        self.assertEqual(["OpenShift", "Route", "Ingress"], updated.open_entities)
        self.assertEqual(
            "OpenShift에서 Route와 Ingress 차이를 운영 관점에서 설명해줘",
            updated.user_goal,
        )
        self.assertIsNone(updated.unresolved_question)

    def test_derive_next_context_preserves_route_ingress_topic_for_compare_follow_up(self) -> None:
        result = AnswerResult(
            query="쿠버네티스와 차이도 설명해줘",
            mode="learn",
            answer="답변: Kubernetes Ingress와 대비하면 Route는 노출 계층이 다릅니다. [1]",
            rewritten_query="OCP 4.20 | 주제 Route와 Ingress 비교 | 엔터티 OpenShift, Route, Ingress | 사용자 목표 OpenShift에서 Route와 Ingress 차이를 운영 관점에서 설명해줘 | 쿠버네티스와 차이도 설명해줘",
            citations=[
                _citation(
                    1,
                    section="1.3.1. Ingress 및 Route 오브젝트를 사용하여 애플리케이션 노출",
                    book_slug="networking_overview",
                )
            ],
            cited_indices=[1],
        )

        updated = _derive_next_context(
            SessionContext(
                mode="learn",
                user_goal="OpenShift에서 Route와 Ingress 차이를 운영 관점에서 설명해줘",
                current_topic="Route와 Ingress 비교",
                open_entities=["OpenShift", "Route", "Ingress"],
                ocp_version="4.20",
            ),
            query="쿠버네티스와 차이도 설명해줘",
            mode="learn",
            result=result,
        )

        self.assertEqual("Route와 Ingress 비교", updated.current_topic)
        self.assertEqual(["OpenShift", "Route", "Ingress"], updated.open_entities)
        self.assertEqual(
            "OpenShift에서 Route와 Ingress 차이를 운영 관점에서 설명해줘",
            updated.user_goal,
        )

    def test_derive_next_context_preserves_task_topic_for_corrective_follow_up(self) -> None:
        result = AnswerResult(
            query="그럼 명령어라도 알려줘",
            mode="ops",
            answer="답변: `oc scale` 명령을 사용합니다. [1]",
            rewritten_query="OCP 4.20 | 주제 Deployment 스케일링 | 사용자 목표 실행 중인 Deployment의 복제본(Replicas) 개수를 3개에서 5개로 변경하려면 어떻게 해야 해? | 그럼 명령어라도 알려줘",
            citations=[_citation(1, section="2.6.1.124. oc scale", book_slug="cli_tools")],
            cited_indices=[1],
        )

        updated = _derive_next_context(
            SessionContext(
                mode="ops",
                user_goal="실행 중인 Deployment의 복제본(Replicas) 개수를 3개에서 5개로 변경하려면 어떻게 해야 해?",
                current_topic="Deployment 스케일링",
                open_entities=["Deployment", "replicas"],
                ocp_version="4.20",
            ),
            query="그럼 명령어라도 알려줘",
            mode="ops",
            result=result,
        )

        self.assertEqual("Deployment 스케일링", updated.current_topic)
        self.assertEqual(["Deployment", "replicas"], updated.open_entities)

    def test_derive_next_context_preserves_rbac_task_topic_for_permission_follow_up(self) -> None:
        result = AnswerResult(
            query="그 권한이 잘 들어갔는지 확인하는 명령도 알려줘",
            mode="ops",
            answer="답변: rolebinding을 확인하면 됩니다. [1]",
            rewritten_query="OCP 4.20 | 주제 RBAC | 사용자 목표 특정 namespace에 admin 권한 주는 법 알려줘 | 그 권한이 잘 들어갔는지 확인하는 명령도 알려줘",
            citations=[
                _citation(
                    1,
                    section="1.3. OpenShift Container Platform에서 권한 부여 정보",
                    book_slug="authentication_and_authorization",
                )
            ],
            cited_indices=[1],
        )

        updated = _derive_next_context(
            SessionContext(
                mode="ops",
                user_goal="특정 namespace에 admin 권한 주는 법 알려줘",
                current_topic="RBAC",
                open_entities=["RBAC"],
                ocp_version="4.20",
            ),
            query="그 권한이 잘 들어갔는지 확인하는 명령도 알려줘",
            mode="ops",
            result=result,
        )

        self.assertEqual("RBAC", updated.current_topic)
        self.assertEqual(["RBAC"], updated.open_entities)
        self.assertEqual("특정 namespace에 admin 권한 주는 법 알려줘", updated.user_goal)

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

    def test_derive_next_context_ignores_smalltalk_route(self) -> None:
        result = AnswerResult(
            query="하이",
            mode="ops",
            answer="답변: 안녕하세요.",
            rewritten_query="하이",
            response_kind="smalltalk",
            citations=[],
        )

        updated = _derive_next_context(
            SessionContext(
                mode="ops",
                current_topic="etcd",
                open_entities=["etcd"],
                unresolved_question="복원은 어떻게 해?",
                ocp_version="4.20",
            ),
            query="하이",
            mode="ops",
            result=result,
        )

        self.assertEqual("etcd", updated.current_topic)
        self.assertEqual(["etcd"], updated.open_entities)
        self.assertEqual("복원은 어떻게 해?", updated.unresolved_question)

    def test_derive_next_context_preserves_topic_for_clarification_route(self) -> None:
        result = AnswerResult(
            query="로그는 어디서 봐?",
            mode="ops",
            answer="답변: 지금은 어떤 로그를 보려는지 불명확합니다.",
            rewritten_query="로그는 어디서 봐?",
            response_kind="clarification",
            citations=[],
        )

        updated = _derive_next_context(
            SessionContext(
                mode="ops",
                current_topic="OpenShift",
                open_entities=["OpenShift"],
                ocp_version="4.20",
            ),
            query="로그는 어디서 봐?",
            mode="ops",
            result=result,
        )

        self.assertEqual("OpenShift", updated.current_topic)
        self.assertEqual(["OpenShift"], updated.open_entities)
        self.assertEqual("로그는 어디서 봐?", updated.unresolved_question)

    def test_derive_next_context_prefers_explicit_new_topic_over_prior_citation_section(self) -> None:
        result = AnswerResult(
            query="오픈시프트에 대해 새줄약해봐",
            mode="ops",
            answer="답변: OpenShift 설명 [1]",
            rewritten_query="오픈시프트에 대해 새줄약해봐",
            citations=[
                _citation(
                    1,
                    section="2.1.3. 클러스터 업데이트 전 etcd 백업",
                    book_slug="updating_clusters",
                )
            ],
            cited_indices=[1],
        )

        updated = _derive_next_context(
            SessionContext(mode="ops", current_topic="etcd", ocp_version="4.20"),
            query="오픈시프트에 대해 새줄약해봐",
            mode="ops",
            result=result,
        )

        self.assertEqual("OpenShift", updated.current_topic)
        self.assertEqual(["OpenShift"], updated.open_entities)
        self.assertIsNone(updated.unresolved_question)

    def test_write_recent_chat_session_snapshot_keeps_latest_20_turns(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            session = ChatSession(session_id="f4296055abcdef12")
            session.history = [
                Turn(
                    query=f"질문 {index}",
                    mode="chat",
                    answer=f"답변 {index}",
                    rewritten_query=f"질문 {index} 확장",
                    response_kind="rag",
                    warnings=[],
                    stages=[
                        {"step": "user_input", "label": "사용자 입력", "value": f"질문 {index}"},
                        {"step": "rewritten_query", "label": "쿼리 재생성", "value": f"질문 {index} 확장"},
                    ],
                    diagnosis={
                        "severity": "ok",
                        "summary": "정상: 답변과 근거가 함께 생성됐습니다.",
                        "signals": ["문제 신호 없음"],
                    },
                )
                for index in range(25)
            ]

            output = _write_recent_chat_session_snapshot(root, session=session)

            payload = json.loads(output.read_text(encoding="utf-8"))
            session_payload = json.loads(
                (root / "artifacts" / "runtime" / "sessions" / "f4296055.json").read_text(encoding="utf-8")
            )

        self.assertEqual("세션 f4296055", payload["session_name"])
        self.assertEqual("f4296055abcdef12", payload["session_id"])
        self.assertEqual(20, payload["turn_count"])
        self.assertEqual(20, len(payload["turns"]))
        self.assertEqual("질문 5", payload["turns"][0]["user"])
        self.assertEqual("답변 24", payload["turns"][-1]["chatbot"])
        self.assertEqual("질문 5 확장", payload["turns"][0]["rewritten_query"])
        self.assertEqual("사용자 입력", payload["turns"][0]["stages"][0]["label"])
        self.assertEqual("ok", payload["turns"][0]["diagnosis"]["severity"])
        self.assertEqual(payload, session_payload)

    def test_build_turn_diagnosis_marks_missing_citations_as_risk(self) -> None:
        result = AnswerResult(
            query="질문",
            mode="chat",
            answer="답변",
            rewritten_query="질문 확장",
            response_kind="rag",
            citations=[],
            cited_indices=[],
            warnings=["answer has no inline citations"],
            retrieval_trace={"metrics": {"hybrid": {"count": 0}}, "reranker": {"enabled": False, "applied": False}},
            pipeline_trace={"llm": {"preferred_provider": "openai-compatible", "last_fallback_used": False}},
        )

        diagnosis = _build_turn_diagnosis(result)

        self.assertEqual("risk", diagnosis["severity"])
        self.assertIn("citation 없음", diagnosis["signals"])
        self.assertIn("hybrid 후보 없음", diagnosis["signals"])

    def test_suggest_follow_up_questions_for_rbac_answer(self) -> None:
        session = type(
            "SessionStub",
            (),
            {
                "mode": "ops",
                "context": SessionContext(mode="ops", current_topic="RBAC", ocp_version="4.20"),
            },
        )()
        result = AnswerResult(
            query="특정 namespace에 admin 권한 주려면 어떤 명령 써?",
            mode="ops",
            answer="답변: 명령은 ... [1]",
            rewritten_query="특정 namespace에 admin 권한 주려면 어떤 명령 써?",
            citations=[_citation(1, book_slug="authentication_and_authorization", section="9.6. 사용자 역할 추가")],
            cited_indices=[1],
        )

        suggestions = _suggest_follow_up_questions(session=session, result=result)

        self.assertEqual(3, len(suggestions))
        self.assertEqual(
            [
                "같은 권한을 RoleBinding YAML로 적용하는 예시도 보여줘",
                "권한이 제대로 들어갔는지 확인하는 명령도 알려줘",
                "권한이 너무 넓게 들어갔을 때 회수하는 방법도 알려줘",
            ],
            suggestions,
        )

    def test_suggest_follow_up_questions_refills_three_slots_after_clicking_play_plan_item(self) -> None:
        session = type(
            "SessionStub",
            (),
            {
                "mode": "ops",
                "context": SessionContext(mode="ops", current_topic="RBAC", ocp_version="4.20"),
            },
        )()
        result = AnswerResult(
            query="같은 권한을 RoleBinding YAML로 적용하는 예시도 보여줘",
            mode="ops",
            answer="답변: YAML 예시는 ... [1]",
            rewritten_query="같은 권한을 RoleBinding YAML로 적용하는 예시도 보여줘",
            citations=[_citation(1, book_slug="authentication_and_authorization", section="9.6. 사용자 역할 추가")],
            cited_indices=[1],
        )

        suggestions = _suggest_follow_up_questions(session=session, result=result)

        self.assertEqual(3, len(suggestions))
        self.assertEqual(
            [
                "권한이 제대로 들어갔는지 확인하는 명령도 알려줘",
                "권한이 너무 넓게 들어갔을 때 회수하는 방법도 알려줘",
                "edit 나 view 권한을 줄 때는 어떻게 달라?",
            ],
            suggestions,
        )

    def test_suggest_follow_up_questions_for_smalltalk_returns_product_starters(self) -> None:
        session = type(
            "SessionStub",
            (),
            {"mode": "ops", "context": SessionContext(mode="ops", ocp_version="4.20")},
        )()
        result = AnswerResult(
            query="하이",
            mode="ops",
            answer="답변: 안녕하세요.",
            rewritten_query="하이",
            response_kind="smalltalk",
            citations=[],
        )

        suggestions = _suggest_follow_up_questions(session=session, result=result)

        self.assertEqual(
            [
                "오픈시프트가 뭐야?",
                "특정 namespace에 admin 권한 주는 법 알려줘",
                "프로젝트가 Terminating에서 안 지워질 때 어떻게 해?",
            ],
            suggestions,
        )

    def test_suggest_follow_up_questions_contextualizes_generic_operator_followups(self) -> None:
        session = type(
            "SessionStub",
            (),
            {"mode": "chat", "context": SessionContext(mode="chat", current_topic="확장", ocp_version="4.20")},
        )()
        result = AnswerResult(
            query="Operator가 뭐고 왜 필요한가?",
            mode="chat",
            answer="답변: Operator는 ... [1]",
            rewritten_query="Operator가 뭐고 왜 필요한가?",
            citations=[_citation(1, book_slug="extensions", section="2장. 아키텍처 > 2.1. OLM v1 구성 요소 개요")],
            cited_indices=[1],
        )

        suggestions = _suggest_follow_up_questions(session=session, result=result)

        self.assertEqual(
            [
                "Operator 관련 다음 작업을 이어서 알려줘",
                "Operator 적용 후 검증 방법도 알려줘",
                "Operator 진행 중 막히면 다음에는 어디부터 확인해야 해?",
            ],
            suggestions,
        )

    def test_suggest_follow_up_questions_for_route_ingress_follow_play_flow(self) -> None:
        session = type(
            "SessionStub",
            (),
            {"mode": "chat", "context": SessionContext(mode="chat", current_topic="Route와 Ingress 비교", ocp_version="4.20")},
        )()
        result = AnswerResult(
            query="Route와 Ingress 차이를 운영 관점에서 설명해줘",
            mode="chat",
            answer="답변: Route는 ... [1]",
            rewritten_query="Route와 Ingress 차이를 운영 관점에서 설명해줘",
            citations=[_citation(1, book_slug="networking_overview", section="1.3.1. Ingress 및 Route 오브젝트를 사용하여 애플리케이션 노출")],
            cited_indices=[1],
        )

        suggestions = _suggest_follow_up_questions(session=session, result=result)

        self.assertEqual(
            [
                "OpenShift에서 Route를 실제로 만드는 예시를 보여줘",
                "노출이 정상인지 확인하는 명령과 체크포인트를 알려줘",
                "접속이 안 되거나 503이면 어디부터 봐야 하는지 알려줘",
            ],
            suggestions,
        )

    def test_suggest_follow_up_questions_uses_citation_metadata_for_procedure_flow(self) -> None:
        session = type(
            "SessionStub",
            (),
            {"mode": "ops", "context": SessionContext(mode="ops", current_topic="이미지 레지스트리", ocp_version="4.20")},
        )()
        citation = _citation(1, book_slug="registry", section="5.2. 레지스트리 상태 확인")
        citation.chunk_type = "procedure"
        citation.cli_commands = ("oc get pods -n openshift-image-registry",)
        citation.verification_hints = ("pod 상태 확인",)
        result = AnswerResult(
            query="이미지 레지스트리 상태를 점검하려면 어떻게 해?",
            mode="ops",
            answer="답변: 절차는 ... [1]",
            rewritten_query="이미지 레지스트리 상태를 점검하려면 어떻게 해?",
            citations=[citation],
            cited_indices=[1],
        )

        suggestions = _suggest_follow_up_questions(session=session, result=result)

        self.assertEqual(
            [
                "이미지 레지스트리 실행 명령만 추려서 다시 보여줘",
                "이미지 레지스트리 적용 후 검증 포인트를 기준으로 다시 정리해줘",
                "이미지 레지스트리 진행 중 막히면 다음에는 어디부터 확인해야 해?",
            ],
            suggestions,
        )

    def test_suggest_follow_up_questions_for_no_answer_returns_empty(self) -> None:
        session = type(
            "SessionStub",
            (),
            {"mode": "ops", "context": SessionContext(mode="ops", current_topic="이미지 레지스트리", ocp_version="4.20")},
        )()
        result = AnswerResult(
            query="이미지 레지스트리 저장소를 구성하려면?",
            mode="ops",
            answer="답변: 제공된 근거 문서에 관련 절차가 없습니다.",
            rewritten_query="이미지 레지스트리 저장소를 구성하려면?",
            response_kind="no_answer",
            citations=[],
        )

        suggestions = _suggest_follow_up_questions(session=session, result=result)

        self.assertEqual([], suggestions)

    def test_suggest_follow_up_questions_with_warnings_returns_empty(self) -> None:
        session = type(
            "SessionStub",
            (),
            {"mode": "chat", "context": SessionContext(mode="chat", current_topic="Route와 Ingress 비교", ocp_version="4.20")},
        )()
        result = AnswerResult(
            query="Route와 Ingress 관련 실행 예시도 같이 보여줘",
            mode="chat",
            answer="답변: 제공된 근거 문서에는 관련 실행 예시가 없습니다.",
            rewritten_query="Route와 Ingress 관련 실행 예시도 같이 보여줘",
            response_kind="rag",
            citations=[_citation(1, book_slug="networking_overview", section="1.3.1. Ingress 및 Route 오브젝트를 사용하여 애플리케이션 노출")],
            cited_indices=[1],
            warnings=["answer has no inline citations"],
        )

        suggestions = _suggest_follow_up_questions(session=session, result=result)

        self.assertEqual([], suggestions)
