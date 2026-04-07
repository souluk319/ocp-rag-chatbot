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

from ocp_rag_part1.settings import load_settings


class SettingsPathTests(unittest.TestCase):
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
                self.assertEqual(root / "artifacts" / "part1", settings.part1_dir)
                self.assertEqual(root / "artifacts" / "part2", settings.part2_dir)
                self.assertEqual(root / "artifacts" / "doc_to_book", settings.doc_to_book_dir)
                self.assertEqual(root / "artifacts" / "doc_to_book" / "drafts", settings.doc_to_book_drafts_dir)
                self.assertEqual(root / "artifacts" / "doc_to_book" / "captures", settings.doc_to_book_capture_dir)
                self.assertEqual(root / "artifacts" / "doc_to_book" / "books", settings.doc_to_book_books_dir)
                self.assertEqual(root / "artifacts" / "part1" / "raw_html", settings.raw_html_dir)
            finally:
                if old_env is None:
                    os.environ.pop("ARTIFACTS_DIR", None)
                else:
                    os.environ["ARTIFACTS_DIR"] = old_env
                if old_raw_env is None:
                    os.environ.pop("RAW_HTML_DIR", None)
                else:
                    os.environ["RAW_HTML_DIR"] = old_raw_env

    def test_artifacts_dir_override_moves_part1_and_part2_together(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            external = root.parent / "shared-artifacts"
            old_env = os.environ.get("ARTIFACTS_DIR")
            old_raw_env = os.environ.get("RAW_HTML_DIR")
            try:
                os.environ["ARTIFACTS_DIR"] = str(external)
                os.environ.pop("RAW_HTML_DIR", None)
                settings = load_settings(root)
                self.assertEqual(external.resolve(), settings.artifacts_dir)
                self.assertEqual((external / "part1").resolve(), settings.part1_dir)
                self.assertEqual((external / "part2").resolve(), settings.part2_dir)
                self.assertEqual((external / "doc_to_book").resolve(), settings.doc_to_book_dir)
                self.assertEqual((external / "doc_to_book" / "drafts").resolve(), settings.doc_to_book_drafts_dir)
                self.assertEqual((external / "doc_to_book" / "captures").resolve(), settings.doc_to_book_capture_dir)
                self.assertEqual((external / "doc_to_book" / "books").resolve(), settings.doc_to_book_books_dir)
                self.assertEqual((external / "part1" / "raw_html").resolve(), settings.raw_html_dir)
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
                    (root / "artifacts" / "part1").resolve(),
                    settings.part1_dir.resolve(),
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
                "ARTIFACTS_DIR=..\\shared-artifacts\n",
                encoding="utf-8",
            )
            old_env = os.environ.get("ARTIFACTS_DIR")
            old_raw_env = os.environ.get("RAW_HTML_DIR")
            try:
                os.environ.pop("ARTIFACTS_DIR", None)
                os.environ.pop("RAW_HTML_DIR", None)
                settings = load_settings(root)
                self.assertEqual(
                    (root.parent / "shared-artifacts").resolve(),
                    settings.artifacts_dir,
                )
                self.assertEqual(
                    (root.parent / "shared-artifacts" / "part1" / "raw_html").resolve(),
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
                self.assertEqual("company-token", os.environ.get("OPENAI_API_KEY"))
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
                "LLM_ENDPOINT=http://10.0.1.201:8010/v1\n",
                encoding="utf-8",
            )
            old_llm_endpoint = os.environ.get("LLM_ENDPOINT")
            try:
                os.environ["LLM_ENDPOINT"] = "http://old-server:8080/v1"
                settings = load_settings(root)
                self.assertEqual("http://10.0.1.201:8010/v1", settings.llm_endpoint)
                self.assertEqual("http://10.0.1.201:8010/v1", os.environ.get("LLM_ENDPOINT"))
            finally:
                if old_llm_endpoint is None:
                    os.environ.pop("LLM_ENDPOINT", None)
                else:
                    os.environ["LLM_ENDPOINT"] = old_llm_endpoint


if __name__ == "__main__":
    unittest.main()
