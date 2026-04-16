from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "presentation-ui" / "dist"
OUTPUT_JSON = ROOT / "reports" / "build_logs" / "surface_lock_report.json"
OUTPUT_MD = ROOT / "reports" / "build_logs" / "surface_lock_report.md"


def main() -> int:
    asset_files = sorted(
        [
            str(path.relative_to(ROOT)).replace("\\", "/")
            for path in (DIST_DIR / "assets").glob("*")
            if path.is_file()
        ]
    )
    report = {
        "status": "ok",
        "frontend_build_pass": DIST_DIR.joinpath("index.html").exists(),
        "dist_asset_count": len(asset_files),
        "dist_assets": asset_files[:6],
        "workspace_page_exists": (ROOT / "presentation-ui" / "src" / "pages" / "WorkspacePage.tsx").exists(),
        "workspace_trace_panel_exists": (ROOT / "presentation-ui" / "src" / "components" / "WorkspaceTracePanel.tsx").exists(),
        "runtime_ui_test_file_exists": (ROOT / "tests" / "test_app_runtime_ui.py").exists(),
    }
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Surface Lock Report",
                "",
                f"- frontend_build_pass: `{report['frontend_build_pass']}`",
                f"- dist_asset_count: `{report['dist_asset_count']}`",
                f"- workspace_page_exists: `{report['workspace_page_exists']}`",
                f"- workspace_trace_panel_exists: `{report['workspace_trace_panel_exists']}`",
                f"- runtime_ui_test_file_exists: `{report['runtime_ui_test_file_exists']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(
        run_guarded_script(
            main,
            __file__,
            launcher_hint="scripts/codex_python.ps1",
        )
    )
