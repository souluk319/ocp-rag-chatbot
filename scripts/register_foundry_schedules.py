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
from play_book_studio.ingestion.foundry_scheduler import (
    build_foundry_schedule_tasks,
    register_foundry_schedule_tasks,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Register Windows Task Scheduler entries for gold foundry profiles.",
    )
    parser.add_argument(
        "--profile",
        action="append",
        default=[],
        help="Restrict registration to one or more profile ids.",
    )
    parser.add_argument(
        "--task-prefix",
        default="PlayBookStudio\\Foundry",
        help="Task Scheduler folder/name prefix.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=2,
        help="Retry transient foundry failures this many times inside each scheduled run.",
    )
    parser.add_argument(
        "--retry-delay-seconds",
        type=int,
        default=900,
        help="Delay between retry attempts for scheduled runs.",
    )
    parser.add_argument(
        "--no-replace",
        action="store_true",
        help="Do not overwrite an existing scheduled task with the same name.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually register tasks. Without this flag, print the planned task definitions only.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)

    tasks = build_foundry_schedule_tasks(
        settings,
        selected_profiles=tuple(args.profile) or None,
        task_prefix=args.task_prefix,
        retries=args.retries,
        retry_delay_seconds=args.retry_delay_seconds,
        replace=not args.no_replace,
    )
    payload = {
        "task_count": len(tasks),
        "tasks": [
            {
                "profile_id": task.profile_id,
                "task_name": task.task_name,
                "log_path": task.log_path,
                "schedule_args": list(task.schedule_args),
                "schtasks_args": list(task.schtasks_args),
            }
            for task in tasks
        ],
    }
    if not args.apply:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    results = register_foundry_schedule_tasks(tasks)
    print(
        json.dumps(
            {
                **payload,
                "registered": results,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
