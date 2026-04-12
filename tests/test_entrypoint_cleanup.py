from __future__ import annotations

import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scripts import register_foundry_schedules
from scripts import check_runtime_endpoints
from scripts import build_source_approval
from scripts import build_synthesis_lane
from scripts import build_translation_draft_manifest
from scripts import generate_translation_drafts
from scripts import promote_translation_gold
from scripts import run_answer_eval
from scripts import run_gold_foundry
from scripts import run_ingestion
from scripts import run_ragas_eval
from scripts import validate_ingestion_outputs
from play_book_studio.execution_guard import run_guarded_script


class PlayBookCmdCleanupTests(unittest.TestCase):
    def test_play_book_cmd_requires_venv_and_preflight_before_running(self) -> None:
        content = (ROOT / "play_book.cmd").read_text(encoding="utf-8")

        self.assertIn('if not exist "%VENV_PY%" (', content)
        self.assertIn("Missing required virtual environment", content)
        self.assertIn('if not exist "%PWSH%" (', content)
        self.assertIn("Missing required PowerShell 7", content)
        self.assertIn('codex_preflight.ps1', content)
        self.assertIn('set "ARTIFACTS_SCOPE_ROOT=%ROOT%artifacts"', content)
        self.assertIn('if /I "%%A"=="ARTIFACTS_DIR" set "ARTIFACTS_DIR_OVERRIDE=%%B"', content)
        self.assertIn('set "PLAY_BOOK_WRITE_SCOPE=', content)
        self.assertIn('set "PLAY_BOOK_VERIFY_CMD=', content)
        self.assertIn('%ARTIFACTS_SCOPE_ROOT%\\answering\\answer_log.jsonl', content)
        self.assertIn('%ARTIFACTS_SCOPE_ROOT%\\answering\\answer_eval_report.json', content)
        self.assertIn('%ARTIFACTS_SCOPE_ROOT%\\runtime\\runtime_report.json', content)
        self.assertIn('set "PLAY_BOOK_VERIFY_CMD=%ROOT%play_book.cmd %*"', content)
        self.assertIn('-WriteScope "%PLAY_BOOK_WRITE_SCOPE%"', content)
        self.assertIn('-VerifyCmd "%PLAY_BOOK_VERIFY_CMD%"', content)
        self.assertIn('set "PLAY_BOOK_LAUNCHER=play_book.cmd"', content)
        self.assertNotIn("else (", content)
        self.assertNotIn('python "%ROOT%scripts\\play_book.py" %*', content)

    def test_play_book_python_entrypoint_rejects_direct_execution(self) -> None:
        content = (ROOT / "scripts" / "play_book.py").read_text(encoding="utf-8")

        self.assertIn("run_guarded_script(", content)
        self.assertIn('launcher_hint="play_book.cmd from the repo root"', content)


class CodexPreflightCleanupTests(unittest.TestCase):
    def test_codex_preflight_is_powershell_native_and_records_report(self) -> None:
        content = (ROOT / "scripts" / "codex_preflight.ps1").read_text(encoding="utf-8")

        self.assertIn("Missing required virtual environment", content)
        self.assertIn("$report.git_bash_available", content)
        self.assertIn("Missing required write_scope", content)
        self.assertIn("Missing required verify_cmd", content)
        self.assertIn("Set-Location -LiteralPath $Root", content)
        self.assertIn("Get-NetTCPConnection", content)
        self.assertIn("codex_preflight.json", content)
        self.assertIn("UI port", content)
        self.assertIn('rev-parse --abbrev-ref HEAD', content)
        self.assertIn('rev-parse --show-toplevel', content)
        self.assertIn("Dirty main worktree is blocked", content)
        self.assertIn("verify_cmd", content)

    def test_codex_git_bash_wrapper_is_repo_scoped(self) -> None:
        content = (ROOT / "scripts" / "codex_git_bash.ps1").read_text(encoding="utf-8")

        self.assertIn("Missing required Git Bash", content)
        self.assertIn("Missing command. Use codex_git_bash.ps1", content)
        self.assertIn("cd '$repoRootForBash' &&", content)
        self.assertIn("& $GitBash -lc", content)

    def test_codex_python_wrapper_requires_scope_and_verify_contract(self) -> None:
        content = (ROOT / "scripts" / "codex_python.ps1").read_text(encoding="utf-8")

        self.assertIn("[Parameter(Mandatory = $true)]", content)
        self.assertIn("[string]$WriteScope", content)
        self.assertIn("[string]$VerifyCmd", content)
        self.assertIn("Set-Location -LiteralPath $Root", content)
        self.assertIn('$env:PLAY_BOOK_LAUNCHER = "codex_python.ps1"', content)
        self.assertIn('$env:PLAY_BOOK_WRITE_SCOPE = $WriteScope', content)
        self.assertIn('$env:PLAY_BOOK_VERIFY_CMD = $VerifyCmd', content)
        self.assertIn("& $Preflight -WriteScope $WriteScope -VerifyCmd $VerifyCmd", content)


