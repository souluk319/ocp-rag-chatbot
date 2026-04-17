from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

WORKING_SET_PATH = ROOT / "manifests" / "ocp_ko_4_20_corpus_working_set.json"
OUTPUT_MANIFEST_PATH = ROOT / "manifests" / "ocp420_source_first_full_rebuild_manifest.json"
OUTPUT_REPORT_PATH = ROOT / "reports" / "build_logs" / "ocp420_full_rebuild_manifest_report.json"
# local unmanaged source mirror; top-level git intentionally ignores tmp_source/
SOURCE_ROOT = ROOT / "tmp_source" / "openshift-docs-enterprise-4.20"
SOURCE_REPO_URL = "https://github.com/openshift/openshift-docs"
SOURCE_BRANCH = "enterprise-4.20"

MANUAL_PATH_ALIASES: dict[str, str] = {
    "architecture": "architecture/index.adoc",
    "authentication_and_authorization": "authentication/index.adoc",
    "backup_and_restore": "backup_and_restore/index.adoc",
    "cli_tools": "cli_reference/index.adoc",
    "disconnected_environments": "disconnected/index.adoc",
    "etcd": "etcd/etcd-overview.adoc",
    "images": "openshift_images/index.adoc",
    "installing_on_any_platform": "installing/overview/index.adoc",
    "installation_overview": "installing/overview/index.adoc",
    "machine_configuration": "machine_configuration/index.adoc",
    "machine_management": "machine_management/index.adoc",
    "monitoring": "observability/monitoring/about-ocp-monitoring.adoc",
    "nodes": "nodes/index.adoc",
    "observability_overview": "observability/overview/index.adoc",
    "operators": "operators/index.adoc",
    "postinstallation_configuration": "post_installation_configuration/index.adoc",
    "registry": "registry/index.adoc",
    "security_and_compliance": "security/index.adoc",
    "storage": "storage/index.adoc",
    "support": "support/index.adoc",
    "updating_clusters": "updating/index.adoc",
    "web_console": "web_console/index.adoc",
}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _repo_path_candidates(slug: str) -> list[Path]:
    candidates: list[Path] = []
    alias = MANUAL_PATH_ALIASES.get(slug)
    if alias:
        candidates.append(SOURCE_ROOT / alias)
    candidates.extend(
        [
            SOURCE_ROOT / slug / "index.adoc",
            SOURCE_ROOT / slug.replace("_", "-") / "index.adoc",
        ]
    )
    return candidates


def _resolve_repo_path(slug: str) -> Path | None:
    for candidate in _repo_path_candidates(slug):
        if candidate.exists():
            return candidate
    return None


def main() -> int:
    working_set = _read_json(WORKING_SET_PATH)
    entries = working_set.get("entries") if isinstance(working_set.get("entries"), list) else []
    manifest_entries: list[dict[str, Any]] = []
    source_first_count = 0
    fallback_count = 0

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        slug = str(entry.get("book_slug") or "").strip()
        if not slug:
            continue
        repo_path = _resolve_repo_path(slug)
        primary_input_kind = "source_repo" if repo_path else "html_single"
        if repo_path:
            source_first_count += 1
        else:
            fallback_count += 1
        manifest_entries.append(
            {
                "book_slug": slug,
                "title": str(entry.get("title") or slug),
                "ocp_version": str(entry.get("ocp_version") or "4.20"),
                "docs_language": str(entry.get("docs_language") or "ko"),
                "primary_input_kind": primary_input_kind,
                "source_repo": SOURCE_REPO_URL if repo_path else "",
                "source_branch": SOURCE_BRANCH if repo_path else "",
                "source_relative_path": str(repo_path.relative_to(SOURCE_ROOT)).replace("\\", "/") if repo_path else "",
                "source_mirror_root": str(SOURCE_ROOT) if repo_path else "",
                "fallback_input_kind": "html_single",
                "fallback_source_url": str(entry.get("resolved_source_url") or entry.get("source_url") or ""),
                "fallback_viewer_path": str(entry.get("viewer_path") or ""),
                "source_lane": str(entry.get("source_lane") or ""),
                "content_status": str(entry.get("content_status") or ""),
                "approval_status": str(entry.get("approval_status") or ""),
                "high_value": bool(entry.get("high_value")),
                "rebuild_target_paths": {
                    "gold_candidate_md": f"data/gold_candidate_books/full_rebuild/{slug}.md",
                    "wiki_runtime_md": f"data/wiki_runtime_books/full_rebuild/{slug}.md",
                    "viewer_path": f"/playbooks/wiki-runtime/full-rebuild/{slug}/index.html",
                },
            }
        )

    payload = {
        "status": "ok",
        "product_slug": "openshift_container_platform",
        "ocp_version": "4.20",
        "docs_language": "ko",
        "source_strategy": "source-first-with-html-single-fallback",
        "source_repo": SOURCE_REPO_URL,
        "source_branch": SOURCE_BRANCH,
        "source_mirror_root": str(SOURCE_ROOT),
        "working_set_path": str(WORKING_SET_PATH),
        "entry_count": len(manifest_entries),
        "source_first_count": source_first_count,
        "fallback_only_count": fallback_count,
        "entries": manifest_entries,
    }

    OUTPUT_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MANIFEST_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
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
