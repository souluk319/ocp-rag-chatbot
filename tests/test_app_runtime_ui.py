from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from _support_app_ui import *  # noqa: F401,F403

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
        html = (
            ROOT / "src" / "play_book_studio" / "app" / "static" / "index.html"
        ).read_text(encoding="utf-8")
        assets_dir = ROOT / "src" / "play_book_studio" / "app" / "static" / "assets"
        app_shell_css = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(assets_dir.glob("app-shell*.css"))
        )
        app_config = (
            assets_dir / "app-config.js"
        ).read_text(encoding="utf-8")
        app_bootstrap = (
            assets_dir / "app-bootstrap.js"
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
        self.assertIn("function renderSendButtonState(generating)", shell_helpers)
        self.assertIn('refs.sendBtn.innerHTML = \'<span class=\"send-btn-stop-icon\" aria-hidden=\"true\"></span>\';', shell_helpers)
        self.assertNotIn("setButtonBusy(refs.sendBtn, next);", shell_helpers)
        self.assertIn("async function consumeChatStream", chat_session)
        self.assertNotIn('id="pipeline-trace"', html)
        self.assertNotIn('id="pipeline-summary"', html)
        self.assertNotIn('data-study-page="friendly_trace"', html)
        self.assertIn('data-rail-page="friendly_trace"', html)
        self.assertIn("Play Book Studio", html)
        self.assertIn("<h1>OCP Book Studio</h1>", html)
        self.assertIn('<title>Play Book Studio</title>', html)
        self.assertIn("OpenShift v4.20 DEMO", html)
        self.assertIn('<link rel="stylesheet" href="/assets/app-shell.css">', html)
        self.assertIn("--accent: #ee0000;", app_shell_css)
        self.assertIn("--layout-gap: 16px;", app_shell_css)
        self.assertIn("padding: var(--layout-gap);", app_shell_css)
        self.assertIn("height: 100dvh;", app_shell_css)
        self.assertIn("flex: 1 1 auto;", app_shell_css)
        self.assertIn("grid-template-columns: 0 minmax(0, 1.22fr) minmax(620px, 1.04fr);", app_shell_css)
        self.assertIn(".send-btn-stop-icon", app_shell_css)
        self.assertIn("#send-btn.is-stop", app_shell_css)
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
        self.assertIn("if (!token) continue;", chat_renderer)
        self.assertNotIn("if (!token) return;", chat_renderer)
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
        self.assertIn("vertical-align: middle;", app_shell_css)
        self.assertNotIn("vertical-align: super;", app_shell_css)
        self.assertIn('version: "4.20"', app_config)
        self.assertIn("etcd 백업 절차", app_config)
        self.assertIn("Route / Ingress 차이", app_config)
        self.assertIn("특정 namespace에 admin 권한 주는 법 알려줘", app_config)
        self.assertNotIn("이미지 레지스트리 저장소를 구성하려면?", app_config)
        self.assertIn("function renderEmptyState", message_shells)
        self.assertIn("function escapeHtml(value)", message_shells)
        self.assertIn("function contextualizeSuggestedQuery(suggestedQuery, payload)", message_shells)
        self.assertIn('if (/operator/i.test(rewritten) || /operator/i.test(answer) || /operator/i.test(primarySection)) {', message_shells)
        self.assertIn('`${subject} 관련 주의사항도 함께 정리해줘`', message_shells)
        self.assertIn('`${subject} 상태 확인 방법도 같이 알려줘`', message_shells)
        self.assertIn("const canRenderSuggestedQueries = (", message_shells)
        self.assertIn('payload.response_kind === "rag"', message_shells)
        self.assertIn("payload.cited_indices.length > 0", message_shells)
        self.assertIn("payload.warnings.length === 0", message_shells)
        self.assertNotIn("경고 ${payload.warnings.length}개", message_shells)
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
        self.assertIn("기반 소스", html)
        self.assertIn("사용자 보관함", html)
        self.assertIn("새 자료 업로드", html)
        self.assertIn("무엇이 궁금한가요?", html)
        self.assertNotIn('id="source-hero"', html)
        self.assertIn('id="rail-upload-status"', html)
        self.assertIn('id="composer-samples"', html)
        self.assertNotIn("예시 질문", chat_session)
        self.assertIn("OpenShift 4.20 공식 문서", html)
        self.assertIn('id="active-pack-title"', html)
        self.assertIn(".core-pack-tab", app_shell_css)
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
        self.assertIn(".assistant-copy", app_shell_css)
        self.assertIn(".citation-list-title", app_shell_css)
        self.assertIn(".suggestion-list-title", app_shell_css)
        self.assertIn(".followup-chip", app_shell_css)
        self.assertIn('title.textContent = "추천 질문"', message_shells)
        self.assertIn('void deps.sendMessage({ query: effectiveQuery })', message_shells)
        self.assertIn('id="source-panel-toggle-btn"', html)
        self.assertIn("function setStudyTab", workspace_state)
        self.assertNotIn('data-study-tab="source"', html)
        self.assertNotIn('data-study-tab="library"', html)
        self.assertNotIn('data-study-tab="ingest"', html)
        self.assertNotIn('data-study-tab="query"', html)
        self.assertNotIn('data-study-tab="session"', html)
        self.assertNotIn('data-study-tab="pipeline"', html)
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
        self.assertIn("function uploadDocToBookFile", intake_actions)
        self.assertIn("function handleIngestFileSelection", intake_actions)
        self.assertIn("function syncIngestUploadHint", intake_actions)
        self.assertIn('id="source-viewer-frame"', html)
        self.assertNotIn('id="source-summary-strip"', html)
        self.assertNotIn('id="source-outline"', html)
        self.assertNotIn('id="source-open-origin"', html)
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
        self.assertIn(".source-tag-group", app_shell_css)
        self.assertIn(".source-tag", app_shell_css)
        self.assertIn(".summary-grid", app_shell_css)
        self.assertIn("function startStatusPulse", diagnostics_renderer)
        self.assertIn("function setStatus", diagnostics_renderer)
        self.assertIn("function updateSessionContextDisplay", diagnostics_renderer)
        self.assertIn("function humanizePipelineKey", diagnostics_renderer)
        self.assertIn("function summarizeTraceMeta", diagnostics_renderer)
        self.assertIn("function renderPipelineSummary", diagnostics_renderer)
        self.assertIn("function renderPipelineTrace", diagnostics_renderer)
        self.assertIn("function appendTraceEvent", diagnostics_renderer)
        self.assertIn(".trace-step", app_shell_css)
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
        self.assertNotIn('id="source-open-doc"', html)
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
        self.assertIn("function buildEmbeddedViewerHref", panel_controller)
        self.assertIn("embed=1", panel_controller)
        self.assertIn('class="source-frame-shell" hidden', html)
        self.assertIn(".source-frame-shell[hidden]", app_shell_css)
        self.assertIn("grid-template-rows: auto minmax(0, 1fr);", app_shell_css)
        self.assertNotIn("grid-template-rows: auto auto minmax(0, 1fr);", app_shell_css)
        self.assertIn('font-family: "Red Hat Display", "Red Hat Text", sans-serif;', app_shell_css)
        self.assertIn("font-size: 22px;", app_shell_css)
        self.assertIn('.inspector-page[data-study-page="source"]', app_shell_css)
        self.assertNotIn("height: min(720px, 56vh);", app_shell_css)
        self.assertNotIn("min-height: 420px;", app_shell_css)
        self.assertNotIn("열린 문서가 없습니다", html)
        self.assertNotIn('class="source-empty"', html)

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
