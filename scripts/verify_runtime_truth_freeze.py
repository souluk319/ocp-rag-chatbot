from __future__ import annotations

import json
import sys
from pathlib import Path

from play_book_studio.execution_guard import run_guarded_script

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.runtime_truth_freeze import audit_runtime_truth


def _markdown_lines(report: dict[str, object]) -> list[str]:
    metrics = report["metrics"]
    lines = [
        "# Runtime Truth Freeze Report",
        "",
        f"- status: `{report['status']}`",
        f"- canonical_truth_owner: `{report['canonical_truth_owner']}`",
        f"- active_runtime_snapshot_id: `{report['snapshot']['active_runtime_snapshot_id']}`",
        "",
        "## Metrics",
        "",
    ]
    for key, value in metrics.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Owner Decisions",
            "",
        ]
    )
    for item in report.get("owner_decisions", []):
        lines.append(f"- `{item}`")
    if report.get("anchor_drift_books"):
        lines.extend(["", "## Anchor Drift Books", ""])
        for item in report["anchor_drift_books"]:
            lines.append(
                f"- `{item['slug']}`: candidate={item['candidate_anchor_count']} runtime={item['runtime_anchor_count']}"
            )
    return lines


def main() -> int:
    report = audit_runtime_truth(ROOT)
    out_dir = ROOT / "reports" / "build_logs"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "runtime_truth_freeze_report.json"
    md_path = out_dir / "runtime_truth_freeze_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text("\n".join(_markdown_lines(report)).rstrip() + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
