from __future__ import annotations

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fetch_text(url: str) -> str:
    with urllib.request.urlopen(url) as response:
        return response.read().decode("utf-8", errors="ignore")


def main() -> int:
    diagram_catalog = _load_json(ROOT / "data" / "wiki_relations" / "diagram_assets.json")
    figure_catalog = _load_json(ROOT / "data" / "wiki_relations" / "figure_assets.json")
    report_path = ROOT / "reports" / "build_logs" / "diagram_block_coverage_report.json"
    entries = diagram_catalog.get("entries") or {}
    sample_slug = ""
    sample_asset = ""
    for slug, assets in entries.items():
        if assets:
            sample_slug = str(slug)
            sample_asset = str(assets[0].get("asset_url") or "")
            break
    if not sample_slug or not sample_asset:
        payload = {
            "status": "ok",
            "diagram_book_count": int(diagram_catalog.get("book_count") or 0),
            "diagram_count": int(diagram_catalog.get("diagram_count") or 0),
            "sample_runtime_url": "",
            "sample_runtime_has_diagram_block": False,
        }
        report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    runtime_url = f"http://127.0.0.1:8765/playbooks/wiki-runtime/active/{sample_slug}/index.html?embed=1"
    figure_url = f"http://127.0.0.1:8765/wiki/figures/{sample_slug}/{Path(sample_asset).name}/index.html?embed=1"
    runtime_html = _fetch_text(runtime_url)
    figure_html = _fetch_text(figure_url)
    payload = {
        "status": "ok",
        "diagram_book_count": int(diagram_catalog.get("book_count") or 0),
        "diagram_count": int(diagram_catalog.get("diagram_count") or 0),
        "figure_book_count": int(figure_catalog.get("book_count") or 0),
        "sample_slug": sample_slug,
        "sample_runtime_url": runtime_url,
        "sample_figure_url": figure_url,
        "sample_runtime_has_diagram_block": "diagram-block" in runtime_html,
        "sample_runtime_has_diagram_label": "Diagram" in runtime_html,
        "sample_figure_has_diagram_block": "diagram-block" in figure_html,
        "sample_figure_has_diagram_label": "Diagram" in figure_html,
    }
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
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