class RunGoldFoundryCleanupTests(unittest.TestCase):
    def _fake_profile(self) -> SimpleNamespace:
        return SimpleNamespace(
            profile_id="morning_gate",
            name="Morning Gold Gate",
            description="daily gate",
            cadence="daily",
            days=("Mon",),
            time="08:30",
            minute=None,
            interval_hours=None,
            jobs=("validation_gate",),
        )

    def test_parser_does_not_accept_report_dir_override(self) -> None:
        parser = run_gold_foundry.build_parser()
        option_strings = {
            option
            for action in parser._actions
            for option in action.option_strings
        }

        self.assertNotIn("--report-dir", option_strings)

    def test_main_uses_fixed_report_dir_for_supported_profile(self) -> None:
        fake_settings = SimpleNamespace(root_dir=ROOT)

        with patch.object(run_gold_foundry, "load_settings", return_value=fake_settings), patch.object(
            run_gold_foundry, "load_foundry_profiles", return_value={"morning_gate": self._fake_profile()}
        ), patch.object(
            run_gold_foundry, "run_foundry_profile", return_value={"verdict": {"release_blocking": False}}
        ) as runner, patch.object(
            sys,
            "argv",
            ["run_gold_foundry.py", "--profile", "morning_gate"],
        ):
            exit_code = run_gold_foundry.main()

        self.assertEqual(0, exit_code)
        runner.assert_called_once_with(
            fake_settings,
            "morning_gate",
        )

    def test_main_rejects_unknown_profile_before_running(self) -> None:
        fake_settings = SimpleNamespace(root_dir=ROOT)

        with patch.object(run_gold_foundry, "load_settings", return_value=fake_settings), patch.object(
            run_gold_foundry, "load_foundry_profiles", return_value={"morning_gate": self._fake_profile()}
        ), patch.object(run_gold_foundry, "run_foundry_profile") as runner, patch.object(
            sys,
            "argv",
            ["run_gold_foundry.py", "--profile", "legacy_gate"],
        ):
            with self.assertRaises(SystemExit) as exc_info:
                run_gold_foundry.main()

        self.assertIn("unknown foundry profile: legacy_gate", str(exc_info.exception))
        runner.assert_not_called()

    def test_main_lists_profiles_without_running_foundry(self) -> None:
        fake_settings = SimpleNamespace(root_dir=ROOT)

        with patch.object(run_gold_foundry, "load_settings", return_value=fake_settings), patch.object(
            run_gold_foundry, "load_foundry_profiles", return_value={"morning_gate": self._fake_profile()}
        ), patch.object(run_gold_foundry, "run_foundry_profile") as runner, patch.object(
            sys,
            "argv",
            ["run_gold_foundry.py", "--list-profiles"],
        ), redirect_stdout(io.StringIO()) as stdout:
            exit_code = run_gold_foundry.main()

        self.assertEqual(0, exit_code)
        self.assertIn('"morning_gate"', stdout.getvalue())
        runner.assert_not_called()


