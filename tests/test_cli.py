from __future__ import annotations

import argparse
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from play_book_studio import cli


class _FakeReranker:
    def __init__(self, *, should_raise: bool = False) -> None:
        self.should_raise = should_raise
        self.model_name = "fake-reranker"
        self.warmup_calls = 0

    def warmup(self) -> bool:
        self.warmup_calls += 1
        if self.should_raise:
            raise RuntimeError("warmup boom")
        return True


class _FakeAnswerer:
    def __init__(self, reranker) -> None:
        self.retriever = SimpleNamespace(reranker=reranker)


class CliUiWarmupTests(unittest.TestCase):
    def test_run_ui_warms_reranker_before_serve(self) -> None:
        fake_answerer = _FakeAnswerer(_FakeReranker())
        args = argparse.Namespace(host="127.0.0.1", port=8765, no_browser=True)

        with patch("play_book_studio.cli._build_answerer", return_value=fake_answerer), patch(
            "play_book_studio.cli.serve"
        ) as serve_mock:
            exit_code = cli._run_ui(args)

        self.assertEqual(0, exit_code)
        self.assertEqual(1, fake_answerer.retriever.reranker.warmup_calls)
        serve_mock.assert_called_once_with(
            answerer=fake_answerer,
            root_dir=Path(cli.ROOT),
            host="127.0.0.1",
            port=8765,
            open_browser=False,
        )

    def test_run_ui_continues_when_reranker_warmup_fails(self) -> None:
        fake_answerer = _FakeAnswerer(_FakeReranker(should_raise=True))
        args = argparse.Namespace(host="127.0.0.1", port=8765, no_browser=True)

        with patch("play_book_studio.cli._build_answerer", return_value=fake_answerer), patch(
            "play_book_studio.cli.serve"
        ) as serve_mock:
            exit_code = cli._run_ui(args)

        self.assertEqual(0, exit_code)
        self.assertEqual(1, fake_answerer.retriever.reranker.warmup_calls)
        serve_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
