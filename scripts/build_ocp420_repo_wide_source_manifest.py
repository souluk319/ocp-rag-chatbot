from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.execution_guard import run_guarded_script
from play_book_studio.ingestion.repo_topic_map import (
    TOPIC_MAP_RELATIVE_PATH,
    TARGET_DISTRO,
    discover_enterprise_topic_map_entries,
)
from play_book_studio.ingestion.source_first import SOURCE_BRANCH, SOURCE_REPO_URL, source_mirror_root

OUTPUT_MANIFEST_PATH = ROOT / "manifests" / "ocp420_repo_wide_source_manifest.json"
OUTPUT_REPORT_PATH = ROOT / "reports" / "build_logs" / "ocp420_repo_wide_source_manifest_report.json"


def main() -> int:
    entries = discover_enterprise_topic_map_entries(ROOT)
    payload = {
        "status": "ok",
        "product_slug": "openshift_container_platform",
        "ocp_version": "4.20",
        "source_strategy": "repo-wide-topic-map-source-first",
        "source_repo": SOURCE_REPO_URL,
        "source_branch": SOURCE_BRANCH,
        "source_mirror_root": str(source_mirror_root(ROOT)),
        "topic_map_path": str((source_mirror_root(ROOT) / TOPIC_MAP_RELATIVE_PATH).resolve()),
        "target_distro": TARGET_DISTRO,
        "entry_count": len(entries),
        "entries": [
            {
                "book_slug": entry.slug,
                "title": entry.title,
                "primary_input_kind": "source_repo",
                "source_repo": entry.source_repo,
                "source_branch": entry.source_branch,
                "source_binding_kind": "file",
                "source_relative_path": entry.source_relative_path,
                "source_relative_paths": [entry.source_relative_path],
                "topic_path": list(entry.topic_path),
                "section_family": list(entry.section_family),
                "rebuild_admission": "repo_source_ready",
                "source_lane": "official_source_first",
                "rebuild_target_paths": {
                    "canonical_document_json": f"artifacts/official_lane/repo_wide_official_source/canonical_documents/{entry.slug}.json",
                    "playbook_document_json": f"artifacts/official_lane/repo_wide_official_source/playbooks/{entry.slug}.json",
                    "viewer_path": f"/docs/ocp/4.20/ko/{entry.slug}/index.html",
                },
            }
            for entry in entries
        ],
    }
    OUTPUT_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    OUTPUT_MANIFEST_PATH.write_text(text + "\n", encoding="utf-8")
    OUTPUT_REPORT_PATH.write_text(text + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "entry_count": len(entries)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(
        run_guarded_script(
            main,
            __file__,
            launcher_hint="scripts/codex_python.ps1",
        )
    )