class FoundryWrapperCleanupTests(unittest.TestCase):
    def test_run_foundry_task_requires_venv_and_has_no_report_dir_or_system_python_fallback(self) -> None:
        content = (ROOT / "scripts" / "run_foundry_task.ps1").read_text(encoding="utf-8")

        self.assertIn("Missing required virtual environment", content)
        self.assertIn("Missing required preflight script", content)
        self.assertIn("Set-Location -LiteralPath $Root", content)
        self.assertIn('$WriteScope = "reports\\\\build_logs\\\\task_scheduler;reports\\\\build_logs\\\\foundry_runs"', content)
        self.assertIn('$env:PLAY_BOOK_LAUNCHER = "run_foundry_task.ps1"', content)
        self.assertIn('& $Preflight -WriteScope $WriteScope -VerifyCmd $VerifyCmd "foundry" "--profile" $Profile', content)
        self.assertIn('`"$Python`" `"$Runner`" --profile $Profile', content)
        self.assertNotIn('$Python = "python"', content)
        self.assertNotIn("--report-dir", content)

    def test_register_foundry_schedules_parser_does_not_accept_report_dir_override(self) -> None:
        parser = register_foundry_schedules.build_parser()
        option_strings = {
            option
            for action in parser._actions
            for option in action.option_strings
        }

        self.assertNotIn("--report-dir", option_strings)
        self.assertNotIn("--log-dir", option_strings)


class RunIngestionCleanupTests(unittest.TestCase):
    def test_run_ingestion_is_full_run_only_and_has_no_partial_path_flags(self) -> None:
        content = (ROOT / "scripts" / "run_ingestion.py").read_text(encoding="utf-8")

        for flag in (
            "--refresh-manifest",
            "--collect-subset",
            "--process-subset",
            "--collect-limit",
            "--process-limit",
            "--force-collect",
            "--skip-embeddings",
            "--skip-qdrant",
            "--source-manifest-path",
        ):
            self.assertNotIn(flag, content)

        fake_settings = SimpleNamespace(root_dir=ROOT)
        fake_log = SimpleNamespace(
            manifest_count=1,
            collected_count=2,
            normalized_count=3,
            chunk_count=4,
            embedded_count=5,
            qdrant_upserted_count=6,
            errors=[],
        )

        with patch.object(run_ingestion, "load_settings", return_value=fake_settings), patch.object(
            run_ingestion,
            "run_ingestion_pipeline",
            return_value=fake_log,
        ) as runner:
            exit_code = run_ingestion.main()

        self.assertEqual(0, exit_code)
        runner.assert_called_once_with(
            fake_settings,
            refresh_manifest=False,
            collect_subset="all",
            process_subset="all",
            collect_limit=None,
            process_limit=None,
            force_collect=False,
            skip_embeddings=False,
            skip_qdrant=False,
        )


class LegacyEvalWrapperCleanupTests(unittest.TestCase):
    def test_run_answer_eval_reuses_canonical_runtime_defaults(self) -> None:
        parser = run_answer_eval.build_parser()
        args = parser.parse_args([])

        self.assertEqual(8, args.top_k)
        self.assertEqual(20, args.candidate_k)
        self.assertEqual(6, args.max_context_chunks)

    def test_run_ragas_eval_reuses_canonical_runtime_defaults(self) -> None:
        parser = run_ragas_eval.build_parser()
        args = parser.parse_args([])

        self.assertEqual(8, args.top_k)
        self.assertEqual(20, args.candidate_k)
        self.assertEqual(6, args.max_context_chunks)


