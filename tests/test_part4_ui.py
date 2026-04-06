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

from ocp_rag.retrieval.models import ProcedureMemory, SessionContext
from ocp_rag.answering.models import AnswerResult, Citation
from ocp_rag.app.server import (
    _build_library_payload,
    _citation_href,
    _derive_next_context,
    _internal_viewer_html,
    _override_answer_with_command_template_follow_up,
    _override_answer_with_procedure_follow_up,
    _viewer_path_to_local_html,
)


def _citation(
    index: int,
    *,
    anchor: str = "overview",
    section: str = "Architecture overview",
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
        excerpt="OpenShift architecture overview excerpt.",
    )


class Part4UiTests(unittest.TestCase):
    def test_static_ui_contains_workspace_contract(self) -> None:
        html = (ROOT / "src" / "ocp_rag" / "app" / "static" / "index.html").read_text(
            encoding="utf-8"
        )

        self.assertIn("function bootstrapPlatformLayout", html)
        self.assertIn("event.isComposing || event.keyCode === 229 || state.isComposing", html)
        self.assertIn('elements.composer.addEventListener("compositionstart"', html)
        self.assertIn('elements.composer.addEventListener("compositionend"', html)
        self.assertIn("/api/chat/stream", html)
        self.assertIn("function consumeChatStream", html)
        self.assertIn("function startStatusPulse", html)
        self.assertIn("function renderMarkdownInto", html)
        self.assertIn("navigator.clipboard.writeText", html)
        self.assertIn('id="workspace-mode"', html)
        self.assertIn('id="workspace-topic"', html)
        self.assertIn('id="workspace-response-kind"', html)
        self.assertIn('id="workspace-citation-count"', html)
        self.assertIn('id="workspace-stage"', html)
        self.assertIn('id="workspace-stage-detail"', html)
        self.assertIn('id="procedure-panel"', html)
        self.assertIn('id="document-frame"', html)
        self.assertIn('id="library-panel"', html)
        self.assertIn('id="library-search"', html)
        self.assertIn('id="library-status"', html)
        self.assertIn('id="library-list"', html)
        self.assertIn('id="source-list"', html)
        self.assertIn('id="pipeline-trace"', html)
        self.assertIn('id="pipeline-summary"', html)
        self.assertIn("/api/library", html)
        self.assertIn("function loadLibrary", html)
        self.assertIn("function renderLibraryRail", html)
        self.assertIn("function openLibraryItemInPanel", html)
        self.assertIn("function citationOrigin", html)
        self.assertIn("replayed citation", html)
        self.assertIn("source-origin-tag", html)
        self.assertIn("function renderSourcesPanel", html)
        self.assertIn("function openCitationInPanel", html)
        self.assertIn("function renderProcedurePanel", html)
        self.assertIn("function renderSearchMetrics", html)
        self.assertIn("function collectSourceTags", html)
        self.assertIn("pipelineTrace.selection && pipelineTrace.selection.selected_hits", html)
        self.assertIn("총 citation ", html)
        self.assertIn("세션 절차 메모", html)
        self.assertIn("이 패널은 검색된 절차 원문이 아니라 세션에서 유지되는 절차 상태입니다.", html)
        self.assertIn("elements.documentFrame.src = citation.href || citation.source_url || \"\"", html)
        self.assertIn("retrieved excerpt", html)

    def test_citation_href_prefers_internal_viewer_path(self) -> None:
        href = _citation_href(_citation(1, anchor="overview-anchor"))
        self.assertEqual("/docs/ocp/4.20/ko/architecture/index.html#overview", href)

    def test_derive_next_context_updates_topic_when_grounded(self) -> None:
        result = AnswerResult(
            query="What is OpenShift architecture?",
            mode="learn",
            answer="Answer: OpenShift architecture overview [1]",
            rewritten_query="What is OpenShift architecture?",
            citations=[_citation(1)],
            cited_indices=[1],
        )

        updated = _derive_next_context(
            SessionContext(mode="learn", current_topic="legacy", ocp_version="4.20"),
            query="What is OpenShift architecture?",
            mode="learn",
            result=result,
        )

        self.assertEqual("learn", updated.mode)
        self.assertTrue((updated.current_topic or "").startswith("OpenShift"))
        self.assertIsNone(updated.unresolved_question)
        self.assertIsNotNone(updated.active_citation_group)
        assert updated.active_citation_group is not None
        self.assertEqual(1, len(updated.active_citation_group.citations))
        self.assertEqual("architecture", updated.active_citation_group.citations[0].book_slug)
        self.assertEqual(1, len(updated.citation_groups))

    def test_derive_next_context_keeps_branch_order_for_multiple_topics(self) -> None:
        first = _derive_next_context(
            SessionContext(mode="learn", ocp_version="4.20"),
            query="What is OpenShift architecture?",
            mode="learn",
            result=AnswerResult(
                query="What is OpenShift architecture?",
                mode="learn",
                answer="Answer: OpenShift architecture overview [1]",
                rewritten_query="What is OpenShift architecture?",
                citations=[_citation(1, book_slug="architecture", section="Architecture overview")],
                cited_indices=[1],
            ),
        )
        second = _derive_next_context(
            first,
            query="Grant admin in one namespace with rolebinding",
            mode="ops",
            result=AnswerResult(
                query="Grant admin in one namespace with rolebinding",
                mode="ops",
                answer="Answer: Use a RoleBinding [1]",
                rewritten_query="Grant admin in one namespace with rolebinding",
                citations=[
                    _citation(
                        1,
                        book_slug="authentication_and_authorization",
                        section="RoleBinding",
                    )
                ],
                cited_indices=[1],
            ),
        )

        self.assertEqual(2, len(second.citation_groups))
        self.assertEqual("architecture", second.citation_groups[0].citations[0].book_slug)
        self.assertEqual("authentication_and_authorization", second.citation_groups[1].citations[0].book_slug)
        self.assertEqual("authentication_and_authorization", second.active_citation_group.citations[0].book_slug)

    def test_derive_next_context_builds_procedure_memory(self) -> None:
        result = AnswerResult(
            query="Grant admin in one namespace with rolebinding",
            mode="ops",
            answer=(
                "Answer: Use a RoleBinding for namespace-scoped admin.\n\n"
                "1. Create the binding\n"
                "```bash\noc adm policy add-role-to-user admin alice -n joe\n```\n\n"
                "2. Verify the binding\n"
                "```bash\noc describe rolebinding -n joe\n```"
            ),
            rewritten_query="Grant admin in one namespace with rolebinding",
            citations=[
                _citation(
                    1,
                    book_slug="authentication_and_authorization",
                    section="RoleBinding",
                )
            ],
            cited_indices=[1],
        )

        updated = _derive_next_context(
            SessionContext(mode="ops", current_topic="OpenShift", ocp_version="4.20"),
            query="Grant admin in one namespace with rolebinding",
            mode="ops",
            result=result,
        )

        self.assertEqual("RBAC", updated.current_topic)
        self.assertIsNotNone(updated.procedure_memory)
        assert updated.procedure_memory is not None
        self.assertEqual(2, len(updated.procedure_memory.steps))
        self.assertEqual(0, updated.procedure_memory.active_step_index)
        self.assertEqual(
            "oc adm policy add-role-to-user admin alice -n joe",
            updated.procedure_memory.command_for(0),
        )
        self.assertEqual(
            "oc describe rolebinding -n joe",
            updated.procedure_memory.command_for(1),
        )
        self.assertIsNotNone(updated.procedure_memory.command_template_for(0))
        self.assertIsNotNone(updated.procedure_memory.command_template_for(1))
        self.assertEqual(2, len(updated.recent_command_templates))

    def test_override_answer_with_command_template_follow_up_clarifies_unsafe_kind_change(self) -> None:
        result = AnswerResult(
            query="serviceaccount 기준으로 다시",
            mode="ops",
            answer="Answer: generic follow-up",
            rewritten_query="serviceaccount 기준으로 다시",
            citations=[_citation(1)],
            cited_indices=[1],
        )

        context = _derive_next_context(
            SessionContext(mode="ops", current_topic="RBAC", ocp_version="4.20"),
            query="Grant admin in one namespace with rolebinding",
            mode="ops",
            result=AnswerResult(
                query="Grant admin in one namespace with rolebinding",
                mode="ops",
                answer=(
                    "Answer: Use a RoleBinding for namespace-scoped admin.\n\n"
                    "1. Create the binding\n"
                    "```bash\noc adm policy add-role-to-user admin alice -n joe\n```\n\n"
                    "2. Verify the binding\n"
                    "```bash\noc describe rolebinding -n joe\n```"
                ),
                rewritten_query="Grant admin in one namespace with rolebinding",
                citations=[_citation(1)],
                cited_indices=[1],
            ),
        )

        updated = _override_answer_with_command_template_follow_up(
            query="serviceaccount 기준으로 다시",
            context=context,
            result=result,
        )

        self.assertIn("user/group/serviceaccount", updated.answer)
        self.assertNotIn("add-role-to-serviceaccount", updated.answer)

    def test_override_answer_with_procedure_follow_up_prefers_requested_step(self) -> None:
        result = AnswerResult(
            query="2번만 더 자세히",
            mode="ops",
            answer="Answer: generic follow-up",
            rewritten_query="2번만 더 자세히",
            citations=[_citation(1)],
            cited_indices=[1],
        )

        updated = _override_answer_with_procedure_follow_up(
            query="2번만 더 자세히",
            context=SessionContext(
                mode="ops",
                procedure_memory=ProcedureMemory(
                    goal="namespace admin role",
                    steps=["Create binding", "Verify binding"],
                    active_step_index=0,
                    step_commands=[
                        "oc adm policy add-role-to-user admin alice -n joe",
                        "oc describe rolebinding -n joe",
                    ],
                ),
            ),
            result=result,
        )

        self.assertIn("2번 단계는 Verify binding입니다.", updated.answer)
        self.assertIn("oc describe rolebinding -n joe", updated.answer)
        self.assertNotIn("oc adm policy add-role-to-user admin alice -n joe", updated.answer)

    def test_viewer_path_maps_to_local_raw_html(self) -> None:
        target = _viewer_path_to_local_html(
            ROOT,
            "/docs/ocp/4.20/ko/architecture/index.html#overview",
        )

        self.assertIsNotNone(target)
        assert target is not None
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
                                "book_title": "Architecture",
                                "heading": "Overview",
                                "section_level": 1,
                                "section_path": ["Overview"],
                                "anchor": "overview",
                                "source_url": "https://example.com/architecture",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                                "text": "OpenShift architecture overview.\n\n[CODE]\noc get nodes\n[/CODE]",
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "book_slug": "architecture",
                                "book_title": "Architecture",
                                "heading": "Control plane",
                                "section_level": 2,
                                "section_path": ["Overview", "Control plane"],
                                "anchor": "control-plane",
                                "source_url": "https://example.com/architecture",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#control-plane",
                                "text": "API server and controllers live here.",
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
        assert html is not None
        self.assertIn("Architecture", html)
        self.assertIn("Internal Citation Viewer", html)
        self.assertIn("section-card is-target", html)
        self.assertIn("oc get nodes", html)
        self.assertNotIn("[CODE]", html)

    def test_build_library_payload_groups_books_from_normalized_docs(self) -> None:
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
                                "book_title": "Architecture",
                                "heading": "Overview",
                                "source_url": "https://example.com/architecture",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                                "text": "Architecture overview body.",
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "book_slug": "architecture",
                                "book_title": "Architecture",
                                "heading": "Control plane",
                                "source_url": "https://example.com/architecture",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#control-plane",
                                "text": "Control plane body.",
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "book_slug": "nodes",
                                "book_title": "Nodes",
                                "heading": "Node maintenance",
                                "source_url": "https://example.com/nodes",
                                "viewer_path": "/docs/ocp/4.20/ko/nodes/index.html#node-maintenance",
                                "text": "Node maintenance body.",
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
                payload = _build_library_payload(root)
                architecture = next(
                    item for item in payload["items"] if item["book_slug"] == "architecture"
                )
                viewer_html = _internal_viewer_html(root, architecture["viewer_path"])
            finally:
                if old_artifacts is None:
                    os.environ.pop("ARTIFACTS_DIR", None)
                else:
                    os.environ["ARTIFACTS_DIR"] = old_artifacts
                if old_raw is None:
                    os.environ.pop("RAW_HTML_DIR", None)
                else:
                    os.environ["RAW_HTML_DIR"] = old_raw

        self.assertTrue(payload["available"])
        self.assertEqual(2, payload["total_books"])
        self.assertEqual(3, payload["total_sections"])
        self.assertEqual("Architecture", architecture["book_title"])
        self.assertEqual(2, architecture["section_count"])
        self.assertEqual("/docs/ocp/4.20/ko/architecture/index.html", architecture["viewer_path"])
        self.assertLessEqual(len(architecture["sample_sections"]), 3)
        self.assertIn("Overview", architecture["sample_sections"])
        self.assertIsNotNone(viewer_html)

    def test_build_library_payload_handles_missing_normalized_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            old_artifacts = os.environ.get("ARTIFACTS_DIR")
            old_raw = os.environ.get("RAW_HTML_DIR")
            try:
                os.environ.pop("ARTIFACTS_DIR", None)
                os.environ.pop("RAW_HTML_DIR", None)
                payload = _build_library_payload(root)
            finally:
                if old_artifacts is None:
                    os.environ.pop("ARTIFACTS_DIR", None)
                else:
                    os.environ["ARTIFACTS_DIR"] = old_artifacts
                if old_raw is None:
                    os.environ.pop("RAW_HTML_DIR", None)
                else:
                    os.environ["RAW_HTML_DIR"] = old_raw

        self.assertFalse(payload["available"])
        self.assertEqual([], payload["items"])
        self.assertEqual(0, payload["total_books"])
        self.assertEqual(0, payload["total_sections"])


if __name__ == "__main__":
    unittest.main()
