from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part2.models import SessionContext
from ocp_rag_part3.models import AnswerResult, Citation
from ocp_rag_part4.server import (
    _build_doc_to_book_plan,
    _capture_doc_to_book_draft,
    _canonical_source_book,
    _clean_source_view_text,
    _create_doc_to_book_draft,
    _citation_href,
    _doc_to_book_meta_for_viewer_path,
    _derive_next_context,
    _internal_doc_to_book_viewer_html,
    _internal_viewer_html,
    _list_doc_to_book_drafts,
    _load_doc_to_book_book,
    _load_doc_to_book_capture,
    _load_doc_to_book_draft,
    _normalize_doc_to_book_draft,
    _serialize_citation,
    _suggest_follow_up_questions,
    _upload_doc_to_book_draft,
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
        self.assertIn("OCP PLAY STUDIO", html)
        self.assertIn("<h1>OCP PLAY STUDIO</h1>", html)
        self.assertIn("OCP RAG CHATBOT PLATFORM", html)
        self.assertIn("--accent: #ee0000;", html)
        self.assertIn("width: calc(100vw - 12px);", html)
        self.assertIn("grid-template-columns: 0 minmax(0, 1.28fr) minmax(620px, 1.04fr);", html)
        self.assertIn("function syncViewportLayout()", html)
        self.assertIn("function renderEmptyState", html)
        self.assertIn('class="sample-chip"', html)
        self.assertIn("function normalizeAssistantAnswer", html)
        self.assertIn('label.textContent = "Answer"', html)
        self.assertIn('title.textContent = "근거 문서"', html)
        self.assertIn(".assistant-copy", html)
        self.assertIn(".citation-list-title", html)
        self.assertIn(".suggestion-list-title", html)
        self.assertIn(".followup-chip", html)
        self.assertIn('title.textContent = "이어서 볼 질문"', html)
        self.assertIn('sendMessage({ query: suggestedQuery })', html)
        self.assertIn('id="source-panel-toggle-btn"', html)
        self.assertIn("function setSourcePanelVisible", html)
        self.assertIn("function setStudyTab", html)
        self.assertIn('data-study-tab="source"', html)
        self.assertIn('data-study-tab="library"', html)
        self.assertIn('data-study-page="library"', html)
        self.assertIn('id="library-summary"', html)
        self.assertIn('id="library-list"', html)
        self.assertIn('id="library-detail"', html)
        self.assertIn('id="ingest-dropzone"', html)
        self.assertIn('id="ingest-file-btn"', html)
        self.assertIn('id="ingest-file-input"', html)
        self.assertIn('id="ingest-file-pill"', html)
        self.assertIn("function fetchSourceMeta", html)
        self.assertIn("function fetchSourceBook", html)
        self.assertIn("function renderDocToBookLibrary", html)
        self.assertIn("function renderLibraryDetail", html)
        self.assertIn("function openLibraryTrace", html)
        self.assertIn("function openLibraryAsset", html)
        self.assertIn("function humanizeSourceCollection", html)
        self.assertIn("function formatInferredScope", html)
        self.assertIn("function qualityStatusLabel", html)
        self.assertIn("function isReviewNeeded", html)
        self.assertIn("function uploadDocToBookFile", html)
        self.assertIn("function handleIngestFileSelection", html)
        self.assertIn("function syncIngestUploadHint", html)
        self.assertIn("function renderSourceBook", html)
        self.assertIn("function openSourcePanel", html)
        self.assertIn('id="source-viewer-frame"', html)
        self.assertIn('id="source-outline"', html)
        self.assertIn('data-study-tab="ingest"', html)
        self.assertIn('id="ingest-plan-btn"', html)
        self.assertIn('id="ingest-save-btn"', html)
        self.assertIn('id="ingest-capture-btn"', html)
        self.assertIn('id="ingest-normalize-btn"', html)
        self.assertIn('id="ingest-open-capture-btn"', html)
        self.assertIn('id="ingest-capture-meta"', html)
        self.assertIn("function previewDocToBookPlan", html)
        self.assertIn("function createDocToBookDraft", html)
        self.assertIn("function captureDocToBookDraft", html)
        self.assertIn("function normalizeDocToBookDraft", html)
        self.assertIn("function fetchDocToBookBook", html)
        self.assertIn("function openCapturedDocToBookDraft", html)
        self.assertIn("function loadDocToBookDrafts", html)
        self.assertIn("function openDocToBookDraft", html)
        self.assertIn(".source-tag-group", html)
        self.assertIn(".source-tag", html)
        self.assertIn(".summary-grid", html)
        self.assertIn("function humanizePipelineKey", html)
        self.assertIn("function summarizeTraceMeta", html)
        self.assertIn(".trace-step", html)
        self.assertIn('class="summary-grid"', html)
        self.assertIn("Capture Status", html)
        self.assertIn("Knowledge Library", html)
        self.assertIn("Ready Sources", html)
        self.assertIn("Canonical Draft Preview", html)
        self.assertIn("Recent Drafts", html)

    def test_citation_href_prefers_internal_viewer_path(self) -> None:
        href = _citation_href(_citation(1, anchor="overview-anchor"))

        self.assertEqual(
            "/docs/ocp/4.20/ko/architecture/index.html#overview",
            href,
        )

    def test_clean_source_view_text_strips_notice_noise(self) -> None:
        cleaned = _clean_source_view_text(
            "Red Hat OpenShift Documentation Team 법적 공지 초록\n\n목차\n\n정상 본문입니다."
        )

        self.assertEqual("정상 본문입니다.", cleaned)

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
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            raw_html_dir = root / "custom_raw_html"
            raw_html_dir.mkdir(parents=True)
            expected = raw_html_dir / "architecture.html"
            expected.write_text("<html><body>ok</body></html>", encoding="utf-8")

            old_artifacts = os.environ.get("ARTIFACTS_DIR")
            old_raw = os.environ.get("RAW_HTML_DIR")
            try:
                os.environ.pop("ARTIFACTS_DIR", None)
                os.environ["RAW_HTML_DIR"] = str(raw_html_dir)
                target = _viewer_path_to_local_html(
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

        self.assertEqual(expected.resolve(), target)

    def test_serialize_citation_enriches_source_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "manifests" / "ocp_ko_4_20_html_single.json"
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "book_slug": "architecture",
                                "title": "아키텍처",
                                "source_url": "https://example.com/architecture",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            normalized_docs_path = root / "artifacts" / "part1" / "normalized_docs.jsonl"
            normalized_docs_path.parent.mkdir(parents=True)
            normalized_docs_path.write_text(
                json.dumps(
                    {
                        "book_slug": "architecture",
                        "book_title": "아키텍처",
                        "heading": "컨트롤 플레인",
                        "section_level": 2,
                        "section_path": ["개요", "컨트롤 플레인"],
                        "anchor": "overview",
                        "source_url": "https://example.com/architecture",
                        "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                        "text": "본문",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            old_artifacts = os.environ.get("ARTIFACTS_DIR")
            old_raw = os.environ.get("RAW_HTML_DIR")
            old_manifest = os.environ.get("SOURCE_MANIFEST_PATH")
            try:
                os.environ.pop("ARTIFACTS_DIR", None)
                os.environ.pop("RAW_HTML_DIR", None)
                os.environ.pop("SOURCE_MANIFEST_PATH", None)
                payload = _serialize_citation(root, _citation(1))
            finally:
                if old_artifacts is None:
                    os.environ.pop("ARTIFACTS_DIR", None)
                else:
                    os.environ["ARTIFACTS_DIR"] = old_artifacts
                if old_raw is None:
                    os.environ.pop("RAW_HTML_DIR", None)
                else:
                    os.environ["RAW_HTML_DIR"] = old_raw
                if old_manifest is None:
                    os.environ.pop("SOURCE_MANIFEST_PATH", None)
                else:
                    os.environ["SOURCE_MANIFEST_PATH"] = old_manifest

        self.assertEqual("아키텍처", payload["book_title"])
        self.assertEqual(["개요", "컨트롤 플레인"], payload["section_path"])
        self.assertEqual("개요 > 컨트롤 플레인", payload["section_path_label"])
        self.assertEqual("아키텍처 · 개요 > 컨트롤 플레인", payload["source_label"])
        self.assertEqual("core", payload["source_collection"])
        self.assertEqual("openshift-4-20-core", payload["pack_id"])
        self.assertEqual("OpenShift 4.20 Core Pack", payload["pack_label"])
        self.assertEqual("openshift", payload["inferred_product"])
        self.assertEqual("4.20", payload["inferred_version"])

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
                                "text": "Red Hat OpenShift Documentation Team 법적 공지 초록\n\nOpenShift 아키텍처는 `컨트롤 플레인`과 작업자 노드로 구성됩니다.\n\n[CODE]\noc get nodes\n[/CODE]",
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
        self.assertIn("width: min(1480px, calc(100vw - 32px));", html)
        self.assertIn("section-card is-target", html)
        self.assertIn(".code-block code {", html)
        self.assertIn("background: transparent;", html)
        self.assertIn("OpenShift 아키텍처는 <code>컨트롤 플레인</code>과 작업자 노드로 구성됩니다.", html)
        self.assertIn('class="code-block"', html)
        self.assertIn("oc get nodes", html)
        self.assertIn(">복사<", html)
        self.assertNotIn("[CODE]", html)
        self.assertNotIn("Red Hat OpenShift Documentation Team", html)

    def test_canonical_source_book_projects_normalized_sections(self) -> None:
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
                                "text": "설명 본문\n\n[CODE]\noc get nodes\n[/CODE]",
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
                                "text": "구성 요소 설명",
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            payload = _canonical_source_book(
                root,
                "/docs/ocp/4.20/ko/architecture/index.html#control-plane",
            )

        self.assertIsNotNone(payload)
        assert payload is not None
        self.assertEqual("canonical_book_v1", payload["canonical_model"])
        self.assertEqual("architecture", payload["book_slug"])
        self.assertEqual("core", payload["source_collection"])
        self.assertEqual("openshift-4-20-core", payload["pack_id"])
        self.assertEqual("OpenShift 4.20 Core Pack", payload["pack_label"])
        self.assertEqual("openshift", payload["inferred_product"])
        self.assertEqual("4.20", payload["inferred_version"])
        self.assertEqual("control-plane", payload["target_anchor"])
        self.assertEqual("normalized_sections_v1", payload["source_view_strategy"])
        self.assertEqual(2, len(payload["sections"]))
        self.assertEqual("architecture:overview", payload["sections"][0]["section_key"])
        self.assertEqual(["paragraph", "code"], payload["sections"][0]["block_kinds"])
        self.assertEqual("개요 > 컨트롤 플레인", payload["sections"][1]["section_path_label"])

    def test_build_doc_to_book_plan_returns_resolved_web_capture(self) -> None:
        payload = _build_doc_to_book_plan(
            {
                "source_type": "web",
                "uri": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/nodes",
                "title": "노드",
            }
        )

        self.assertEqual("web", payload["source_type"])
        self.assertEqual("uploaded", payload["source_collection"])
        self.assertEqual("openshift-4-20-custom", payload["pack_id"])
        self.assertEqual("OpenShift 4.20 Custom Pack", payload["pack_label"])
        self.assertEqual("openshift", payload["inferred_product"])
        self.assertEqual("4.20", payload["inferred_version"])
        self.assertEqual("docs_redhat_html_single_v1", payload["capture_strategy"])
        self.assertEqual(
            "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/nodes/index",
            payload["acquisition_uri"],
        )

    def test_build_doc_to_book_plan_rejects_unknown_source_type(self) -> None:
        with self.assertRaisesRegex(ValueError, "source_type은 web 또는 pdf여야 합니다."):
            _build_doc_to_book_plan({"source_type": "docx", "uri": "/tmp/a.docx"})

    def test_create_doc_to_book_draft_persists_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            created = _create_doc_to_book_draft(
                root,
                {
                    "source_type": "web",
                    "uri": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/nodes",
                    "title": "노드 운영 가이드",
                },
            )
            loaded = _load_doc_to_book_draft(root, str(created["draft_id"]))

        self.assertEqual("planned", created["status"])
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(created["draft_id"], loaded["draft_id"])
        self.assertEqual("노드 운영 가이드", loaded["plan"]["title"])
        self.assertEqual("uploaded", loaded["source_collection"])
        self.assertEqual("OpenShift 4.20 Custom Pack", loaded["pack_label"])
        self.assertEqual("4.20", loaded["inferred_version"])
        self.assertEqual(
            "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/nodes/index",
            loaded["plan"]["acquisition_uri"],
        )

    def test_upload_doc_to_book_draft_persists_uploaded_pdf_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            created = _upload_doc_to_book_draft(
                root,
                {
                    "source_type": "pdf",
                    "uri": "guide.pdf",
                    "title": "업로드 가이드",
                    "file_name": "guide.pdf",
                    "content_base64": "JVBERi0xLjQgc2FtcGxl",
                },
            )
            uploaded_path = Path(str(created["uploaded_file_path"]))
            loaded = _load_doc_to_book_draft(root, str(created["draft_id"]))
            uploaded_bytes = uploaded_path.read_bytes()

        self.assertEqual("pdf", created["request"]["source_type"])
        self.assertEqual("업로드 가이드", created["plan"]["title"])
        self.assertIsNotNone(loaded)
        self.assertEqual(str(uploaded_path), loaded["request"]["uri"])
        self.assertEqual("guide.pdf", loaded["uploaded_file_name"])
        self.assertEqual(str(uploaded_path), loaded["uploaded_file_path"])
        self.assertEqual(b"%PDF-1.4 sample", uploaded_bytes)

    def test_list_doc_to_book_drafts_returns_saved_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _create_doc_to_book_draft(
                root,
                {
                    "source_type": "pdf",
                    "uri": "/tmp/openshift-troubleshooting.pdf",
                    "title": "트러블슈팅 핸드북",
                },
            )
            payload = _list_doc_to_book_drafts(root)

        self.assertEqual(1, len(payload["drafts"]))
        self.assertEqual("트러블슈팅 핸드북", payload["drafts"][0]["title"])
        self.assertEqual("pdf_text_extract_v1", payload["drafts"][0]["capture_strategy"])

    def test_capture_doc_to_book_draft_fetches_and_serves_web_artifact(self) -> None:
        class _FakeResponse:
            encoding = "utf-8"
            apparent_encoding = "utf-8"
            text = "<html><body>captured web source</body></html>"

            def raise_for_status(self) -> None:
                return None

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            with patch("ocp_rag_part1.collector.requests.get", return_value=_FakeResponse()):
                created = _capture_doc_to_book_draft(
                    root,
                    {
                        "source_type": "web",
                        "uri": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/nodes",
                        "title": "노드 운영 가이드",
                    },
                )
            served = _load_doc_to_book_capture(root, str(created["draft_id"]))

        self.assertEqual("captured", created["status"])
        self.assertIsNotNone(served)
        assert served is not None
        body, content_type = served
        self.assertEqual("text/html; charset=utf-8", content_type)
        self.assertIn("captured web source", body.decode("utf-8"))

    def test_normalize_doc_to_book_draft_builds_internal_study_view(self) -> None:
        class _FakeResponse:
            encoding = "utf-8"
            apparent_encoding = "utf-8"
            text = """
            <html>
              <body>
                <main id="main-content">
                  <article>
                    <h1>노드 운영</h1>
                    <p>개요 설명입니다.</p>
                    <h2 id="events">이벤트 확인</h2>
                    <p>문제를 좁혀가는 절차를 설명합니다.</p>
                  </article>
                </main>
              </body>
            </html>
            """

            def raise_for_status(self) -> None:
                return None

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            with patch("ocp_rag_part1.collector.requests.get", return_value=_FakeResponse()):
                captured = _capture_doc_to_book_draft(
                    root,
                    {
                        "source_type": "web",
                        "uri": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/nodes",
                        "title": "노드 운영 가이드",
                    },
                )
            normalized = _normalize_doc_to_book_draft(root, {"draft_id": str(captured["draft_id"])})
            book = _load_doc_to_book_book(root, str(captured["draft_id"]))
            viewer_html = _internal_doc_to_book_viewer_html(
                root,
                f"/docs/intake/{captured['draft_id']}/index.html#events",
            )

        self.assertEqual("normalized", normalized["status"])
        self.assertIsNotNone(book)
        assert book is not None
        self.assertEqual(str(captured["draft_id"]), book["draft_id"])
        self.assertEqual(2, len(book["sections"]))
        self.assertEqual("events", book["sections"][1]["anchor"])
        self.assertIn("/docs/intake/", book["target_viewer_path"])
        self.assertEqual(f"/api/doc-to-book/captured?draft_id={captured['draft_id']}", book["source_origin_url"])
        self.assertEqual("ready", book["quality_status"])
        self.assertIsNotNone(viewer_html)
        assert viewer_html is not None
        self.assertIn("Doc-to-Book Study Viewer", viewer_html)
        self.assertIn("이벤트 확인", viewer_html)

    def test_doc_to_book_meta_prefers_captured_source_url_and_quality(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            draft_dir = root / "artifacts" / "doc_to_book" / "drafts"
            book_dir = root / "artifacts" / "doc_to_book" / "books"
            draft_dir.mkdir(parents=True)
            book_dir.mkdir(parents=True)

            (draft_dir / "dtb-review.json").write_text(
                json.dumps(
                    {
                        "draft_id": "dtb-review",
                        "status": "normalized",
                        "created_at": "2026-04-06T00:00:00Z",
                        "updated_at": "2026-04-06T00:00:00Z",
                        "request": {
                            "source_type": "pdf",
                            "uri": "/tmp/demo.pdf",
                            "title": "데모 PDF",
                            "language_hint": "ko",
                        },
                        "plan": {
                            "book_slug": "demo-pdf",
                            "title": "데모 PDF",
                            "source_type": "pdf",
                            "source_uri": "/tmp/demo.pdf",
                            "source_collection": "uploaded",
                            "pack_id": "openshift-4-16-custom",
                            "pack_label": "OpenShift 4.16 Custom Pack",
                            "inferred_product": "openshift",
                            "inferred_version": "4.16",
                            "acquisition_uri": "/tmp/demo.pdf",
                            "capture_strategy": "pdf_text_extract_v1",
                            "acquisition_step": "capture",
                            "normalization_step": "normalize",
                            "derivation_step": "derive",
                            "notes": [],
                            "canonical_model": "canonical_book_v1",
                            "source_view_strategy": "source_view_first",
                            "retrieval_derivation": "chunks_from_canonical_sections",
                        },
                        "capture_artifact_path": "/tmp/demo.pdf",
                        "capture_content_type": "application/pdf",
                        "capture_byte_size": 12,
                        "capture_error": "",
                        "canonical_book_path": str(book_dir / "dtb-review.json"),
                        "normalized_section_count": 3,
                        "normalize_error": "",
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )
            (book_dir / "dtb-review.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "canonical_book_v1",
                        "book_slug": "demo-pdf",
                        "title": "데모 PDF",
                        "source_type": "pdf",
                        "source_uri": "/tmp/demo.pdf",
                        "language_hint": "ko",
                        "source_view_strategy": "normalized_sections_v1",
                        "retrieval_derivation": "chunks_from_canonical_sections",
                        "sections": [
                            {
                                "ordinal": 1,
                                "section_key": "demo-pdf:page-summary",
                                "heading": "Page Summary",
                                "section_level": 1,
                                "section_path": ["Page 1", "Page Summary"],
                                "section_path_label": "Page 1 > Page Summary",
                                "anchor": "page-summary",
                                "viewer_path": "/docs/intake/dtb-review/index.html#page-summary",
                                "source_url": "/tmp/demo.pdf",
                                "text": "Page Summary",
                                "block_kinds": ["paragraph"],
                            },
                            {
                                "ordinal": 2,
                                "section_key": "demo-pdf:short-a",
                                "heading": "온프레미스",
                                "section_level": 1,
                                "section_path": ["Page 1", "온프레미스"],
                                "section_path_label": "Page 1 > 온프레미스",
                                "anchor": "short-a",
                                "viewer_path": "/docs/intake/dtb-review/index.html#short-a",
                                "source_url": "/tmp/demo.pdf",
                                "text": "온프레미스",
                                "block_kinds": ["paragraph"],
                            },
                            {
                                "ordinal": 3,
                                "section_key": "demo-pdf:short-b",
                                "heading": "설치",
                                "section_level": 1,
                                "section_path": ["Page 1", "설치"],
                                "section_path_label": "Page 1 > 설치",
                                "anchor": "short-b",
                                "viewer_path": "/docs/intake/dtb-review/index.html#short-b",
                                "source_url": "/tmp/demo.pdf",
                                "text": "설치",
                                "block_kinds": ["paragraph"],
                            },
                        ],
                        "notes": [],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            meta = _doc_to_book_meta_for_viewer_path(root, "/docs/intake/dtb-review/index.html#short-a")

        self.assertIsNotNone(meta)
        assert meta is not None
        self.assertEqual("/api/doc-to-book/captured?draft_id=dtb-review", meta["source_url"])
        self.assertEqual("review", meta["quality_status"])
        self.assertIn("정규화 품질 검토", meta["quality_summary"])

    def test_serialize_citation_enriches_doc_to_book_source_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            draft_dir = root / "artifacts" / "doc_to_book" / "drafts"
            book_dir = root / "artifacts" / "doc_to_book" / "books"
            draft_dir.mkdir(parents=True)
            book_dir.mkdir(parents=True)

            draft_payload = {
                "draft_id": "dtb-demo",
                "status": "normalized",
                "created_at": "2026-04-06T00:00:00Z",
                "updated_at": "2026-04-06T00:00:00Z",
                "request": {
                    "source_type": "web",
                    "uri": "https://example.com/demo",
                    "title": "데모 가이드",
                    "language_hint": "ko",
                },
                "plan": {
                    "book_slug": "demo-guide",
                    "title": "데모 가이드",
                    "source_type": "web",
                    "source_uri": "https://example.com/demo",
                    "acquisition_uri": "https://example.com/demo",
                    "capture_strategy": "docs_redhat_html_single_v1",
                    "acquisition_step": "capture",
                    "normalization_step": "normalize",
                    "derivation_step": "derive",
                    "notes": [],
                    "canonical_model": "canonical_book_v1",
                    "source_view_strategy": "source_view_first",
                    "retrieval_derivation": "chunks_from_canonical_sections",
                },
                "capture_artifact_path": "",
                "capture_content_type": "",
                "capture_byte_size": 0,
                "capture_error": "",
                "canonical_book_path": str(book_dir / "dtb-demo.json"),
                "normalized_section_count": 1,
                "normalize_error": "",
            }
            (draft_dir / "dtb-demo.json").write_text(
                json.dumps(draft_payload, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            (book_dir / "dtb-demo.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "canonical_book_v1",
                        "book_slug": "demo-guide",
                        "title": "데모 가이드",
                        "source_type": "web",
                        "source_uri": "https://example.com/demo",
                        "language_hint": "ko",
                        "source_view_strategy": "normalized_sections_v1",
                        "retrieval_derivation": "chunks_from_canonical_sections",
                        "sections": [
                            {
                                "ordinal": 1,
                                "section_key": "demo-guide:events",
                                "heading": "이벤트 확인",
                                "section_level": 2,
                                "section_path": ["문제 해결", "이벤트 확인"],
                                "section_path_label": "문제 해결 > 이벤트 확인",
                                "anchor": "events",
                                "viewer_path": "/docs/intake/dtb-demo/index.html#events",
                                "source_url": "https://example.com/demo",
                                "text": "이벤트 확인 절차",
                                "block_kinds": ["paragraph"],
                            }
                        ],
                        "notes": [],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            payload = _serialize_citation(
                root,
                Citation(
                    index=1,
                    chunk_id="dtb-demo:demo-guide:events",
                    book_slug="demo-guide",
                    section="이벤트 확인",
                    anchor="events",
                    source_url="https://example.com/demo",
                    viewer_path="/docs/intake/dtb-demo/index.html#events",
                    excerpt="이벤트 확인 절차",
                ),
            )

        self.assertEqual("데모 가이드", payload["book_title"])
        self.assertEqual("문제 해결 > 이벤트 확인", payload["section_path_label"])
        self.assertEqual("데모 가이드 · 문제 해결 > 이벤트 확인", payload["source_label"])


if __name__ == "__main__":
    unittest.main()
