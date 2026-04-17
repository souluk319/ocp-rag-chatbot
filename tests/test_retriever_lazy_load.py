from __future__ import annotations

import importlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from play_book_studio.config.settings import load_settings


class RetrieverLazyLoadTests(unittest.TestCase):
    def _reset_modules(self) -> None:
        sys.modules.pop("play_book_studio.retrieval.retriever", None)
        sys.modules.pop("play_book_studio.retrieval.reranker", None)

    def test_importing_retriever_does_not_import_reranker_module(self) -> None:
        self._reset_modules()

        try:
            importlib.import_module("play_book_studio.retrieval.retriever")
            self.assertNotIn("play_book_studio.retrieval.reranker", sys.modules)
        finally:
            self._reset_modules()

    def test_from_settings_keeps_reranker_unloaded_when_disabled(self) -> None:
        self._reset_modules()

        try:
            retriever_module = importlib.import_module("play_book_studio.retrieval.retriever")
            with tempfile.TemporaryDirectory() as tmpdir:
                root = Path(tmpdir)
                (root / ".env").write_text("ARTIFACTS_DIR=artifacts\nRERANKER_ENABLED=false\n", encoding="utf-8")
                settings = load_settings(root)

                with patch.object(retriever_module.BM25Index, "from_jsonl", return_value=object()):
                    retriever = retriever_module.ChatRetriever.from_settings(
                        settings,
                        enable_vector=False,
                        enable_reranker=False,
                    )

            self.assertIsNone(retriever.reranker)
            self.assertNotIn("play_book_studio.retrieval.reranker", sys.modules)
        finally:
            self._reset_modules()


if __name__ == "__main__":
    unittest.main()