class CleanupBypassRemovalTests(unittest.TestCase):
    def test_promote_translation_gold_parser_does_not_accept_skip_qdrant(self) -> None:
        parser = promote_translation_gold.build_parser()
        option_strings = {
            option
            for action in parser._actions
            for option in action.option_strings
        }

        self.assertNotIn("--skip-qdrant", option_strings)
        self.assertNotIn("--report-path", option_strings)

    def test_promote_translation_gold_always_syncs_qdrant(self) -> None:
        fake_settings = SimpleNamespace(root_dir=ROOT)
        fake_report = {"status": "ok"}

        with patch.object(promote_translation_gold, "load_settings", return_value=fake_settings), patch.object(
            promote_translation_gold,
            "promote_translation_gold",
            return_value=fake_report,
        ) as runner, patch.object(
            sys,
            "argv",
            ["promote_translation_gold.py"],
        ), redirect_stdout(io.StringIO()):
            exit_code = promote_translation_gold.main()

        self.assertEqual(0, exit_code)
        runner.assert_called_once_with(
            fake_settings,
            slugs=None,
            generate_first=False,
            force_collect=False,
            force_regenerate=False,
            sync_qdrant=True,
            refresh_synthesis_report=True,
        )

    def test_validate_ingestion_outputs_parser_does_not_accept_skip_qdrant_id_check(self) -> None:
        parser = validate_ingestion_outputs.build_parser()
        option_strings = {
            option
            for action in parser._actions
            for option in action.option_strings
        }

        self.assertNotIn("--skip-qdrant-id-check", option_strings)

    def test_validate_ingestion_outputs_always_checks_qdrant_ids(self) -> None:
        fake_settings = SimpleNamespace(corpus_dir=ROOT)
        fake_report = {"status": "ok"}

        with patch.object(validate_ingestion_outputs, "load_settings", return_value=fake_settings), patch.object(
            validate_ingestion_outputs,
            "build_validation_report",
            return_value=fake_report,
        ) as builder, patch.object(
            sys,
            "argv",
            ["validate_ingestion_outputs.py"],
        ), redirect_stdout(io.StringIO()):
            exit_code = validate_ingestion_outputs.main()

        self.assertEqual(0, exit_code)
        builder.assert_called_once_with(
            fake_settings,
            expected_process_subset="high-value",
            include_qdrant_id_check=True,
        )

    def test_build_source_approval_parser_does_not_accept_output_override_flags(self) -> None:
        content = (ROOT / "scripts" / "build_source_approval.py").read_text(encoding="utf-8")

        for flag in (
            "--report-path",
            "--gap-report-path",
            "--translation-lane-report-path",
            "--output-manifest-path",
        ):
            self.assertNotIn(flag, content)

        self.assertIn("settings.source_approval_report_path", content)
        self.assertIn("settings.corpus_gap_report_path", content)
        self.assertIn("settings.translation_lane_report_path", content)
        self.assertIn("settings.source_manifest_path", content)

    def test_build_translation_draft_manifest_parser_does_not_accept_output_override(self) -> None:
        content = (ROOT / "scripts" / "build_translation_draft_manifest.py").read_text(encoding="utf-8")

        self.assertNotIn("--output-manifest-path", content)
        self.assertIn("settings.translation_draft_manifest_path", content)

    def test_generate_translation_drafts_parser_does_not_accept_report_override(self) -> None:
        content = (ROOT / "scripts" / "generate_translation_drafts.py").read_text(encoding="utf-8")

        self.assertNotIn("--report-path", content)
        self.assertIn("DEFAULT_REPORT_PATH", content)

    def test_build_synthesis_lane_parser_does_not_accept_report_override(self) -> None:
        content = (ROOT / "scripts" / "build_synthesis_lane.py").read_text(encoding="utf-8")

        self.assertNotIn("--report-path", content)
        self.assertIn("write_synthesis_lane_outputs(settings)", content)

    def test_runtime_endpoint_check_parser_does_not_accept_degraded_flags(self) -> None:
        parser = check_runtime_endpoints.build_parser()
        option_strings = {
            option
            for action in parser._actions
            for option in action.option_strings
        }

        self.assertNotIn("--skip-samples", option_strings)
        self.assertNotIn("--write-legacy-copy", option_strings)

    def test_runtime_endpoint_check_always_runs_full_probe(self) -> None:
        fake_output_path = ROOT / "runtime_report.json"
        fake_report = {"status": "ok"}

        with patch.object(
            check_runtime_endpoints,
            "write_runtime_report",
            return_value=(fake_output_path, fake_report),
        ) as writer, patch.object(
            sys,
            "argv",
            ["check_runtime_endpoints.py"],
        ), redirect_stdout(io.StringIO()):
            exit_code = check_runtime_endpoints.main()

        self.assertEqual(0, exit_code)
        writer.assert_called_once_with(
            ROOT,
            output_path=None,
            ui_base_url="http://127.0.0.1:8765",
            recent_turns=3,
            sample=True,
        )


