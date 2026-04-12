from __future__ import annotations

import json
import os
import shutil
import subprocess
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
    _append_chat_turn_log,
    _build_handler,
    _build_health_payload,
    _build_session_debug_payload,
    _build_turn_diagnosis,
    _citation,
    _citation_href,
    _clean_source_view_text,
    _context_with_request_overrides,
    _refresh_answerer_llm_settings,
    _suggest_follow_up_questions,
    ChatSession,
    SessionContext,
    SessionStore,
    Turn,
)

TEST_RUNTIME_LLM_ENDPOINT = "http://test-runtime-llm.example/v1"
TEST_STALE_PROCESS_LLM_ENDPOINT = "http://stale-process-llm.example/v1"


class TestAppRuntimeUi(unittest.TestCase):
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
                f"LLM_ENDPOINT={TEST_RUNTIME_LLM_ENDPOINT}\n"
                "LLM_MODEL=Qwen/Qwen3.5-9B\n",
                encoding="utf-8",
            )
            original_endpoint = os.environ.get("LLM_ENDPOINT")
            original_model = os.environ.get("LLM_MODEL")
            try:
                os.environ["LLM_ENDPOINT"] = TEST_STALE_PROCESS_LLM_ENDPOINT
                os.environ["LLM_MODEL"] = "old-model"
                answerer = _FakeAnswerer(TEST_STALE_PROCESS_LLM_ENDPOINT)
                refreshed, signature = _refresh_answerer_llm_settings(
                    answerer,
                    root_dir=root,
                    current_signature=("stale",),
                )
                self.assertIs(refreshed, answerer)
                self.assertEqual(TEST_RUNTIME_LLM_ENDPOINT, refreshed.settings.llm_endpoint)
                self.assertEqual(TEST_RUNTIME_LLM_ENDPOINT, refreshed.llm_client.endpoint)
                self.assertIn(TEST_RUNTIME_LLM_ENDPOINT, signature)
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
                    "fallback_enabled": False,
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
            self.assertFalse(runtime["llm_fallback_enabled"])
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
        home_html = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "index.html"
        ).read_text(encoding="utf-8")
        workspace_html = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "workspace.html"
        ).read_text(encoding="utf-8")
        data_situation_room_html = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "data-situation-room.html"
        ).read_text(encoding="utf-8")
        assets_dir = ROOT / "src" / "play_book_studio" / "app" / "static" / "assets"
        app_shell_css = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(assets_dir.glob("app-shell*.css"))
        )
        homepage_css = (
            assets_dir / "homepage.css"
        ).read_text(encoding="utf-8")
        app_config = (
            assets_dir / "app-config.js"
        ).read_text(encoding="utf-8")
        homepage_js = (
            assets_dir / "homepage.js"
        ).read_text(encoding="utf-8")
        app_bootstrap = (
            assets_dir / "app-bootstrap.js"
        ).read_text(encoding="utf-8")
        data_situation_room = (
            assets_dir / "data-situation-room.js"
        ).read_text(encoding="utf-8")
        app_bootstrap_events = (
            assets_dir / "app-bootstrap-events.js"
        ).read_text(encoding="utf-8")
        app_shell_state = (
            assets_dir / "app-shell-state.js"
        ).read_text(encoding="utf-8")
        shell_helpers = (
            assets_dir / "shell-helpers.js"
        ).read_text(encoding="utf-8")
        panel_controller = (
            assets_dir / "panel-controller.js"
        ).read_text(encoding="utf-8")
        chat_renderer = (
            assets_dir / "chat-renderer.js"
        ).read_text(encoding="utf-8")
        message_shells = (
            assets_dir / "message-shells.js"
        ).read_text(encoding="utf-8")
        chat_session = (
            assets_dir / "chat-session.js"
        ).read_text(encoding="utf-8")
        workspace_state = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "assets" / "workspace-state.js"
        ).read_text(encoding="utf-8")
        diagnostics_renderer = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "assets" / "diagnostics-renderer.js"
        ).read_text(encoding="utf-8")
        self.assertIn("event.isComposing || event.keyCode === 229 || state.isComposing", chat_session)
        self.assertIn("/api/chat/stream", chat_session)
        self.assertIn("async function consumeChatStream", chat_session)
        self.assertIn("function renderSendButtonState(generating)", shell_helpers)
        self.assertIn('refs.sendBtn.innerHTML = \'<span class=\"send-btn-stop-icon\" aria-hidden=\"true\"></span>\';', shell_helpers)
        self.assertIn("window.createAppBootstrap", app_bootstrap)
        self.assertIn('fetch("/api/data-control-room"', data_situation_room)
        self.assertIn("window.bindAppBootstrapEvents", app_bootstrap_events)
        self.assertIn("window.createWorkspaceState", workspace_state)
        self.assertIn("window.createDiagnosticsRenderer", diagnostics_renderer)
        self.assertIn("window.createPanelController", panel_controller)
        self.assertIn("window.createChatRenderer", chat_renderer)
        self.assertIn("window.createChatSession", chat_session)
        self.assertIn("function renumberOrderedSteps(text)", chat_renderer)
        self.assertIn("return renumberOrderedSteps(normalized);", chat_renderer)
        self.assertIn("window.OCP_PLAY_STUDIO_CONFIG", app_config)
        self.assertIn("window.createAppShellState", app_shell_state)
        self.assertIn("function renderCorePackOptions()", workspace_state)
        self.assertIn("function renderTopicPlaybooks(playbooks)", workspace_state)
        self.assertIn("function hydrateFromDataControlRoom(payload)", workspace_state)
        self.assertIn("function setCorePack(", workspace_state)
        self.assertIn("isReviewNeeded: helpers.isReviewNeeded", app_bootstrap)
        self.assertIn('fetch("/api/data-control-room"', app_bootstrap)
        self.assertNotIn("data-control-room.js", app_bootstrap)
        self.assertNotIn("openDataControlRoom", app_bootstrap)
        self.assertNotIn("setDataControlRoomVisible", app_bootstrap)
        self.assertNotIn("selectedSourceCountEl", app_shell_state)
        self.assertNotIn("railOpenIntakeBtn", app_shell_state)
        self.assertNotIn("railLibraryListEl", app_shell_state)
        self.assertNotIn("activeIngestDraftId", app_shell_state)
        self.assertNotIn("docToBookDraftCache", app_shell_state)
        self.assertNotIn("dataControlRoomVisible", app_shell_state)
        self.assertNotIn("dataControlRoomOpenBtn", app_shell_state)
        self.assertNotIn("dataControlRoomOverlayEl", app_shell_state)
        self.assertIn("topicPlaybookListEl", app_shell_state)
        self.assertIn("topicPlaybookSummaryEl", app_shell_state)
        self.assertNotIn("createIntakeRenderer", app_bootstrap)
        self.assertNotIn("createIntakeActions", app_bootstrap)
        self.assertNotIn("createSummaryChip", app_bootstrap)
        self.assertNotIn("createSourceWorkflows", app_bootstrap)
        self.assertNotIn("bindIngestStatus", shell_helpers)
        self.assertNotIn("setIngestBusy", shell_helpers)
        self.assertNotIn("qualityStatusLabel", shell_helpers)
        self.assertNotIn("support-surface", home_html)
        self.assertNotIn("railOpenIntakeBtn", app_bootstrap_events)
        self.assertNotIn("ingestFileBtn", app_bootstrap_events)
        self.assertNotIn("loadDocToBookDrafts", app_bootstrap_events)
        self.assertNotIn("/assets/app-shell-viewers-intake.css", app_shell_css)
        self.assertIn('@import url("/assets/app-shell-workspace.css");', app_shell_css)
        self.assertIn("@media (max-width: 760px)", app_shell_css)
        self.assertIn(".workspace-shell .trace-tab-left.active", app_shell_css)
        self.assertIn("Play Book Studio", home_html)
        self.assertIn("Enterprise Playbook Platform", home_html)
        self.assertIn("공식 문서를 실행형 플레이북으로.", home_html)
        self.assertIn('href="/workspace"', home_html)
        self.assertIn('href="/data-situation-room"', home_html)
        self.assertIn('id="hero-prev-btn"', home_html)
        self.assertIn('id="hero-next-btn"', home_html)
        self.assertIn('id="metric-approved-runtime"', home_html)
        self.assertIn('id="metric-topic-playbooks"', home_html)
        self.assertIn('id="metric-answer-pass-rate"', home_html)
        self.assertIn('id="metric-evidence-ready"', home_html)
        self.assertIn('/assets/homepage.js', home_html)
        self.assertIn(".home-hero-stage", homepage_css)
        self.assertIn('fetch("/api/data-control-room"', homepage_js)
        self.assertNotIn("Owner Checklist", home_html)
        self.assertNotIn("구매형 대화 데모", home_html)
        self.assertNotIn("왜 사야 하나", home_html)
        self.assertNotIn("참조 원문", home_html)
        self.assertIn("<h1>데이터상황실</h1>", data_situation_room_html)
        self.assertIn("원문 매뉴얼북", data_situation_room_html)
        self.assertIn("플레이북 라이브러리", data_situation_room_html)
        self.assertIn('id="data-situation-room-refresh-btn"', data_situation_room_html)
        self.assertIn('id="data-situation-room-summary-raw-manuals"', data_situation_room_html)
        self.assertIn('id="data-situation-room-summary-manual-books"', data_situation_room_html)
        self.assertIn('id="data-situation-room-summary-playbooks"', data_situation_room_html)
        self.assertIn('id="data-situation-room-manual-core-list"', data_situation_room_html)
        self.assertIn('id="data-situation-room-manual-extra-list"', data_situation_room_html)
        self.assertIn('id="data-situation-room-family-grid"', data_situation_room_html)
        self.assertIn('id="data-situation-room-family-sections"', data_situation_room_html)
        self.assertIn('id="data-situation-room-ops-retrieval"', data_situation_room_html)
        self.assertIn('id="data-situation-room-ops-answer"', data_situation_room_html)
        self.assertIn('id="data-situation-room-ops-runtime-count"', data_situation_room_html)
        self.assertIn('id="data-situation-room-ops-runtime-report"', data_situation_room_html)
        self.assertNotIn("High-Value Focus", data_situation_room_html)
        self.assertNotIn("Source-of-Truth / Drift", data_situation_room_html)
        self.assertIn('id="version-chip"', workspace_html)
        self.assertIn('id="active-pack-title"', workspace_html)
        self.assertIn("실행형 질의응답", workspace_html)
        self.assertIn('id="pack-stack"', workspace_html)
        self.assertIn('id="topic-playbook-summary"', workspace_html)
        self.assertIn('id="topic-playbook-list"', workspace_html)
        self.assertIn("Situation Room", workspace_html)
        self.assertIn('data-rail-page="library"', workspace_html)
        self.assertIn('data-rail-page="friendly_trace"', workspace_html)
        self.assertIn('data-study-page="source"', workspace_html)
        self.assertIn('id="source-viewer-frame"', workspace_html)
        self.assertIn('class="source-frame-shell" hidden', workspace_html)
        self.assertIn('id="core-version-picker"', workspace_html)
        self.assertIn('id="core-source-summary"', workspace_html)
        self.assertIn("참조 원문", workspace_html)
        self.assertIn('class="data-control-room-launch-btn"', workspace_html)
        self.assertNotIn("Backup / Restore", workspace_html)
        self.assertNotIn("Monitoring", workspace_html)
        self.assertNotIn("Source Trace", workspace_html)
        self.assertNotIn("4.18", app_config)
        self.assertNotIn("4.16", app_config)
        self.assertNotIn('id="workspace-support-surface"', workspace_html)
        self.assertNotIn("사용자 보관함", workspace_html)
        self.assertNotIn("새 자료 업로드", workspace_html)
        self.assertNotIn('id="selected-source-count"', workspace_html)
        self.assertNotIn('id="rail-upload-status"', workspace_html)
        self.assertNotIn('id="ingest-dropzone"', workspace_html)
        self.assertNotIn('id="library-summary"', workspace_html)
        self.assertNotIn('data-study-page="friendly_trace"', workspace_html)
        self.assertNotIn('data-study-page="library"', workspace_html)
        self.assertNotIn('data-study-page="ingest"', workspace_html)
        self.assertNotIn('data-study-page="query"', workspace_html)
        self.assertNotIn('data-study-page="session"', workspace_html)
        self.assertNotIn('data-study-page="pipeline"', workspace_html)
        self.assertNotIn('/assets/intake-renderer.js', workspace_html)
        self.assertNotIn('/assets/intake-actions.js', workspace_html)
        self.assertNotIn('/assets/source-workflows.js', workspace_html)
        self.assertNotIn("/api/source-book", panel_controller)
        self.assertNotIn("toggleDataControlRoom", app_bootstrap_events)
        self.assertNotIn("setDataControlRoomVisible", app_bootstrap_events)
        self.assertNotIn("dataControlRoomVisible", app_bootstrap_events)
        self.assertIn("function fetchSourceMeta", panel_controller)
        self.assertIn("function openSourcePanel", panel_controller)
        self.assertIn("function resetSourcePanel", panel_controller)
        self.assertIn("function citationMapByIndex", panel_controller)
        self.assertIn("embed=1", panel_controller)
        self.assertIn('"/data-situation-room"', workspace_html)
        self.assertIn("/api/data-control-room", data_situation_room)
        self.assertIn("manual_book_library", data_situation_room)
        self.assertIn("playbook_library", data_situation_room)
        self.assertIn("function renderManualLibrary", data_situation_room)
        self.assertIn("function renderPlaybookLibrary", data_situation_room)
        self.assertIn("function renderOpsSnapshot", data_situation_room)
        self.assertIn("function familySection", data_situation_room)
        self.assertIn("function renderErrorState", data_situation_room)
        self.assertNotIn("known_books", data_situation_room)
        self.assertNotIn("active_queue", data_situation_room)
        self.assertNotIn("source_of_truth_drift", data_situation_room)
        self.assertNotIn("renderOpsNotes(payload)", data_situation_room)
        self.assertNotIn("function corpusRowCard", data_situation_room)
        self.assertNotIn("function manualbookRowCard", data_situation_room)
        self.assertIn("function renderMarkdownInto", chat_renderer)
        self.assertIn("navigator.clipboard.writeText", chat_renderer)
        self.assertIn('copyButton.textContent = "복사"', chat_renderer)
        self.assertIn('wrapButton.textContent = "줄바꿈"', chat_renderer)
        self.assertIn("toggleCodeWrap(block, wrapButton)", chat_renderer)
        self.assertIn('list.setAttribute("start", String(listStart))', chat_renderer)
        self.assertIn('const orderedItem = trimmed.match(/^(\\d+)\\.\\s+(.*)$/);', chat_renderer)
        self.assertIn('let codeTarget = "fragment";', chat_renderer)
        self.assertIn("function appendCodeBlockToActiveList(code, language = \"text\")", chat_renderer)
        self.assertIn("item.codeBlocks.forEach((block) => {", chat_renderer)
        self.assertIn("function renderEmptyState", message_shells)
        self.assertIn("질문 분석", message_shells)
        self.assertIn("리랭킹", message_shells)
        self.assertIn("참조 정리", message_shells)
        self.assertIn("stage-strip", message_shells)

    def test_index_shell_links_to_dedicated_data_situation_room_page(self) -> None:
        home_html = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "index.html"
        ).read_text(encoding="utf-8")
        workspace_html = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "workspace.html"
        ).read_text(encoding="utf-8")
        app_bootstrap = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "assets" / "app-bootstrap.js"
        ).read_text(encoding="utf-8")

        self.assertIn('href="/workspace"', home_html)
        self.assertIn('href="/data-situation-room"', home_html)
        self.assertIn('<a class="data-control-room-launch-btn" href="/data-situation-room"', workspace_html)
        self.assertIn('title="데이터상황실 열기"', workspace_html)
        self.assertNotIn("data-control-room.js", app_bootstrap)
        self.assertNotIn("data-control-room-open-btn", home_html)

    def test_server_static_responses_disable_cache(self) -> None:
        server_source = (
            ROOT / "src" / "play_book_studio" / "app" / "server.py"
        ).read_text(encoding="utf-8")

        self.assertIn('self.send_header("Cache-Control", "no-store")', server_source)
        self.assertIn('self.send_header("Pragma", "no-cache")', server_source)
        self.assertIn('WORKSPACE_HTML_PATH = STATIC_DIR / "workspace.html"', server_source)
        self.assertIn('"/workspace"', server_source)
        self.assertIn('"/data-situation-room"', server_source)

    def test_reset_handler_generates_session_id_without_name_error(self) -> None:
        from play_book_studio.config.settings import load_settings

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = load_settings(root)

            class _FakeAnswerer:
                def __init__(self, settings) -> None:
                    self.settings = settings

            payload_holder: dict[str, object] = {}
            handler_cls = _build_handler(
                answerer=_FakeAnswerer(settings),
                store=SessionStore(),
                root_dir=root,
            )
            handler = object.__new__(handler_cls)
            handler._send_json = lambda payload, status=None: payload_holder.update(
                payload=payload,
                status=status,
            )

            handler._handle_reset({})

            payload = payload_holder["payload"]
            assert isinstance(payload, dict)
            self.assertTrue(payload["session_id"])
            self.assertEqual("chat", payload["mode"])
            self.assertIn("context", payload)

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
