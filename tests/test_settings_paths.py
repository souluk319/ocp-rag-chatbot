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
            try:
                os.environ.pop("ARTIFACTS_DIR", None)
                os.environ.pop("RAW_HTML_DIR", None)
                os.environ.pop("EMBEDDING_BASE_URL", None)
                os.environ.pop("EMBEDDING_MODEL", None)
                settings = load_settings(root)
                self.assertEqual("dragonkue/bge-m3-ko", settings.embedding_model)
                self.assertEqual("", settings.embedding_base_url)
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


if __name__ == "__main__":
    unittest.main()
