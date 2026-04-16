from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import Settings, load_effective_env, load_settings

TEST_SHADOW_EMBEDDING_BASE_URL = "http://shadow-embed.example/v1"
TEST_SHADOW_LLM_ENDPOINT = "http://shadow-llm.example/v1"
TEST_SHADOW_QDRANT_URL = "http://shadow-qdrant.example:6333"
TEST_AMBIENT_EMBEDDING_BASE_URL = "http://ambient-embed.example/v1"
TEST_AMBIENT_LLM_ENDPOINT = "http://ambient-llm.example/v1"
TEST_AMBIENT_QDRANT_URL = "http://ambient-qdrant.example:6333"
TEST_RUNTIME_LLM_ENDPOINT = "http://test-runtime-llm.example/v1"
TEST_STALE_PROCESS_LLM_ENDPOINT = "http://stale-process-llm.example/v1"
TEST_RUNTIME_OVERRIDE_LLM_ENDPOINT = "http://example-runtime-llm.example/v1"


class SettingsPathTests(unittest.TestCase):
    def test_direct_settings_constructor_ignores_ambient_env_and_dotenv(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "ARTIFACTS_DIR=shadow-artifacts\n"
                "RAW_HTML_DIR=shadow-raw-html\n"
                f"EMBEDDING_BASE_URL={TEST_SHADOW_EMBEDDING_BASE_URL}\n"
                f"LLM_ENDPOINT={TEST_SHADOW_LLM_ENDPOINT}\n"
                f"QDRANT_URL={TEST_SHADOW_QDRANT_URL}\n",
                encoding="utf-8",
            )
            old_env = {
                key: os.environ.get(key)
                for key in ("ARTIFACTS_DIR", "RAW_HTML_DIR", "EMBEDDING_BASE_URL", "LLM_ENDPOINT", "QDRANT_URL")
            }
            try:
                os.environ["ARTIFACTS_DIR"] = "ambient-artifacts"
                os.environ["RAW_HTML_DIR"] = "ambient-raw-html"
                os.environ["EMBEDDING_BASE_URL"] = TEST_AMBIENT_EMBEDDING_BASE_URL
                os.environ["LLM_ENDPOINT"] = TEST_AMBIENT_LLM_ENDPOINT
                os.environ["QDRANT_URL"] = TEST_AMBIENT_QDRANT_URL

                settings = Settings(root_dir=root)

                self.assertEqual(root, settings.root_dir)
                self.assertEqual("", settings.artifacts_dir_override)
                self.assertEqual("", settings.raw_html_dir_override)
                self.assertEqual("", settings.embedding_base_url)
                self.assertEqual("", settings.llm_endpoint)
                self.assertEqual("http://localhost:6333", settings.qdrant_url)
                self.assertEqual(root / "artifacts", settings.artifacts_dir)
                self.assertEqual(root / "data" / "bronze" / "raw_html", settings.raw_html_dir)
            finally:
                for key, value in old_env.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

    def test_default_artifact_paths_stay_inside_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            old_env = os.environ.get("ARTIFACTS_DIR")
            old_raw_env = os.environ.get("RAW_HTML_DIR")
            try:
                os.environ.pop("ARTIFACTS_DIR", None)
                os.environ.pop("RAW_HTML_DIR", None)
                settings = load_settings(root)
                self.assertEqual(root / "artifacts", settings.artifacts_dir)
                self.assertEqual(root / "artifacts" / "corpus", settings.corpus_dir)
                self.assertEqual(root / "artifacts" / "retrieval", settings.retrieval_dir)
                self.assertEqual(root / "data", settings.data_dir)
                self.assertEqual(root / "data" / "silver" / "normalized_docs.jsonl", settings.normalized_docs_path)
                self.assertEqual(root / "data" / "gold_corpus_ko" / "chunks.jsonl", settings.chunks_path)
                self.assertEqual(root / "data" / "gold_corpus_ko" / "bm25_corpus.jsonl", settings.bm25_corpus_path)
                self.assertEqual(root / "data" / "gold_manualbook_ko" / "playbook_documents.jsonl", settings.playbook_documents_path)
                self.assertEqual(root / "data" / "gold_manualbook_ko" / "playbooks", settings.playbook_books_dir)
                self.assertEqual(root / "artifacts" / "corpus" / "translation_lane_report.json", settings.translation_lane_report_path)
                self.assertEqual(root / "artifacts" / "runtime" / "recent_chat_session.json", settings.recent_chat_session_path)
                self.assertEqual(root / "artifacts" / "runtime" / "chat_turns.md", settings.chat_markdown_log_path)
                self.assertEqual(root / "artifacts" / "runtime" / "sessions", settings.runtime_sessions_dir)
                self.assertEqual(
                    root / "artifacts" / "runtime" / "sessions" / "session-123.json",
                    settings.session_snapshot_path("session-123"),
                )
                self.assertEqual(
                    root / "artifacts" / "runtime" / "sessions" / "27120e43.json",
                    settings.session_snapshot_path("27120e43-9f7c-4f7d-8d12-123456789abc"),
                )
                self.assertEqual(root / "artifacts" / "customer_packs", settings.customer_packs_dir)
                self.assertEqual(root / "artifacts" / "customer_packs" / "drafts", settings.customer_pack_drafts_dir)
                self.assertEqual(root / "artifacts" / "customer_packs" / "captures", settings.customer_pack_capture_dir)
                self.assertEqual(root / "artifacts" / "customer_packs" / "books", settings.customer_pack_books_dir)
                self.assertEqual(root / "data" / "bronze" / "raw_html", settings.raw_html_dir)
            finally:
                if old_env is None:
                    os.environ.pop("ARTIFACTS_DIR", None)
                else:
                    os.environ["ARTIFACTS_DIR"] = old_env
                if old_raw_env is None:
                    os.environ.pop("RAW_HTML_DIR", None)
                else:
                    os.environ["RAW_HTML_DIR"] = old_raw_env

    def test_artifacts_dir_override_moves_corpus_and_retrieval_together(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            external = root / "shared-artifacts"
            old_env = os.environ.get("ARTIFACTS_DIR")
            old_raw_env = os.environ.get("RAW_HTML_DIR")
            try:
                os.environ["ARTIFACTS_DIR"] = str(external)
                os.environ.pop("RAW_HTML_DIR", None)
                settings = load_settings(root)
                self.assertEqual(external.resolve(), settings.artifacts_dir)
                self.assertEqual((external / "corpus").resolve(), settings.corpus_dir)
                self.assertEqual((external / "retrieval").resolve(), settings.retrieval_dir)
                self.assertEqual((root / "data" / "silver" / "normalized_docs.jsonl").resolve(), settings.normalized_docs_path)
                self.assertEqual((root / "data" / "gold_corpus_ko" / "chunks.jsonl").resolve(), settings.chunks_path)
                self.assertEqual((root / "data" / "gold_corpus_ko" / "bm25_corpus.jsonl").resolve(), settings.bm25_corpus_path)
                self.assertEqual((root / "data" / "gold_manualbook_ko" / "playbook_documents.jsonl").resolve(), settings.playbook_documents_path)
                self.assertEqual((root / "data" / "gold_manualbook_ko" / "playbooks").resolve(), settings.playbook_books_dir)
                self.assertEqual((external / "corpus" / "translation_lane_report.json").resolve(), settings.translation_lane_report_path)
                self.assertEqual((external / "customer_packs").resolve(), settings.customer_packs_dir)
                self.assertEqual((external / "customer_packs" / "drafts").resolve(), settings.customer_pack_drafts_dir)
                self.assertEqual((external / "customer_packs" / "captures").resolve(), settings.customer_pack_capture_dir)
                self.assertEqual((external / "customer_packs" / "books").resolve(), settings.customer_pack_books_dir)
                self.assertEqual((root / "data" / "bronze" / "raw_html").resolve(), settings.raw_html_dir)
            finally:
                if old_env is None:
                    os.environ.pop("ARTIFACTS_DIR", None)
                else:
                    os.environ["ARTIFACTS_DIR"] = old_env
                if old_raw_env is None:
                    os.environ.pop("RAW_HTML_DIR", None)
                else:
                    os.environ["RAW_HTML_DIR"] = old_raw_env

    def test_raw_html_dir_override_moves_only_raw_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            external_raw = root.parent / "shared-raw-html"
            old_env = os.environ.get("ARTIFACTS_DIR")
            old_raw_env = os.environ.get("RAW_HTML_DIR")
            try:
                os.environ.pop("ARTIFACTS_DIR", None)
                os.environ["RAW_HTML_DIR"] = str(external_raw)
                settings = load_settings(root)
                self.assertEqual(
                    (root / "artifacts" / "corpus").resolve(),
                    settings.corpus_dir.resolve(),
                )
                self.assertEqual(external_raw.resolve(), settings.raw_html_dir.resolve())
            finally:
                if old_env is None:
                    os.environ.pop("ARTIFACTS_DIR", None)
                else:
                    os.environ["ARTIFACTS_DIR"] = old_env
                if old_raw_env is None:
                    os.environ.pop("RAW_HTML_DIR", None)
                else:
                    os.environ["RAW_HTML_DIR"] = old_raw_env

    def test_env_file_windows_style_relative_artifacts_dir_is_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "ARTIFACTS_DIR=shared-artifacts\n",
                encoding="utf-8",
            )
            old_env = os.environ.get("ARTIFACTS_DIR")
            old_raw_env = os.environ.get("RAW_HTML_DIR")
            try:
                os.environ.pop("ARTIFACTS_DIR", None)
                os.environ.pop("RAW_HTML_DIR", None)
                settings = load_settings(root)
                self.assertEqual(
                    (root / "shared-artifacts").resolve(),
                    settings.artifacts_dir,
                )
                self.assertEqual(
                    (root / "data" / "bronze" / "raw_html").resolve(),
                    settings.raw_html_dir,
                )
            finally:
                if old_env is None:
                    os.environ.pop("ARTIFACTS_DIR", None)
                else:
                    os.environ["ARTIFACTS_DIR"] = old_env
                if old_raw_env is None:
                    os.environ.pop("RAW_HTML_DIR", None)
                else:
                    os.environ["RAW_HTML_DIR"] = old_raw_env

    def test_source_manifest_path_override_supports_windows_style_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "SOURCE_MANIFEST_PATH=..\\shared-manifests\\approved.json\n",
                encoding="utf-8",
            )
            old_manifest = os.environ.get("SOURCE_MANIFEST_PATH")
            try:
                os.environ.pop("SOURCE_MANIFEST_PATH", None)
                settings = load_settings(root)
                self.assertEqual(
                    (root.parent / "shared-manifests" / "approved.json").resolve(),
                    settings.source_manifest_path,
                )
            finally:
                if old_manifest is None:
                    os.environ.pop("SOURCE_MANIFEST_PATH", None)
                else:
                    os.environ["SOURCE_MANIFEST_PATH"] = old_manifest

    def test_source_catalog_path_defaults_to_multiversion_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = load_settings(root)
            self.assertEqual(
                (root / "manifests" / "ocp_multiversion_html_single_catalog.json").resolve(),
                settings.source_catalog_path,
            )
            self.assertEqual(
                (root / "manifests" / "ocp_ko_4_20_approved_ko.json").resolve(),
                settings.source_manifest_path,
            )
            self.assertEqual(("4.16", "4.17", "4.18", "4.19", "4.20", "4.21"), settings.supported_ocp_versions)
            self.assertEqual(("ko", "en"), settings.supported_docs_languages)
            self.assertEqual(("html-single",), settings.supported_source_kinds)
            self.assertEqual("Play Book Studio", settings.app_label)
            self.assertEqual("openshift-4-20-core", settings.active_pack_id)
            self.assertEqual("OpenShift 4.20", settings.active_pack_label)
            self.assertEqual("/docs/ocp/4.20/ko/", settings.viewer_path_prefix)

    def test_pack_identity_changes_with_ocp_version_without_changing_app_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "OCP_VERSION=4.18\n"
                "DOCS_LANGUAGE=ko\n",
                encoding="utf-8",
            )
            settings = load_settings(root)
            self.assertEqual("Play Book Studio", settings.app_label)
            self.assertEqual("openshift-4-18-core", settings.active_pack_id)
            self.assertEqual("OpenShift 4.18", settings.active_pack_label)
            self.assertEqual(
                (root / "manifests" / "ocp_multiversion_html_single_catalog.json").resolve(),
                settings.source_catalog_path,
            )
            self.assertEqual(
                (root / "manifests" / "ocp_ko_4_18_approved_ko.json").resolve(),
                settings.source_manifest_path,
            )

    def test_source_catalog_scope_override_supports_versions_and_languages(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "SOURCE_CATALOG_VERSIONS=4.20,4.21\n"
                "SOURCE_CATALOG_LANGUAGES=ko\n",
                encoding="utf-8",
            )
            settings = load_settings(root)
            self.assertEqual(("4.20", "4.21"), settings.supported_ocp_versions)
            self.assertEqual(("ko",), settings.supported_docs_languages)
            self.assertEqual(
                [("4.20", "ko"), ("4.21", "ko")],
                [(pack.version, pack.language) for pack in settings.source_catalog_scope],
            )

    def test_source_catalog_path_override_supports_windows_style_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "SOURCE_CATALOG_PATH=..\\shared-manifests\\catalog.json\n",
                encoding="utf-8",
            )
            old_catalog = os.environ.get("SOURCE_CATALOG_PATH")
            try:
                os.environ.pop("SOURCE_CATALOG_PATH", None)
                settings = load_settings(root)
                self.assertEqual(
                    (root.parent / "shared-manifests" / "catalog.json").resolve(),
                    settings.source_catalog_path,
                )
            finally:
                if old_catalog is None:
                    os.environ.pop("SOURCE_CATALOG_PATH", None)
                else:
                    os.environ["SOURCE_CATALOG_PATH"] = old_catalog

    def test_embedding_model_defaults_to_dragonkue_bge_m3_ko(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            old_artifacts = os.environ.get("ARTIFACTS_DIR")
            old_raw = os.environ.get("RAW_HTML_DIR")
            old_base_url = os.environ.get("EMBEDDING_BASE_URL")
            old_embedding = os.environ.get("EMBEDDING_MODEL")
            old_device = os.environ.get("EMBEDDING_DEVICE")
            old_timeout = os.environ.get("EMBEDDING_TIMEOUT_SECONDS")
            try:
                os.environ.pop("ARTIFACTS_DIR", None)
                os.environ.pop("RAW_HTML_DIR", None)
                os.environ.pop("EMBEDDING_BASE_URL", None)
                os.environ.pop("EMBEDDING_MODEL", None)
                os.environ.pop("EMBEDDING_DEVICE", None)
                os.environ.pop("EMBEDDING_TIMEOUT_SECONDS", None)
                settings = load_settings(root)
                self.assertEqual("dragonkue/bge-m3-ko", settings.embedding_model)
                self.assertEqual("auto", settings.embedding_device)
                self.assertEqual("", settings.embedding_base_url)
                self.assertEqual(8.0, settings.embedding_timeout_seconds)
                self.assertFalse(settings.reranker_enabled)
                self.assertEqual("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1", settings.reranker_model)
                self.assertEqual(12, settings.reranker_top_n)
                self.assertEqual(8, settings.reranker_batch_size)
                self.assertEqual("auto", settings.reranker_device)
            finally:
                if old_artifacts is None:
                    os.environ.pop("ARTIFACTS_DIR", None)
                else:
                    os.environ["ARTIFACTS_DIR"] = old_artifacts
                if old_raw is None:
                    os.environ.pop("RAW_HTML_DIR", None)
                else:
                    os.environ["RAW_HTML_DIR"] = old_raw
                if old_base_url is None:
                    os.environ.pop("EMBEDDING_BASE_URL", None)
                else:
                    os.environ["EMBEDDING_BASE_URL"] = old_base_url
                if old_embedding is None:
                    os.environ.pop("EMBEDDING_MODEL", None)
                else:
                    os.environ["EMBEDDING_MODEL"] = old_embedding
                if old_device is None:
                    os.environ.pop("EMBEDDING_DEVICE", None)
                else:
                    os.environ["EMBEDDING_DEVICE"] = old_device
                if old_timeout is None:
                    os.environ.pop("EMBEDDING_TIMEOUT_SECONDS", None)
                else:
                    os.environ["EMBEDDING_TIMEOUT_SECONDS"] = old_timeout

    def test_historical_artifact_directories_are_ignored_when_semantic_dirs_are_expected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            external = root.parent / "shared-artifacts"
            (external / "legacy-corpus").mkdir(parents=True, exist_ok=True)
            (external / "legacy-retrieval").mkdir(parents=True, exist_ok=True)
            (external / "legacy-answering").mkdir(parents=True, exist_ok=True)
            (external / "legacy-runtime").mkdir(parents=True, exist_ok=True)
            old_env = os.environ.get("ARTIFACTS_DIR")
            old_raw_env = os.environ.get("RAW_HTML_DIR")
            try:
                os.environ["ARTIFACTS_DIR"] = str(external)
                os.environ.pop("RAW_HTML_DIR", None)
                settings = load_settings(root)
                self.assertEqual((external / "corpus").resolve(), settings.corpus_dir)
                self.assertEqual((external / "retrieval").resolve(), settings.retrieval_dir)
                self.assertEqual((external / "answering").resolve(), settings.answering_dir)
                self.assertEqual((external / "runtime").resolve(), settings.runtime_dir)
                self.assertEqual((root / "data" / "bronze" / "raw_html").resolve(), settings.raw_html_dir)
                self.assertEqual((external / "runtime" / "recent_chat_session.json").resolve(), settings.recent_chat_session_path)
                self.assertEqual((external / "runtime" / "chat_turns.md").resolve(), settings.chat_markdown_log_path)
                self.assertEqual((external / "runtime" / "sessions").resolve(), settings.runtime_sessions_dir)
                self.assertEqual(
                    (external / "runtime" / "sessions" / "session-456.json").resolve(),
                    settings.session_snapshot_path("session-456"),
                )
            finally:
                if old_env is None:
                    os.environ.pop("ARTIFACTS_DIR", None)
                else:
                    os.environ["ARTIFACTS_DIR"] = old_env
                if old_raw_env is None:
                    os.environ.pop("RAW_HTML_DIR", None)
                else:
                    os.environ["RAW_HTML_DIR"] = old_raw_env

    def test_llm_max_tokens_defaults_to_1100(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            old_llm_max_tokens = os.environ.get("LLM_MAX_TOKENS")
            try:
                os.environ.pop("LLM_MAX_TOKENS", None)
                settings = load_settings(root)
                self.assertEqual(1100, settings.llm_max_tokens)
            finally:
                if old_llm_max_tokens is None:
                    os.environ.pop("LLM_MAX_TOKENS", None)
                else:
                    os.environ["LLM_MAX_TOKENS"] = old_llm_max_tokens

    def test_env_file_expands_referenced_values_for_llm_api_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "LLM_API_KEY=${OPENAI_API_KEY}\n"
                "OPENAI_API_KEY=company-token\n",
                encoding="utf-8",
            )
            old_llm = os.environ.get("LLM_API_KEY")
            old_openai = os.environ.get("OPENAI_API_KEY")
            try:
                os.environ.pop("LLM_API_KEY", None)
                os.environ.pop("OPENAI_API_KEY", None)
                settings = load_settings(root)
                self.assertEqual("company-token", settings.llm_api_key)
                self.assertIsNone(os.environ.get("OPENAI_API_KEY"))
            finally:
                if old_llm is None:
                    os.environ.pop("LLM_API_KEY", None)
                else:
                    os.environ["LLM_API_KEY"] = old_llm
                if old_openai is None:
                    os.environ.pop("OPENAI_API_KEY", None)
                else:
                    os.environ["OPENAI_API_KEY"] = old_openai

    def test_env_file_overrides_existing_process_env_for_llm_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                f"LLM_ENDPOINT={TEST_RUNTIME_LLM_ENDPOINT}\n",
                encoding="utf-8",
            )
            old_llm_endpoint = os.environ.get("LLM_ENDPOINT")
            try:
                os.environ["LLM_ENDPOINT"] = TEST_STALE_PROCESS_LLM_ENDPOINT
                settings = load_settings(root)
                self.assertEqual(TEST_RUNTIME_LLM_ENDPOINT, settings.llm_endpoint)
                self.assertEqual(TEST_STALE_PROCESS_LLM_ENDPOINT, os.environ.get("LLM_ENDPOINT"))
            finally:
                if old_llm_endpoint is None:
                    os.environ.pop("LLM_ENDPOINT", None)
                else:
                    os.environ["LLM_ENDPOINT"] = old_llm_endpoint

    def test_env_file_values_do_not_leak_into_process_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                f"LLM_ENDPOINT={TEST_RUNTIME_OVERRIDE_LLM_ENDPOINT}\n"
                "OPENAI_API_KEY=shadow-token\n"
                "LLM_API_KEY=${OPENAI_API_KEY}\n"
                "EMBEDDING_MODEL=test-embedding-model\n",
                encoding="utf-8",
            )
            old_llm_endpoint = os.environ.get("LLM_ENDPOINT")
            old_openai = os.environ.get("OPENAI_API_KEY")
            old_llm_api_key = os.environ.get("LLM_API_KEY")
            old_embedding_model = os.environ.get("EMBEDDING_MODEL")
            try:
                os.environ.pop("LLM_ENDPOINT", None)
                os.environ.pop("OPENAI_API_KEY", None)
                os.environ.pop("LLM_API_KEY", None)
                os.environ.pop("EMBEDDING_MODEL", None)
                settings = load_settings(root)
                self.assertEqual(TEST_RUNTIME_OVERRIDE_LLM_ENDPOINT, settings.llm_endpoint)
                self.assertEqual("shadow-token", settings.llm_api_key)
                self.assertEqual("test-embedding-model", settings.embedding_model)
                self.assertIsNone(os.environ.get("LLM_ENDPOINT"))
                self.assertIsNone(os.environ.get("OPENAI_API_KEY"))
                self.assertIsNone(os.environ.get("LLM_API_KEY"))
                self.assertIsNone(os.environ.get("EMBEDDING_MODEL"))
            finally:
                if old_llm_endpoint is None:
                    os.environ.pop("LLM_ENDPOINT", None)
                else:
                    os.environ["LLM_ENDPOINT"] = old_llm_endpoint
                if old_openai is None:
                    os.environ.pop("OPENAI_API_KEY", None)
                else:
                    os.environ["OPENAI_API_KEY"] = old_openai
                if old_llm_api_key is None:
                    os.environ.pop("LLM_API_KEY", None)
                else:
                    os.environ["LLM_API_KEY"] = old_llm_api_key
                if old_embedding_model is None:
                    os.environ.pop("EMBEDDING_MODEL", None)
                else:
                    os.environ["EMBEDDING_MODEL"] = old_embedding_model

    def test_load_effective_env_resolves_dotenv_without_mutating_process_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "OPENAI_API_KEY=judge-token\n"
                "OPENAI_BASE_URL=https://judge.example/v1\n"
                "OPENAI_JUDGE_MODEL=gpt-test-judge\n"
                "OPENAI_EMBEDDING_MODEL=text-test-embedding\n"
                "LLM_API_KEY=${OPENAI_API_KEY}\n",
                encoding="utf-8",
            )
            old_openai_api_key = os.environ.get("OPENAI_API_KEY")
            old_openai_base_url = os.environ.get("OPENAI_BASE_URL")
            old_openai_judge_model = os.environ.get("OPENAI_JUDGE_MODEL")
            old_openai_embedding_model = os.environ.get("OPENAI_EMBEDDING_MODEL")
            old_llm_api_key = os.environ.get("LLM_API_KEY")
            try:
                os.environ.pop("OPENAI_API_KEY", None)
                os.environ.pop("OPENAI_BASE_URL", None)
                os.environ.pop("OPENAI_JUDGE_MODEL", None)
                os.environ.pop("OPENAI_EMBEDDING_MODEL", None)
                os.environ.pop("LLM_API_KEY", None)
                effective_env = load_effective_env(root)
                self.assertEqual("judge-token", effective_env.get("OPENAI_API_KEY"))
                self.assertEqual("https://judge.example/v1", effective_env.get("OPENAI_BASE_URL"))
                self.assertEqual("gpt-test-judge", effective_env.get("OPENAI_JUDGE_MODEL"))
                self.assertEqual("text-test-embedding", effective_env.get("OPENAI_EMBEDDING_MODEL"))
                self.assertEqual("judge-token", effective_env.get("LLM_API_KEY"))
                self.assertIsNone(os.environ.get("OPENAI_API_KEY"))
                self.assertIsNone(os.environ.get("OPENAI_BASE_URL"))
                self.assertIsNone(os.environ.get("OPENAI_JUDGE_MODEL"))
                self.assertIsNone(os.environ.get("OPENAI_EMBEDDING_MODEL"))
                self.assertIsNone(os.environ.get("LLM_API_KEY"))
            finally:
                if old_openai_api_key is None:
                    os.environ.pop("OPENAI_API_KEY", None)
                else:
                    os.environ["OPENAI_API_KEY"] = old_openai_api_key
                if old_openai_base_url is None:
                    os.environ.pop("OPENAI_BASE_URL", None)
                else:
                    os.environ["OPENAI_BASE_URL"] = old_openai_base_url
                if old_openai_judge_model is None:
                    os.environ.pop("OPENAI_JUDGE_MODEL", None)
                else:
                    os.environ["OPENAI_JUDGE_MODEL"] = old_openai_judge_model
                if old_openai_embedding_model is None:
                    os.environ.pop("OPENAI_EMBEDDING_MODEL", None)
                else:
                    os.environ["OPENAI_EMBEDDING_MODEL"] = old_openai_embedding_model
                if old_llm_api_key is None:
                    os.environ.pop("LLM_API_KEY", None)
                else:
                    os.environ["LLM_API_KEY"] = old_llm_api_key


if __name__ == "__main__":
    unittest.main()
