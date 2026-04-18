from __future__ import annotations

import json
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

REPORT_PATH = ROOT / "reports" / "build_logs" / "ocp420_one_click_runtime_report.json"
CODEX_PYTHON = ROOT / "scripts" / "codex_python.ps1"

STEPS = [
    {
        "step_id": "full_rebuild_batch_ab",
        "script": ROOT / "scripts" / "run_ocp420_full_rebuild.py",
        "write_scope": "manifests + data/gold_candidate_books/full_rebuild + data/wiki_runtime_books/full_rebuild + data/wiki_relations + reports/build_logs",
        "verify_cmd": "batch a+b full rebuild assets exist",
    },
    {
        "step_id": "quarantine_old_full_rebuild_outputs",
        "script": ROOT / "scripts" / "quarantine_old_official_rebuild_artifacts.py",
        "write_scope": "data/quarantine + reports/build_logs/official_rebuild_quarantine_report.json",
        "verify_cmd": "contaminated full rebuild outputs quarantined before fresh materialization",
    },
    {
        "step_id": "materialize_full_rebuild_books",
        "script": ROOT / "scripts" / "materialize_ocp420_full_rebuild_books.py",
        "write_scope": "scripts + data/gold_candidate_books/full_rebuild + data/wiki_runtime_books/full_rebuild + reports/build_logs",
        "verify_cmd": "full rebuild books materialized",
    },
    {
        "step_id": "activate_full_rebuild_runtime",
        "script": ROOT / "scripts" / "activate_wiki_runtime_group.py",
        "write_scope": "scripts + data/wiki_runtime_books + reports/build_logs",
        "verify_cmd": "active manifest switched to full_rebuild",
        "args": ["full_rebuild"],
    },
    {
        "step_id": "generate_full_rebuild_wiki_relations",
        "script": ROOT / "scripts" / "generate_full_rebuild_wiki_relations.py",
        "write_scope": "scripts + data/wiki_relations + reports/build_logs",
        "verify_cmd": "full rebuild wiki relations generated",
    },
]


def _run_step(step: dict[str, Any]) -> dict[str, Any]:
    args = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(CODEX_PYTHON),
        str(step["script"]),
        str(step["write_scope"]),
        str(step["verify_cmd"]),
    ]
    args.extend(step.get("args") or [])
    completed = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    return {
        "step_id": step["step_id"],
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _http_get_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _http_get_text(url: str) -> str:
    with urllib.request.urlopen(url) as response:
        return response.read().decode("utf-8", errors="replace")


def _smoke_payload() -> dict[str, Any]:
    figure_catalog_path = ROOT / "data" / "wiki_relations" / "figure_assets.json"
    figure_catalog = json.loads(figure_catalog_path.read_text(encoding="utf-8")) if figure_catalog_path.exists() else {}
    figure_entries = figure_catalog.get("entries") if isinstance(figure_catalog, dict) else {}
    architecture_figures = figure_entries.get("architecture") if isinstance(figure_entries, dict) else []
    first_architecture_figure = architecture_figures[0] if isinstance(architecture_figures, list) and architecture_figures else {}

    data_control_room = _http_get_json("http://127.0.0.1:8765/api/data-control-room")
    runtime_html = _http_get_text("http://127.0.0.1:8765/playbooks/wiki-runtime/active/advanced_networking/index.html?embed=1")
    storage_html = _http_get_text("http://127.0.0.1:8765/playbooks/wiki-runtime/active/storage/index.html?embed=1")
    nodes_html = _http_get_text("http://127.0.0.1:8765/playbooks/wiki-runtime/active/nodes/index.html?embed=1")
    architecture_html = _http_get_text("http://127.0.0.1:8765/playbooks/wiki-runtime/active/architecture/index.html?embed=1")
    proxy_hub_html = _http_get_text("http://127.0.0.1:8765/wiki/entities/cluster-wide-proxy/index.html?embed=1")
    architecture_figure_viewer_path = str(first_architecture_figure.get("viewer_path") or "")
    architecture_figure_html = _http_get_text(f"http://127.0.0.1:8765{architecture_figure_viewer_path}?embed=1") if architecture_figure_viewer_path else ""

    chat_request = urllib.request.Request(
        "http://127.0.0.1:8765/api/chat",
        data=json.dumps({"query": "etcd 백업 절차 알려줘"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(chat_request) as response:
        chat_payload = json.loads(response.read().decode("utf-8", errors="replace"))

    related_links = chat_payload.get("related_links") if isinstance(chat_payload.get("related_links"), list) else []
    active_runtime_links = [
        str(item.get("href") or "")
        for item in related_links
        if isinstance(item, dict) and "/playbooks/wiki-runtime/active/" in str(item.get("href") or "")
    ]
    approved_books = data_control_room.get("approved_wiki_runtime_books", {}).get("books") or []
    approved_count = data_control_room.get("summary", {}).get("approved_wiki_runtime_book_count")
    return {
        "approved_wiki_runtime_book_count": approved_count,
        "has_advanced_networking": any(
            isinstance(item, dict) and str(item.get("book_slug") or "") == "advanced_networking"
            for item in approved_books
        ),
        "advanced_networking_viewer_path": next(
            (
                str(item.get("viewer_path") or "")
                for item in approved_books
                if isinstance(item, dict) and str(item.get("book_slug") or "") == "advanced_networking"
            ),
            "",
        ),
        "runtime_viewer_has_title": "고급 네트워킹" in runtime_html,
        "runtime_viewer_has_related_documents": "Related Documents" in runtime_html,
        "runtime_viewer_has_networking_hub": "/wiki/entities/networking/index.html" in runtime_html,
        "runtime_viewer_has_related_sections": "Related Sections" in runtime_html and "/playbooks/wiki-runtime/active/" in runtime_html and "#" in runtime_html,
        "storage_viewer_has_topic_hub": "/wiki/entities/storage-and-content/index.html" in storage_html,
        "proxy_hub_has_related_figures": "Related Figures" in proxy_hub_html and "/wiki/figures/advanced_networking/" in proxy_hub_html,
        "proxy_hub_has_related_sections": "Related Sections" in proxy_hub_html and "/playbooks/wiki-runtime/active/" in proxy_hub_html and "#" in proxy_hub_html,
        "nodes_viewer_has_figure": "figure-block" in nodes_html and "/playbooks/wiki-assets/full_rebuild/nodes/" in nodes_html,
        "architecture_viewer_has_figure": "figure-block" in architecture_html and "/playbooks/wiki-assets/full_rebuild/architecture/" in architecture_html,
        "architecture_figure_viewer_path": architecture_figure_viewer_path,
        "architecture_figure_viewer_has_parent_book": "Parent Book" in architecture_figure_html,
        "architecture_figure_viewer_has_related_entities": "Related Entities" in architecture_figure_html,
        "architecture_figure_viewer_has_related_section": (
            "Related Section" in architecture_figure_html
            and "/playbooks/wiki-runtime/active/architecture/index.html#" in architecture_figure_html
        ),
        "chat_related_link_count": len(related_links),
        "chat_active_runtime_links": active_runtime_links,
    }


def main() -> int:
    results: list[dict[str, Any]] = []
    for step in STEPS:
        result = _run_step(step)
        results.append(result)
        if int(result["returncode"]) != 0:
            payload = {"status": "failed", "step_results": results}
            REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
            REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return int(result["returncode"])

    smoke = _smoke_payload()
    payload = {
        "status": "ok",
        "step_results": results,
        "smoke": smoke,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
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
