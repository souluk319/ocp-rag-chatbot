from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from play_book_studio.execution_guard import run_guarded_script


def _parse_list(values: list[str]) -> list[str]:
    items: list[str] = []
    for value in values:
        for part in value.split(";"):
            stripped = part.strip()
            if stripped:
                items.append(stripped)
    return items


def _default_role_for_lane(lane_id: str) -> str:
    lowered = lane_id.strip().lower()
    if lowered.startswith("explorer"):
        return "explorer"
    if lowered.startswith("worker"):
        return "worker"
    if lowered.startswith("reviewer"):
        return "reviewer"
    return lowered or "support"


def _parse_companion_lanes(values: list[str]) -> list[dict[str, str]]:
    lanes: list[dict[str, str]] = []
    seen: set[str] = set()
    for value in values:
        for part in value.split(";"):
            stripped = part.strip()
            if not stripped:
                continue
            lane_id, separator, role = stripped.partition(":")
            normalized_lane_id = lane_id.strip()
            normalized_role = role.strip() if separator else _default_role_for_lane(normalized_lane_id)
            if not normalized_lane_id:
                continue
            key = normalized_lane_id.lower()
            if key in seen:
                continue
            seen.add(key)
            lanes.append({"lane_id": normalized_lane_id, "role": normalized_role or "support"})
    return lanes


def _create_harness_package(
    *,
    target_dir: Path,
    manifest: dict,
    worklog_lines: list[str],
) -> tuple[Path, Path, Path]:
    target_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = target_dir / "manifest.json"
    worklog_path = target_dir / "worklog.md"
    final_report_path = target_dir / "final_report.json"

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not worklog_path.exists():
        worklog_path.write_text("\n".join(worklog_lines).rstrip() + "\n", encoding="utf-8")
    if not final_report_path.exists():
        final_report_path.write_text(
            json.dumps(
                {
                    "task_id": manifest["task_id"],
                    "lane_id": manifest["lane_id"],
                    "role": manifest["role"],
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
    return manifest_path, worklog_path, final_report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare milestone execution harness artifacts.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--shell", required=True)
    parser.add_argument("--cwd", required=True)
    parser.add_argument("--python-path", required=True)
    parser.add_argument("--worktree-path", required=True)
    parser.add_argument("--lane-id", default="main")
    parser.add_argument("--role", default="main")
    parser.add_argument("--major-task", action="store_true")
    parser.add_argument("--companion-lane", action="append", default=[])
    parser.add_argument("--write-scope", required=True)
    parser.add_argument("--output", action="append", default=[])
    parser.add_argument("--validate", action="append", default=[])
    args = parser.parse_args()

    repo_root = Path(args.cwd).resolve()
    target_dir = repo_root / "reports" / "execution_harness" / args.task_id / args.lane_id
    companion_lanes = _parse_companion_lanes(args.companion_lane)
    companion_roles = {lane["role"] for lane in companion_lanes}
    if args.major_task and args.role == "main":
        if "explorer" not in companion_roles or not companion_roles.intersection({"worker", "reviewer"}):
            raise SystemExit(
                "major task requires companion lanes including explorer and worker or reviewer"
            )

    manifest = {
        "task_id": args.task_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "shell": args.shell,
        "cwd": str(repo_root),
        "python_path": args.python_path,
        "worktree_path": args.worktree_path,
        "lane_id": args.lane_id,
        "role": args.role,
        "major_task": bool(args.major_task),
        "parallel_execution_required": bool(args.major_task),
        "companion_lanes": companion_lanes,
        "write_scope": args.write_scope,
        "target_outputs": _parse_list(args.output),
        "validation_commands": _parse_list(args.validate),
        "status": "prepared",
    }
    manifest_path, worklog_path, final_report_path = _create_harness_package(
        target_dir=target_dir,
        manifest=manifest,
        worklog_lines=[
            "# Local Worklog",
            "",
            f"- task_id: `{args.task_id}`",
            f"- lane_id: `{args.lane_id}`",
            f"- role: `{args.role}`",
            f"- major_task: `{str(bool(args.major_task)).lower()}`",
            "- user-visible progress는 milestone 종료 전까지 기록하지 않는다.",
            "- 중간 자동 복구, 실행 메모, 임시 판단은 이 파일에만 적는다.",
        ],
    )

    for lane in companion_lanes:
        companion_manifest = {
            "task_id": args.task_id,
            "created_at": manifest["created_at"],
            "shell": args.shell,
            "cwd": str(repo_root),
            "python_path": args.python_path,
            "worktree_path": args.worktree_path,
            "lane_id": lane["lane_id"],
            "role": lane["role"],
            "major_task": bool(args.major_task),
            "parallel_execution_required": bool(args.major_task),
            "companion_lanes": [],
            "write_scope": "reserved-by-main",
            "target_outputs": [],
            "validation_commands": [],
            "status": "reserved",
            "reserved_by_lane": args.lane_id,
        }
        _create_harness_package(
            target_dir=repo_root / "reports" / "execution_harness" / args.task_id / lane["lane_id"],
            manifest=companion_manifest,
            worklog_lines=[
                "# Local Worklog",
                "",
                f"- task_id: `{args.task_id}`",
                f"- lane_id: `{lane['lane_id']}`",
                f"- role: `{lane['role']}`",
                f"- reserved_by_lane: `{args.lane_id}`",
                "- companion lane skeleton generated at harness bootstrap.",
                "- main lane 이 실제 write_scope 와 validation 을 확정한 뒤 진행한다.",
            ],
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "task_id": args.task_id,
                "lane_id": args.lane_id,
                "major_task": bool(args.major_task),
                "companion_lanes": companion_lanes,
                "manifest": str(manifest_path),
                "worklog": str(worklog_path),
                "final_report": str(final_report_path),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
