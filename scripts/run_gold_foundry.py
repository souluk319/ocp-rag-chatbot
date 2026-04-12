from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import load_settings
from play_book_studio.ingestion.foundry_orchestrator import (
    load_foundry_profiles,
    run_foundry_profile,
    run_foundry_profile_with_retry,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a named gold foundry orchestration profile.",
    )
    parser.add_argument(
        "--profile",
        default="morning_gate",
        help="Configured foundry profile id from pipelines/foundry_routines.json.",
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="Print configured profile ids and exit.",
    )
    parser.add_argument(
        "--fail-on-release-blocking",
        action="store_true",
        help="Return exit code 1 when the final judge verdict blocks release.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=0,
        help="Retry transient foundry failures this many times.",
    )
    parser.add_argument(
        "--retry-delay-seconds",
        type=int,
        default=300,
        help="Delay between retry attempts for transient foundry failures.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    profiles = load_foundry_profiles(settings)
    if args.list_profiles:
        print(
            json.dumps(
                {
                    profile_id: {
                        "name": profile.name,
                        "cadence": profile.cadence,
                        "days": list(profile.days),
                        "time": profile.time,
                        "minute": profile.minute,
                        "interval_hours": profile.interval_hours,
                        "jobs": list(profile.jobs),
                    }
                    for profile_id, profile in profiles.items()
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.profile not in profiles:
        available_profiles = ", ".join(sorted(profiles))
        raise SystemExit(
            f"unknown foundry profile: {args.profile}. Available profiles: {available_profiles}"
        )

    if args.retries > 0:
        report = run_foundry_profile_with_retry(
            settings,
            args.profile,
            retries=args.retries,
            retry_delay_seconds=args.retry_delay_seconds,
        )
    else:
        report = run_foundry_profile(settings, args.profile)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.fail_on_release_blocking and bool(report["verdict"]["release_blocking"]):
        return 1
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(
        run_guarded_script(
            main,
            __file__,
            allowed_launchers={"codex_python.ps1", "run_foundry_task.ps1"},
            launcher_hint="scripts/codex_python.ps1 or scripts/run_foundry_task.ps1",
        )
    )
