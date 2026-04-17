from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.execution_guard import run_guarded_script
JUNK_ROOTS = (
    ROOT / ".pytest_cache",
    ROOT / "presentation-ui" / "dist",
)
TOP_SCAN_ROOTS = (
    ROOT / "src",
    ROOT / "tests",
    ROOT / "presentation-ui" / "src",
)
JUNK_FILE_SUFFIXES = {".pyc", ".pyo"}
SKIP_PARTS = {".git", ".venv", "node_modules", "tmp_source"}


def _is_within_root(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return False
    return True


def _is_skipped(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def _tracked_top_level_counts() -> list[dict[str, int | str]]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []

    counts: dict[str, int] = {}
    for line in result.stdout.splitlines():
        if not line:
            continue
        top = line.split("/", 1)[0]
        counts[top] = counts.get(top, 0) + 1
    return [
        {"path": path, "count": count}
        for path, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def _largest_files(root: Path, *, limit: int) -> list[dict[str, int | str]]:
    if not root.exists():
        return []
    files = [
        path
        for path in root.rglob("*")
        if path.is_file() and not _is_skipped(path) and "__pycache__" not in path.parts
    ]
    files.sort(key=lambda path: path.stat().st_size, reverse=True)
    return [
        {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "bytes": path.stat().st_size,
        }
        for path in files[:limit]
    ]


def collect_workspace_junk() -> list[Path]:
    junk: list[Path] = []
    for path in JUNK_ROOTS:
        if path.exists():
            junk.append(path)
    for search_root in (ROOT / "src", ROOT / "tests", ROOT / "scripts"):
        if not search_root.exists():
            continue
        for path in search_root.rglob("*"):
            if not path.exists() or _is_skipped(path):
                continue
            if path.is_dir() and path.name == "__pycache__":
                junk.append(path)
            if path.is_file() and path.suffix in JUNK_FILE_SUFFIXES:
                junk.append(path)
    seen: set[Path] = set()
    ordered: list[Path] = []
    for path in sorted(junk, key=lambda item: (len(item.parts), str(item))):
        if path in seen:
            continue
        if any(parent in seen for parent in path.parents):
            continue
        seen.add(path)
        ordered.append(path)
    return ordered


def _path_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(child.stat().st_size for child in path.rglob("*") if child.is_file())


def build_report(*, limit: int) -> dict:
    junk_paths = collect_workspace_junk()
    return {
        "tracked_top_level_counts": _tracked_top_level_counts(),
        "largest_source_files": _largest_files(ROOT / "src", limit=limit),
        "largest_test_files": _largest_files(ROOT / "tests", limit=limit),
        "largest_frontend_files": _largest_files(ROOT / "presentation-ui" / "src", limit=limit),
        "workspace_junk": [
            {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "kind": "dir" if path.is_dir() else "file",
                "bytes": _path_size(path),
            }
            for path in junk_paths
        ],
        "workspace_junk_count": len(junk_paths),
        "workspace_junk_bytes": sum(_path_size(path) for path in junk_paths),
    }


def clean_workspace_junk() -> dict[str, int | list[dict[str, int | str]]]:
    removed: list[dict[str, int | str]] = []
    for path in collect_workspace_junk():
        if not _is_within_root(path) or _is_skipped(path):
            continue
        size = _path_size(path)
        relative = str(path.relative_to(ROOT)).replace("\\", "/")
        kind = "dir" if path.is_dir() else "file"
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
        removed.append(
            {
                "path": relative,
                "kind": kind,
                "bytes": size,
            }
        )
    return {
        "removed_count": len(removed),
        "removed_bytes": sum(int(item["bytes"]) for item in removed),
        "removed": removed,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit and clean repo hygiene drift.")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--audit-output", type=Path, default=None)
    parser.add_argument("--clean", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = build_report(limit=args.top)
    if args.clean:
        report["cleanup"] = clean_workspace_junk()
        report["post_cleanup"] = build_report(limit=args.top)
    if args.audit_output is not None:
        args.audit_output.parent.mkdir(parents=True, exist_ok=True)
        args.audit_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
