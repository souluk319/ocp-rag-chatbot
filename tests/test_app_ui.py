from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.retrieval.models import SessionContext
from play_book_studio.answering.models import AnswerResult, Citation
from play_book_studio.app.presenters import _clean_source_view_text
from play_book_studio.app.session_flow import (
    context_with_request_overrides as _context_with_request_overrides,
    derive_next_context as _derive_next_context,
    suggest_follow_up_questions as _suggest_follow_up_questions,
)
from play_book_studio.app.server import (
    ChatSession,
    Turn,
    _build_health_payload,
    _build_turn_diagnosis,
    _build_doc_to_book_plan,
    _build_session_debug_payload,
    _capture_doc_to_book_draft,
    _canonical_source_book,
    _create_doc_to_book_draft,
    _citation_href,
    _doc_to_book_meta_for_viewer_path,
    _internal_doc_to_book_viewer_html,
    _internal_viewer_html,
    _list_doc_to_book_drafts,
    _load_doc_to_book_book,
    _load_doc_to_book_capture,
    _load_doc_to_book_draft,
    _normalize_doc_to_book_draft,
    _append_chat_turn_log,
    _write_recent_chat_session_snapshot,
    _refresh_answerer_llm_settings,
    _serialize_citation,
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
    def test_static_asset_scripts_are_syntax_valid(self) -> None:
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not available")

        asset_dir = ROOT / "src" / "play_book_studio" / "app" / "static" / "assets"
        for script_path in sorted(asset_dir.glob("*.js")):
            completed = subprocess.run(
                [node, "--check", str(script_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                0,
                completed.returncode,
                msg=f"{script_path.name} syntax check failed:\n{completed.stderr}",
            )

    def test_context_with_request_overrides_defaults_to_restrict_uploaded_sources(self) -> None:
        context = _context_with_request_overrides(
            SessionContext(selected_draft_ids=["draft-a"], restrict_uploaded_sources=False),
            payload={},
            mode="ops",
        )

        self.assertTrue(context.restrict_uploaded_sources)
        self.assertEqual(["draft-a"], context.selected_draft_ids)

    def test_refresh_answerer_llm_settings_reloads_endpoint_from_env(self) -> None:
        class _FakeSettings:
            def __init__(self, endpoint: str) -> None:
                self.llm_endpoint = endpoint

        class _FakeLlmClient:
            def __init__(self, settings) -> None:
                self.endpoint = settings.llm_endpoint

        class _FakeAnswerer:
            def __init__(self, endpoint: str) -> None:
                self.settings = _FakeSettings(endpoint)
                self.llm_client = _FakeLlmClient(self.settings)

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "LLM_ENDPOINT=http://10.0.1.201:8010/v1\n"
                "LLM_MODEL=Qwen/Qwen3.5-9B\n",
                encoding="utf-8",
            )
            original_endpoint = os.environ.get("LLM_ENDPOINT")
            original_model = os.environ.get("LLM_MODEL")
            try:
                os.environ["LLM_ENDPOINT"] = "http://old-server:8080/v1"
                os.environ["LLM_MODEL"] = "old-model"
                answerer = _FakeAnswerer("http://old-server:8080/v1")
                refreshed, signature = _refresh_answerer_llm_settings(
                    answerer,
                    root_dir=root,
                    current_signature=("stale",),
                )
                self.assertIs(refreshed, answerer)
                self.assertEqual("http://10.0.1.201:8010/v1", refreshed.settings.llm_endpoint)
                self.assertEqual("http://10.0.1.201:8010/v1", refreshed.llm_client.endpoint)
                self.assertIn("http://10.0.1.201:8010/v1", signature)
            finally:
                if original_endpoint is None:
                    os.environ.pop("LLM_ENDPOINT", None)
                else:
                    os.environ["LLM_ENDPOINT"] = original_endpoint
                if original_model is None:
                    os.environ.pop("LLM_MODEL", None)
                else:
                    os.environ["LLM_MODEL"] = original_model

    def test_build_health_payload_exposes_runtime_snapshot_and_fallback_state(self) -> None:
        class _FakeLlmClient:
            def runtime_metadata(self) -> dict[str, object]:
                return {
                    "preferred_provider": "openai-compatible",
                    "fallback_enabled": True,
                    "last_provider": "openai-compatible",
                    "last_fallback_used": False,
                    "last_attempted_providers": ["openai-compatible"],
                }

        class _FakeAnswerer:
            def __init__(self, settings) -> None:
                self.settings = settings
                self.llm_client = _FakeLlmClient()

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "LLM_ENDPOINT=http://cllm.cywell.co.kr/v1\n"
                "LLM_MODEL=Qwen/Qwen3.5-9B\n"
                "EMBEDDING_BASE_URL=http://tei.cywell.co.kr/v1\n"
                "EMBEDDING_MODEL=dragonkue/bge-m3-ko\n"
                "QDRANT_URL=http://localhost:6333\n"
                "QDRANT_COLLECTION=openshift_docs\n",
                encoding="utf-8",
            )
            from play_book_studio.config.settings import load_settings

            payload = _build_health_payload(_FakeAnswerer(load_settings(root)))
            runtime = payload["runtime"]

            self.assertTrue(payload["ok"])
            self.assertEqual("play-book-studio", runtime["app_id"])
            self.assertEqual("Play Book Studio", runtime["app_label"])
            self.assertEqual("openshift-4-20-core", runtime["active_pack_id"])
            self.assertEqual("OpenShift 4.20", runtime["active_pack_label"])
            self.assertEqual("/docs/ocp/4.20/ko/", runtime["viewer_path_prefix"])
            self.assertEqual("http://cllm.cywell.co.kr/v1", runtime["llm_endpoint"])
            self.assertEqual("Qwen/Qwen3.5-9B", runtime["llm_model"])
            self.assertEqual("openai-compatible", runtime["llm_provider_hint"])
            self.assertTrue(runtime["llm_fallback_enabled"])
            self.assertFalse(runtime["llm_last_fallback_used"])
            self.assertEqual(["openai-compatible"], runtime["llm_attempted_providers"])
            self.assertEqual("remote", runtime["embedding_mode"])
            self.assertEqual("http://tei.cywell.co.kr/v1", runtime["embedding_base_url"])
            self.assertEqual("dragonkue/bge-m3-ko", runtime["embedding_model"])
            self.assertFalse(runtime["reranker_enabled"])
            self.assertEqual("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1", runtime["reranker_model"])
            self.assertEqual(12, runtime["reranker_top_n"])
            self.assertEqual(8, runtime["reranker_batch_size"])
            self.assertEqual("auto", runtime["reranker_device"])
            self.assertEqual("http://localhost:6333", runtime["qdrant_url"])
            self.assertEqual("openshift_docs", runtime["qdrant_collection"])
            self.assertEqual("rebuild_answerer_on_signature_change", runtime["runtime_refresh_strategy"])
            self.assertTrue(runtime["config_fingerprint"])

    def test_static_ui_guards_enter_during_ime_composition(self) -> None:
        html = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "index.html"
        ).read_text(encoding="utf-8")
        app_config = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "assets" / "app-config.js"
        ).read_text(encoding="utf-8")
        app_bootstrap = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "assets" / "app-bootstrap.js"
        ).read_text(encoding="utf-8")
        app_shell_state = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "assets" / "app-shell-state.js"
        ).read_text(encoding="utf-8")
        shell_helpers = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "assets" / "shell-helpers.js"
        ).read_text(encoding="utf-8")
        panel_controller = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "assets" / "panel-controller.js"
        ).read_text(encoding="utf-8")
        chat_renderer = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "assets" / "chat-renderer.js"
        ).read_text(encoding="utf-8")
        message_shells = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "assets" / "message-shells.js"
        ).read_text(encoding="utf-8")
        chat_session = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "assets" / "chat-session.js"
        ).read_text(encoding="utf-8")
        workspace_state = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "assets" / "workspace-state.js"
        ).read_text(encoding="utf-8")
        intake_renderer = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "assets" / "intake-renderer.js"
        ).read_text(encoding="utf-8")
        intake_actions = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "assets" / "intake-actions.js"
        ).read_text(encoding="utf-8")
        diagnostics_renderer = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "assets" / "diagnostics-renderer.js"
        ).read_text(encoding="utf-8")
        source_workflows = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "assets" / "source-workflows.js"
        ).read_text(encoding="utf-8")

        self.assertIn("event.isComposing || event.keyCode === 229 || state.isComposing", chat_session)
        self.assertIn('refs.composerEl.addEventListener("compositionstart"', chat_session)
        self.assertIn('refs.composerEl.addEventListener("compositionend"', chat_session)
        self.assertIn("/api/chat/stream", chat_session)
        self.assertIn('id="pipeline-trace"', html)
        self.assertIn("async function consumeChatStream", chat_session)
        self.assertIn('id="pipeline-summary"', html)
        self.assertIn("Play Book Studio", html)
        self.assertIn("<h1>Play Book Studio</h1>", html)
        self.assertIn('<title>Play Book Studio</title>', html)
        self.assertIn("OpenShift 문서와 추가 자료를 함께 읽는 작업 공간.", html)
        self.assertIn("--accent: #ee0000;", html)
        self.assertIn("--layout-gap: 16px;", html)
        self.assertIn("padding: var(--layout-gap);", html)
        self.assertIn("height: 100dvh;", html)
        self.assertIn("flex: 1 1 auto;", html)
        self.assertIn("grid-template-columns: 0 minmax(0, 1.22fr) minmax(620px, 1.04fr);", html)
        self.assertIn('<script src="/assets/app-config.js"></script>', html)
        self.assertIn('<script src="/assets/app-shell-state.js"></script>', html)
        self.assertIn('<script src="/assets/shell-helpers.js"></script>', html)
        self.assertIn('<script src="/assets/app-bootstrap.js"></script>', html)
        self.assertIn('<script src="/assets/workspace-state.js"></script>', html)
        self.assertIn('<script src="/assets/panel-controller.js"></script>', html)
        self.assertIn('<script src="/assets/chat-renderer.js"></script>', html)
        self.assertIn('<script src="/assets/message-shells.js"></script>', html)
        self.assertIn('<script src="/assets/chat-session.js"></script>', html)
        self.assertIn('<script src="/assets/intake-renderer.js"></script>', html)
        self.assertIn('<script src="/assets/intake-actions.js"></script>', html)
        self.assertIn('<script src="/assets/diagnostics-renderer.js"></script>', html)
        self.assertIn('<script src="/assets/source-workflows.js"></script>', html)
        self.assertIn("window.OCP_PLAY_STUDIO_CONFIG", app_config)
        self.assertIn("window.createAppShellState", app_shell_state)
        self.assertIn('composerSamplesEl: document.getElementById("composer-samples")', app_shell_state)
        self.assertIn("window.createShellHelpers", shell_helpers)
        self.assertIn("window.createAppBootstrap", app_bootstrap)
        self.assertIn("composerSamplesEl: refs.composerSamplesEl", app_bootstrap)
        self.assertIn("window.createPanelController", panel_controller)
        self.assertIn("window.createChatRenderer", chat_renderer)
        self.assertIn("window.createMessageShells", message_shells)
        self.assertIn("window.createChatSession", chat_session)
        self.assertIn("function renderComposerSamples()", chat_session)
        self.assertIn("window.createWorkspaceState", workspace_state)
        self.assertIn("window.createIntakeRenderer", intake_renderer)
        self.assertIn("window.createIntakeActions", intake_actions)
        self.assertIn("window.createDiagnosticsRenderer", diagnostics_renderer)
        self.assertIn("window.createSourceWorkflows", source_workflows)
        self.assertIn("function renderMarkdownInto", chat_renderer)
        self.assertIn("navigator.clipboard.writeText", chat_renderer)
        self.assertIn('copyButton.textContent = "복사"', chat_renderer)
        self.assertIn('version: "4.20"', app_config)
        self.assertIn("Deployment 복제본 조정", app_config)
        self.assertIn("function renderEmptyState", message_shells)
        self.assertIn("function escapeHtml(value)", message_shells)
        self.assertIn("function syncViewportLayout()", shell_helpers)
        self.assertIn("function syncChatPanelState()", shell_helpers)
        self.assertIn("function setIngestBusy(", shell_helpers)
        self.assertIn("function setGenerating(", shell_helpers)
        self.assertIn("function resizeComposer()", shell_helpers)
        self.assertIn("const EMPTY_STATE_SAMPLES = Array.isArray(APP_CONFIG.emptyStateSamples)", html)
        self.assertIn("function shuffledEmptyStateSamples(limit = 4)", message_shells)
        self.assertIn('id="version-chip"', html)
        self.assertIn("자료", html)
        self.assertIn('id="core-version-picker"', html)
        self.assertIn("대화에 넣을 자료", html)
        self.assertIn("대화에 붙일 자료를 고릅니다.", html)
        self.assertIn("무엇이 궁금한가요?", html)
        self.assertIn("근거 문서를 선택하세요", html)
        self.assertIn("자료 추가 대기", html)
        self.assertIn('id="composer-samples"', html)
        self.assertIn("예시 질문", chat_session)
        self.assertIn("OpenShift 공식 문서", html)
        self.assertIn('id="active-pack-title"', html)
        self.assertIn("core-pack-tab", html)
        self.assertIn("function renderCorePackOptions()", workspace_state)
        self.assertIn('data-pack-version="${pack.version}"', workspace_state)
        self.assertIn("function setCorePack(", workspace_state)
        self.assertIn('message || "자료 추가 대기"', workspace_state)
        self.assertIn('class="sample-chip"', message_shells)
        self.assertIn('id="selected-source-count"', html)
        self.assertIn("function setUploadedDraftSelected", workspace_state)
        self.assertIn("function renderDocToBookDrafts", workspace_state)
        self.assertNotIn("selectedDraftIds.add(draftId);", html)
        self.assertNotIn("selectedDraftIds.add(normalized.draft_id);", html)
        self.assertIn("function prepareUploadedSource", intake_actions)
        self.assertIn("selected_draft_ids: helpers.selectedDraftIdList()", chat_session)
        self.assertIn("function normalizeAssistantAnswer", chat_renderer)
        self.assertIn('label.textContent = "Answer"', chat_renderer)
        self.assertIn('title.textContent = "참조"', message_shells)
        self.assertIn(".assistant-copy", html)
        self.assertIn(".citation-list-title", html)
        self.assertIn(".suggestion-list-title", html)
        self.assertIn(".followup-chip", html)
        self.assertIn('title.textContent = "추천 질문"', message_shells)
        self.assertIn('void deps.sendMessage({ query: suggestedQuery })', message_shells)
        self.assertIn('id="source-panel-toggle-btn"', html)
        self.assertIn("function setStudyTab", workspace_state)
        self.assertIn('data-study-tab="source"', html)
        self.assertIn('data-study-tab="library"', html)
        self.assertIn('data-study-tab="ingest"', html)
        self.assertIn('data-study-tab="query"', html)
        self.assertIn('data-study-tab="session"', html)
        self.assertIn('data-study-tab="pipeline"', html)
        self.assertIn('data-study-page="query"', html)
        self.assertIn('data-study-page="session"', html)
        self.assertIn('data-study-page="pipeline"', html)
        self.assertIn('data-study-page="library"', html)
        self.assertIn('id="library-summary"', html)
        self.assertIn('id="library-list"', html)
        self.assertIn('id="library-detail"', html)
        self.assertIn('id="ingest-dropzone"', html)
        self.assertIn('id="ingest-file-btn"', html)
        self.assertIn('id="ingest-file-input"', html)
        self.assertIn('id="ingest-file-pill"', html)
        self.assertIn("function renderIngestCaptureMeta", intake_renderer)
        self.assertIn("function renderDocToBookPreview", intake_renderer)
        self.assertIn("function renderLibraryDetail", intake_renderer)
        self.assertIn("function setIngestStatus", intake_renderer)
        self.assertIn("function openLibraryTrace", source_workflows)
        self.assertIn("function openLibraryAsset", source_workflows)
        self.assertIn("function humanizeSourceCollection", shell_helpers)
        self.assertIn("function formatInferredScope", shell_helpers)
        self.assertIn("function qualityStatusLabel", shell_helpers)
        self.assertIn("function isReviewNeeded", shell_helpers)
        self.assertIn('refs.sourceTitleEl.textContent = "근거 문서를 선택하세요";', panel_controller)
        self.assertIn("핵심 구간과 원문 링크를 함께 보여줍니다.", panel_controller)
        self.assertIn("function uploadDocToBookFile", intake_actions)
        self.assertIn("function handleIngestFileSelection", intake_actions)
        self.assertIn("function syncIngestUploadHint", intake_actions)
        self.assertIn('id="source-viewer-frame"', html)
        self.assertIn('id="source-outline"', html)
        self.assertIn('data-study-tab="ingest"', html)
        self.assertIn('id="ingest-plan-btn"', html)
        self.assertIn('id="ingest-save-btn"', html)
        self.assertIn('id="ingest-capture-btn"', html)
        self.assertIn('id="ingest-normalize-btn"', html)
        self.assertIn('id="ingest-open-capture-btn"', html)
        self.assertIn('id="ingest-capture-meta"', html)
        self.assertIn("function previewDocToBookPlan", intake_actions)
        self.assertIn("function createDocToBookDraft", intake_actions)
        self.assertIn("function captureDocToBookDraft", intake_actions)
        self.assertIn("function normalizeDocToBookDraft", intake_actions)
        self.assertIn("function fetchDocToBookBook", intake_actions)
        self.assertIn("function openCapturedDocToBookDraft", source_workflows)
        self.assertIn("function loadDocToBookDrafts", intake_actions)
        self.assertIn("function openDocToBookDraft", intake_actions)
        self.assertIn(".source-tag-group", html)
        self.assertIn(".source-tag", html)
        self.assertIn(".summary-grid", html)
        self.assertIn("function startStatusPulse", diagnostics_renderer)
        self.assertIn("function setStatus", diagnostics_renderer)
        self.assertIn("function updateSessionContextDisplay", diagnostics_renderer)
        self.assertIn("function humanizePipelineKey", diagnostics_renderer)
        self.assertIn("function summarizeTraceMeta", diagnostics_renderer)
        self.assertIn("function renderPipelineSummary", diagnostics_renderer)
        self.assertIn("function renderPipelineTrace", diagnostics_renderer)
        self.assertIn("function appendTraceEvent", diagnostics_renderer)
        self.assertIn(".trace-step", html)
        self.assertIn('class="summary-grid"', html)
        self.assertIn("수집 결과", html)
        self.assertIn("보관함 개요", html)
        self.assertIn("정리된 자료", html)
        self.assertIn("정리 결과", html)
        self.assertIn("저장된 초안", html)
        self.assertIn("파일이나 URL로 초안을 만듭니다", html)
        self.assertIn("파일 선택", html)
        self.assertIn("초안 보기", html)
        self.assertIn("결과 보기", html)
        self.assertIn("문서 열기", html)
        self.assertIn("function setSourcePanelVisible", panel_controller)
        self.assertIn('참조 패널 닫기', panel_controller)
        self.assertIn('참조 패널 열기', panel_controller)
        self.assertIn("function fetchSourceMeta", panel_controller)
        self.assertIn("function fetchSourceBook", panel_controller)
        self.assertIn("function renderSourceBook", panel_controller)
        self.assertIn("function openSourcePanel", panel_controller)
        self.assertIn("function resetSourcePanel", panel_controller)
        self.assertIn("function citationMapByIndex", panel_controller)
        self.assertIn("function syncActiveSourceTags", panel_controller)
        self.assertIn(
            '(meta && meta.viewer_path) || citation.viewer_path || citation.href || ""',
            panel_controller,
        )
        self.assertIn(
            'const viewerPath = citation.viewer_path',
            panel_controller,
        )
        self.assertIn(
            'const viewerHref = viewerPath',
            panel_controller,
        )
        self.assertIn('class="source-frame-shell" hidden', html)
        self.assertIn(".source-frame-shell[hidden]", html)

    def test_server_static_responses_disable_cache(self) -> None:
        server_source = (
            ROOT / "src" / "play_book_studio" / "app" / "server.py"
        ).read_text(encoding="utf-8")

        self.assertIn('self.send_header("Cache-Control", "no-store")', server_source)
        self.assertIn('self.send_header("Pragma", "no-cache")', server_source)

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

    def test_build_session_debug_payload_includes_history(self) -> None:
        session = ChatSession(
            session_id="session-1",
            mode="ops",
            context=SessionContext(mode="ops", user_goal="replicas 조정", ocp_version="4.20"),
            history=[
                Turn(
                    query="Deployment replicas를 3에서 5로 바꾸려면?",
                    mode="ops",
                    answer="답변: `oc scale`을 사용하세요.",
                )
            ],
        )

        payload = _build_session_debug_payload(session)

        self.assertEqual("session-1", payload["session_id"])
        self.assertEqual(1, payload["history_size"])
        self.assertEqual("Deployment replicas를 3에서 5로 바꾸려면?", payload["last_query"])
        self.assertEqual("replicas 조정", payload["context"]["user_goal"])
        self.assertEqual("답변: `oc scale`을 사용하세요.", payload["history"][0]["answer"])

    def test_append_chat_turn_log_writes_jsonl_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            session = ChatSession(
                session_id="session-2",
                mode="ops",
                context=SessionContext(mode="ops", user_goal="replicas 조정", ocp_version="4.20"),
                history=[
                    Turn(
                        query="그럼 5개에서 10개로 변경하려면?",
                        mode="ops",
                        answer="답변: replicas를 10으로 바꾸세요.",
                    )
                ],
            )
            result = AnswerResult(
                query="그럼 5개에서 10개로 변경하려면?",
                mode="ops",
                answer="답변: replicas를 10으로 바꾸세요.",
                rewritten_query="OCP 4.20 | 사용자 목표 replicas 조정 | 그럼 5개에서 10개로 변경하려면?",
                citations=[],
                retrieval_trace={"query": "rewritten"},
                pipeline_trace={"timings_ms": {"total": 10}},
            )

            target = _append_chat_turn_log(
                root,
                session=session,
                query=result.query,
                result=result,
                context_before=SessionContext(mode="ops", user_goal="replicas 조정", ocp_version="4.20"),
                context_after=session.context,
            )

            self.assertTrue(target.exists())
            rows = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertEqual(1, len(rows))
            self.assertEqual("session-2", rows[0]["session_id"])
            self.assertEqual("그럼 5개에서 10개로 변경하려면?", rows[0]["query"])
            self.assertEqual("replicas 조정", rows[0]["context_after"]["user_goal"])
            self.assertEqual(1, rows[0]["history_size"])

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

        self.assertEqual("세션 f4296055", payload["session_name"])
        self.assertEqual("f4296055abcdef12", payload["session_id"])
        self.assertEqual(20, payload["turn_count"])
        self.assertEqual(20, len(payload["turns"]))
        self.assertEqual("질문 5", payload["turns"][0]["user"])
        self.assertEqual("답변 24", payload["turns"][-1]["chatbot"])
        self.assertEqual("질문 5 확장", payload["turns"][0]["rewritten_query"])
        self.assertEqual("사용자 입력", payload["turns"][0]["stages"][0]["label"])
        self.assertEqual("ok", payload["turns"][0]["diagnosis"]["severity"])

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

    def test_viewer_path_parser_accepts_non_default_pack_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            raw_html_dir = root / "custom_raw_html"
            raw_html_dir.mkdir(parents=True)
            expected = raw_html_dir / "architecture.html"
            expected.write_text("<html><body>ok</body></html>", encoding="utf-8")
            (root / ".env").write_text(
                "RAW_HTML_DIR=custom_raw_html\n"
                "OCP_VERSION=4.18\n",
                encoding="utf-8",
            )

            target = _viewer_path_to_local_html(
                root,
                "/docs/ocp/4.18/ko/architecture/index.html#overview",
            )

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

            normalized_docs_path = root / "artifacts" / "corpus" / "normalized_docs.jsonl"
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
        self.assertEqual("OpenShift 4.20", payload["pack_label"])
        self.assertEqual("openshift", payload["inferred_product"])
        self.assertEqual("4.20", payload["inferred_version"])
        self.assertTrue(payload["section_match_exact"])

    def test_serialize_citation_marks_section_fallback_when_anchor_missing(self) -> None:
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

            normalized_docs_path = root / "artifacts" / "corpus" / "normalized_docs.jsonl"
            normalized_docs_path.parent.mkdir(parents=True)
            normalized_docs_path.write_text(
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
                        "text": "본문",
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
                    chunk_id="chunk-1",
                    book_slug="architecture",
                    section="존재하지 않는 섹션",
                    anchor="missing-anchor",
                    source_url="https://example.com/architecture",
                    viewer_path="/docs/ocp/4.20/ko/architecture/index.html#missing-anchor",
                    excerpt="본문",
                ),
            )

        self.assertFalse(payload["section_match_exact"])

    def test_internal_viewer_html_uses_normalized_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            normalized_docs_path = root / "artifacts" / "corpus" / "normalized_docs.jsonl"
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
        self.assertIn("Reference Viewer", html)
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
            normalized_docs_path = root / "artifacts" / "corpus" / "normalized_docs.jsonl"
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
        self.assertEqual("OpenShift 4.20", payload["pack_label"])
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
            with patch("play_book_studio.ingestion.collector.requests.get", return_value=_FakeResponse()):
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
            with patch("play_book_studio.ingestion.collector.requests.get", return_value=_FakeResponse()):
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
        self.assertIn("capture된 웹 문서를 canonical section으로 정리한 내부 study view입니다.", viewer_html)

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
        self.assertTrue(meta["section_match_exact"])

    def test_doc_to_book_meta_marks_fallback_when_anchor_missing(self) -> None:
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
                        "normalized_section_count": 1,
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
                        ],
                        "notes": [],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            meta = _doc_to_book_meta_for_viewer_path(root, "/docs/intake/dtb-review/index.html#missing")

        self.assertIsNotNone(meta)
        assert meta is not None
        self.assertFalse(meta["section_match_exact"])

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
        self.assertTrue(payload["section_match_exact"])

    def test_internal_doc_to_book_viewer_html_uses_pdf_summary_for_pdf_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            draft_dir = root / "artifacts" / "doc_to_book" / "drafts"
            book_dir = root / "artifacts" / "doc_to_book" / "books"
            draft_dir.mkdir(parents=True)
            book_dir.mkdir(parents=True)

            (draft_dir / "dtb-pdf.json").write_text(
                json.dumps(
                    {
                        "draft_id": "dtb-pdf",
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
                        "canonical_book_path": str(book_dir / "dtb-pdf.json"),
                        "normalized_section_count": 1,
                        "normalize_error": "",
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )
            (book_dir / "dtb-pdf.json").write_text(
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
                                "section_key": "demo-pdf:short-a",
                                "heading": "온프레미스",
                                "section_level": 1,
                                "section_path": ["Page 1", "온프레미스"],
                                "section_path_label": "Page 1 > 온프레미스",
                                "anchor": "short-a",
                                "viewer_path": "/docs/intake/dtb-pdf/index.html#short-a",
                                "source_url": "/tmp/demo.pdf",
                                "text": "온프레미스",
                                "block_kinds": ["paragraph"],
                            },
                        ],
                        "notes": [],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            viewer_html = _internal_doc_to_book_viewer_html(root, "/docs/intake/dtb-pdf/index.html#short-a")

        self.assertIsNotNone(viewer_html)
        assert viewer_html is not None
        self.assertIn("capture된 PDF를 canonical section으로 정리한 내부 study view입니다.", viewer_html)


if __name__ == "__main__":
    unittest.main()
