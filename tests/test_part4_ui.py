from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part2.models import SessionContext
from ocp_rag_part2.query import rewrite_query
from ocp_rag_part3.models import AnswerResult, Citation
from ocp_rag_part4.server import (
    _citation_href,
    _derive_next_context,
    _internal_viewer_html,
    _suggest_follow_up_questions,
    _viewer_path_to_local_html,
)


def _citation(
    index: int,
    *,
    anchor: str = "overview",
    section: str = "OpenShift 아키텍처 개요",
    book_slug: str = "architecture",
) -> Citation:
    return Citation(
        index=index,
        chunk_id=f"chunk-{index}",
        book_slug=book_slug,
        section=section,
        anchor=anchor,
        source_url="https://example.com/architecture/index",
        viewer_path="/docs/ocp/4.20/ko/architecture/index.html#overview",
        excerpt="OpenShift 아키텍처 개요",
    )


class Part4UiTests(unittest.TestCase):
    def test_static_ui_guards_enter_during_ime_composition(self) -> None:
        html = (
            ROOT / "src" / "ocp_rag_part4" / "static" / "index.html"
        ).read_text(encoding="utf-8")

        self.assertIn("event.isComposing || event.keyCode === 229 || isComposing", html)
        self.assertIn('composerEl.addEventListener("compositionstart"', html)
        self.assertIn('composerEl.addEventListener("compositionend"', html)
        self.assertIn("function renderMarkdownInto", html)
        self.assertIn("navigator.clipboard.writeText", html)
        self.assertIn('copyButton.textContent = "복사"', html)
        self.assertIn("/api/chat/stream", html)
        self.assertIn('id="pipeline-trace"', html)
        self.assertIn("function consumeChatStream", html)
        self.assertIn("function startStatusPulse", html)
        self.assertIn('id="pipeline-summary"', html)
        self.assertIn("OpenShift Operations QA Console", html)
        self.assertIn("--accent: #ee0000;", html)
        self.assertIn("function renderEmptyState", html)
        self.assertIn('class="sample-chip"', html)
        self.assertIn("function normalizeAssistantAnswer", html)
        self.assertIn('label.textContent = "Answer"', html)
        self.assertIn('title.textContent = "Grounded Sources"', html)
        self.assertIn(".assistant-copy", html)
        self.assertIn(".citation-list-title", html)
        self.assertIn(".suggestion-list-title", html)
        self.assertIn(".followup-chip", html)
        self.assertIn('title.textContent = "이어서 볼 질문"', html)
        self.assertIn('sendMessage({ query: suggestedQuery })', html)
        self.assertIn('id="inspector-toggle-btn"', html)
        self.assertIn("function setInspectorVisible", html)
        self.assertIn("function setInspectorTab", html)
        self.assertIn('data-inspector-tab="sources"', html)
        self.assertIn('data-inspector-tab="document"', html)
        self.assertIn('data-inspector-tab="trace"', html)
        self.assertIn('id="source-list"', html)
        self.assertIn('id="document-frame"', html)
        self.assertIn("function openCitationInPanel", html)
        self.assertIn("function renderSourcesPanel", html)
        self.assertIn("function renderSearchMetrics", html)
        self.assertIn("function renderPendingCard", html)
        self.assertIn('setInspectorTab("sources")', html)
        self.assertNotIn('data-inspector-tab="pipeline"', html)
        self.assertIn(".summary-grid", html)
        self.assertIn("function humanizePipelineKey", html)
        self.assertIn("function summarizeTraceMeta", html)
        self.assertIn(".trace-step", html)
        self.assertIn("function humanizePipelineKey", html)
        self.assertIn("function summarizeTraceMeta", html)
        self.assertIn('class="summary-grid"', html)

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
        self.assertEqual("OpenShift 아키텍처", updated.current_topic)
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

    def test_derive_next_context_keeps_semantic_topic_when_citation_section_is_raw_heading(self) -> None:
        result = AnswerResult(
            query="그 명령 다시 보여줘",
            mode="ops",
            answer="답변: 명령은 이 문서를 참고하세요 [1]",
            rewritten_query="그 명령 다시 보여줘",
            citations=[
                _citation(
                    1,
                    book_slug="postinstallation_configuration",
                    section="3.2. 클러스터 재시작",
                )
            ],
            cited_indices=[1],
        )

        updated = _derive_next_context(
            SessionContext(
                mode="ops",
                current_topic="RBAC",
                open_entities=["RBAC"],
                ocp_version="4.20",
            ),
            query="그 명령 다시 보여줘",
            mode="ops",
            result=result,
        )

        self.assertEqual("RBAC", updated.current_topic)
        self.assertEqual(["RBAC"], updated.open_entities)
        self.assertIsNone(updated.unresolved_question)

    def test_derive_next_context_captures_memory_ledgers_from_answer(self) -> None:
        result = AnswerResult(
            query="특정 namespace만 admin 권한 주는 방법 단계별로 알려줘",
            mode="ops",
            answer=(
                "답변: namespace에서 admin 권한을 부여하려면 RoleBinding을 사용합니다 [1].\n\n"
                "1. **역할 바인딩 추가**\n"
                "```bash\noc adm policy add-role-to-user admin alice -n joe\n```\n\n"
                "2. **적용 결과 확인**\n"
                "```bash\noc describe rolebinding -n joe\n```"
            ),
            rewritten_query="특정 namespace만 admin 권한 주는 방법 단계별로 알려줘",
            citations=[
                _citation(
                    1,
                    book_slug="authentication_and_authorization",
                    section="9.6. 사용자 역할 추가",
                )
            ],
            cited_indices=[1],
        )

        updated = _derive_next_context(
            SessionContext(mode="ops", current_topic="OpenShift", ocp_version="4.20"),
            query="특정 namespace만 admin 권한 주는 방법 단계별로 알려줘",
            mode="ops",
            result=result,
        )

        self.assertIn("RBAC", updated.topic_journal)
        self.assertIn("authentication_and_authorization · 9.6. 사용자 역할 추가", updated.reference_hints)
        self.assertEqual(["역할 바인딩 추가", "적용 결과 확인"], updated.recent_steps)
        self.assertIn("oc adm policy add-role-to-user admin alice -n joe", updated.recent_commands)

    def test_multiturn_memory_compacts_but_survives_beyond_ten_turns(self) -> None:
        context = SessionContext(mode="ops", ocp_version="4.20")

        for index in range(14):
            result = AnswerResult(
                query=f"질문 {index}",
                mode="ops",
                answer=f"답변: 항목 {index} 설명 [1]",
                rewritten_query=f"질문 {index}",
                citations=[_citation(1, book_slug="support", section=f"절차 {index}")],
                cited_indices=[1],
            )
            context = _derive_next_context(
                context,
                query=f"질문 {index}",
                mode="ops",
                result=result,
            )

        self.assertEqual(12, len(context.recent_turns))
        self.assertEqual("질문 2", context.recent_turns[0].query)
        rewritten = rewrite_query("그거 다시 설명해줘", context)
        self.assertIn("최근 대화 캡슐", rewritten)
        self.assertIn("절차 13", rewritten)

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
        self.assertIn("RoleBinding YAML 예시도 보여줘", suggestions)
        self.assertIn("권한이 잘 들어갔는지 확인하는 명령도 알려줘", suggestions)

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

    def test_viewer_path_maps_to_local_raw_html(self) -> None:
        target = _viewer_path_to_local_html(
            ROOT,
            "/docs/ocp/4.20/ko/architecture/index.html#overview",
        )

        self.assertIsNotNone(target)
        self.assertEqual("architecture.html", target.name)

    def test_internal_viewer_html_uses_normalized_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            normalized_docs_path = root / "artifacts" / "part1" / "normalized_docs.jsonl"
            normalized_docs_path.parent.mkdir(parents=True)
            normalized_docs_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "book_slug": "architecture",
                                "book_title": "아키텍처",
                                "heading": "개요",
                                "section_level": 1,
                                "section_path": ["개요"],
                                "anchor": "overview",
                                "source_url": "https://example.com/architecture",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                                "text": "OpenShift 아키텍처는 `컨트롤 플레인`과 작업자 노드로 구성됩니다.\n\n[CODE]\noc get nodes\n[/CODE]",
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "book_slug": "architecture",
                                "book_title": "아키텍처",
                                "heading": "컨트롤 플레인",
                                "section_level": 2,
                                "section_path": ["개요", "컨트롤 플레인"],
                                "anchor": "control-plane",
                                "source_url": "https://example.com/architecture",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#control-plane",
                                "text": "API 서버와 스케줄러가 핵심 역할을 담당합니다.",
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            old_artifacts = os.environ.get("ARTIFACTS_DIR")
            old_raw = os.environ.get("RAW_HTML_DIR")
            try:
                os.environ.pop("ARTIFACTS_DIR", None)
                os.environ.pop("RAW_HTML_DIR", None)
                html = _internal_viewer_html(
                    root,
                    "/docs/ocp/4.20/ko/architecture/index.html#overview",
                )
            finally:
                if old_artifacts is None:
                    os.environ.pop("ARTIFACTS_DIR", None)
                else:
                    os.environ["ARTIFACTS_DIR"] = old_artifacts
                if old_raw is None:
                    os.environ.pop("RAW_HTML_DIR", None)
                else:
                    os.environ["RAW_HTML_DIR"] = old_raw

        self.assertIsNotNone(html)
        self.assertIn("아키텍처", html)
        self.assertIn("Internal Citation Viewer", html)
        self.assertIn("section-card is-target", html)
        self.assertIn("OpenShift 아키텍처는 <code>컨트롤 플레인</code>과 작업자 노드로 구성됩니다.", html)
        self.assertIn('class="code-block"', html)
        self.assertIn("oc get nodes", html)
        self.assertIn(">복사<", html)
        self.assertNotIn("[CODE]", html)


if __name__ == "__main__":
    unittest.main()
