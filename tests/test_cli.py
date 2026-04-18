from __future__ import annotations

import argparse
import io
import unittest
from contextlib import redirect_stdout
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
    def test_run_ui_skips_reranker_warmup_by_default(self) -> None:
        fake_answerer = _FakeAnswerer(_FakeReranker())
        args = argparse.Namespace(
            host="127.0.0.1",
            port=8765,
            no_browser=True,
            warmup_reranker=False,
        )

        with patch("play_book_studio.cli._build_answerer", return_value=fake_answerer), patch(
            "play_book_studio.cli.serve"
        ) as serve_mock:
            exit_code = cli._run_ui(args)

        self.assertEqual(0, exit_code)
        self.assertEqual(0, fake_answerer.retriever.reranker.warmup_calls)
        serve_mock.assert_called_once()

    def test_run_ui_warms_reranker_when_requested(self) -> None:
        fake_answerer = _FakeAnswerer(_FakeReranker())
        args = argparse.Namespace(
            host="127.0.0.1",
            port=8765,
            no_browser=True,
            warmup_reranker=True,
        )

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
        args = argparse.Namespace(
            host="127.0.0.1",
            port=8765,
            no_browser=True,
            warmup_reranker=True,
        )

        with patch("play_book_studio.cli._build_answerer", return_value=fake_answerer), patch(
            "play_book_studio.cli.serve"
        ) as serve_mock:
            exit_code = cli._run_ui(args)

        self.assertEqual(0, exit_code)
        self.assertEqual(1, fake_answerer.retriever.reranker.warmup_calls)
        serve_mock.assert_called_once()

    def test_build_parser_accepts_graph_compact_command(self) -> None:
        args = cli.build_parser().parse_args(["graph-compact"])

        self.assertEqual("graph-compact", args.command)
        self.assertIsNone(args.output)

    def test_build_parser_accepts_maintenance_smoke_command(self) -> None:
        args = cli.build_parser().parse_args(["maintenance-smoke"])

        self.assertEqual("maintenance-smoke", args.command)
        self.assertIsNone(args.output)
        self.assertEqual("OpenShift architecture overview", args.query)

    def test_build_parser_accepts_private_lane_smoke_command(self) -> None:
        args = cli.build_parser().parse_args(["private-lane-smoke"])

        self.assertEqual("private-lane-smoke", args.command)
        self.assertIsNone(args.output)
        self.assertEqual("http://127.0.0.1:8765", args.ui_base_url)
        self.assertEqual("{token} 문서를 보여줘", args.query_template)

    def test_run_graph_compact_writes_summary(self) -> None:
        args = argparse.Namespace(output=Path("custom-compact.json"))
        fake_settings = object()
        stdout = io.StringIO()
        payload = {
            "book_count": 2,
            "relation_count": 1,
            "summary": {
                "relation_group_counts": {
                    "shared_operator_names": 1,
                }
            },
        }

        with (
            patch("play_book_studio.cli.load_settings", return_value=fake_settings) as load_settings_mock,
            patch(
                "play_book_studio.cli.write_graph_sidecar_compact_from_artifacts",
                return_value=(Path("custom-compact.json"), payload),
            ) as write_mock,
            redirect_stdout(stdout),
        ):
            exit_code = cli._run_graph_compact(args)

        self.assertEqual(0, exit_code)
        load_settings_mock.assert_called_once_with(Path(cli.ROOT))
        write_mock.assert_called_once_with(fake_settings, output_path=Path("custom-compact.json"))
        rendered = stdout.getvalue()
        self.assertIn("wrote graph sidecar compact artifact: custom-compact.json", rendered)
        self.assertIn('"book_count": 2', rendered)
        self.assertIn('"relation_count": 1', rendered)

    def test_run_maintenance_smoke_writes_summary(self) -> None:
        args = argparse.Namespace(
            output=Path("maintenance-smoke.json"),
            ui_base_url="http://127.0.0.1:8765",
            query="OpenShift architecture overview",
        )
        stdout = io.StringIO()
        payload = {
            "summary": {
                "ok": True,
                "compact_ready": True,
                "health_ok": True,
                "chat_ok": True,
            }
        }

        with (
            patch(
                "play_book_studio.cli.write_runtime_maintenance_smoke",
                return_value=(Path("maintenance-smoke.json"), payload),
            ) as smoke_mock,
            redirect_stdout(stdout),
        ):
            exit_code = cli._run_maintenance_smoke(args)

        self.assertEqual(0, exit_code)
        smoke_mock.assert_called_once_with(
            Path(cli.ROOT),
            output_path=Path("maintenance-smoke.json"),
            ui_base_url="http://127.0.0.1:8765",
            query="OpenShift architecture overview",
        )
        rendered = stdout.getvalue()
        self.assertIn("wrote runtime maintenance smoke: maintenance-smoke.json", rendered)
        self.assertIn('"compact_ready": true', rendered)

    def test_run_private_lane_smoke_writes_summary(self) -> None:
        args = argparse.Namespace(
            output=Path("private-lane-smoke.json"),
            ui_base_url="http://127.0.0.1:8878",
            query_template="{token} 문서를 보여줘",
        )
        stdout = io.StringIO()
        payload = {
            "summary": {
                "ok": True,
                "ingest_ok": True,
                "selected_chat_private_hit": True,
                "no_leak_ok": True,
            }
        }

        with (
            patch(
                "play_book_studio.cli.write_private_lane_smoke",
                return_value=(Path("private-lane-smoke.json"), payload),
            ) as smoke_mock,
            redirect_stdout(stdout),
        ):
            exit_code = cli._run_private_lane_smoke(args)

        self.assertEqual(0, exit_code)
        smoke_mock.assert_called_once_with(
            Path(cli.ROOT),
            output_path=Path("private-lane-smoke.json"),
            ui_base_url="http://127.0.0.1:8878",
            query_template="{token} 문서를 보여줘",
        )
        rendered = stdout.getvalue()
        self.assertIn("wrote private lane smoke: private-lane-smoke.json", rendered)
        self.assertIn('"selected_chat_private_hit": true', rendered)


if __name__ == "__main__":
    unittest.main()