class ExecutionGuardTests(unittest.TestCase):
    def test_run_guarded_script_blocks_direct_execution_without_launcher(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit) as exc_info:
                run_guarded_script(lambda: 0, "scripts/run_ingestion.py")

        self.assertIn("Direct execution is blocked", str(exc_info.exception))

    def test_run_guarded_script_requires_write_scope(self) -> None:
        with patch.dict(
            os.environ,
            {
                "PLAY_BOOK_LAUNCHER": "codex_python.ps1",
                "PLAY_BOOK_VERIFY_CMD": "pytest -q",
            },
            clear=True,
        ):
            with self.assertRaises(SystemExit) as exc_info:
                run_guarded_script(lambda: 0, "scripts/run_ingestion.py")

        self.assertIn("PLAY_BOOK_WRITE_SCOPE", str(exc_info.exception))

    def test_run_guarded_script_requires_verify_cmd(self) -> None:
        with patch.dict(
            os.environ,
            {
                "PLAY_BOOK_LAUNCHER": "codex_python.ps1",
                "PLAY_BOOK_WRITE_SCOPE": "data/bronze",
            },
            clear=True,
        ):
            with self.assertRaises(SystemExit) as exc_info:
                run_guarded_script(lambda: 0, "scripts/run_ingestion.py")

        self.assertIn("PLAY_BOOK_VERIFY_CMD", str(exc_info.exception))

    def test_run_guarded_script_accepts_complete_contract(self) -> None:
        with patch.dict(
            os.environ,
            {
                "PLAY_BOOK_LAUNCHER": "codex_python.ps1",
                "PLAY_BOOK_WRITE_SCOPE": "data/bronze",
                "PLAY_BOOK_VERIFY_CMD": "pytest -q",
            },
            clear=True,
        ):
            result = run_guarded_script(lambda: 7, "scripts/run_ingestion.py")

        self.assertEqual(7, result)

    def test_all_standalone_python_scripts_use_shared_execution_guard(self) -> None:
        scripts_dir = ROOT / "scripts"
        for path in sorted(scripts_dir.glob("*.py")):
            content = path.read_text(encoding="utf-8")
            if 'if __name__ == "__main__":' not in content:
                continue
            self.assertIn(
                "run_guarded_script(",
                content,
                msg=f"{path.name} is missing the shared execution guard",
            )

    def test_task_board_phase3_tracks_write_scope_and_verify_cmd(self) -> None:
        content = (ROOT / "TASK_BOARD.yaml").read_text(encoding="utf-8")

        self.assertIn("id: P3-E1-T1", content)
        self.assertIn("id: P3-E1-T2", content)
        self.assertIn("id: P3-E1-T3", content)
        self.assertIn("write_scope:", content)
        self.assertIn("verify_cmd:", content)
        self.assertIn("../ocp-rag-chatbot-data/answering/answer_eval_report.json", content)
        self.assertIn("../ocp-rag-chatbot-data/retrieval/retrieval_eval_report.json", content)
        self.assertIn(
            "scripts/codex_python.ps1 -ScriptPath scripts/run_retrieval_eval.py -WriteScope ../ocp-rag-chatbot-data/retrieval/retrieval_eval_report.json",
            content,
        )


if __name__ == "__main__":
    unittest.main()
