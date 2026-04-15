from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def _parse_list(values: list[str]) -> list[str]:
    items: list[str] = []
    for value in values:
        for part in value.split(";"):
            stripped = part.strip()
            if stripped:
                items.append(stripped)
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare milestone execution harness artifacts.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--shell", required=True)
    parser.add_argument("--cwd", required=True)
    parser.add_argument("--python-path", required=True)
    parser.add_argument("--worktree-path", required=True)
    parser.add_argument("--lane-id", default="main")
    parser.add_argument("--role", default="main")
    parser.add_argument("--write-scope", required=True)
    parser.add_argument("--output", action="append", default=[])
    parser.add_argument("--validate", action="append", default=[])
    args = parser.parse_args()

    repo_root = Path(args.cwd).resolve()
    target_dir = repo_root / "reports" / "execution_harness" / args.task_id / args.lane_id
    target_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "task_id": args.task_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "shell": args.shell,
        "cwd": str(repo_root),
        "python_path": args.python_path,
        "worktree_path": args.worktree_path,
        "lane_id": args.lane_id,
        "role": args.role,
        "write_scope": args.write_scope,
        "target_outputs": _parse_list(args.output),
        "validation_commands": _parse_list(args.validate),
        "status": "prepared",
    }

    manifest_path = target_dir / "manifest.json"
    worklog_path = target_dir / "worklog.md"
    final_report_path = target_dir / "final_report.json"

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not worklog_path.exists():
        worklog_path.write_text(
            "# Local Worklog\n\n"
            f"- task_id: `{args.task_id}`\n"
            f"- lane_id: `{args.lane_id}`\n"
            f"- role: `{args.role}`\n"
            "- user-visible progress는 milestone 종료 전까지 기록하지 않는다.\n"
            "- 중간 자동 복구, 실행 메모, 임시 판단은 이 파일에만 적는다.\n",
            encoding="utf-8",
        )
    if not final_report_path.exists():
        final_report_path.write_text(
            json.dumps(
                {
                    "task_id": args.task_id,
                    "lane_id": args.lane_id,
                    "role": args.role,
                    "status": "pending",
                    "code_paths": [],
                    "artifacts": [],
                    "validation": [],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "task_id": args.task_id,
                "lane_id": args.lane_id,
                "manifest": str(manifest_path),
                "worklog": str(worklog_path),
                "final_report": str(final_report_path),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
