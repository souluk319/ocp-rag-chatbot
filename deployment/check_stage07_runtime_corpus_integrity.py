from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_PROFILE_PATH = REPO_ROOT / "configs" / "active-source-profile.yaml"
CURRENT_INDEX_PATH = REPO_ROOT / "indexes" / "current.txt"
REPORT_MD_PATH = REPO_ROOT / "docs" / "v2" / "2026-04-01" / "stage-07-report.md"
REPORT_JSON_PATH = REPO_ROOT / "docs" / "v2" / "2026-04-01" / "stage-07-report.json"
BASE_URL = "http://127.0.0.1:8000"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def render_markdown(report: dict[str, object]) -> str:
    checks = report["checks"]
    lines = [
        "# Stage 7 Runtime-Corpus Integrity Report",
        "",
        "## Goal",
        "",
        "Confirm that the live runtime at `localhost:8000` is serving the same corpus/profile that the project currently declares as active.",
        "",
        "## Summary",
        "",
        f"- checked_at: `{report['checked_at']}`",
        f"- base_url: `{report['base_url']}`",
        f"- health_status: `{report['health_status']}`",
        f"- active_profile_id: `{report['active_profile_id']}`",
        f"- active_index_id: `{report['active_index_id']}`",
        f"- active_manifest_path: `{report['active_manifest_path']}`",
        f"- active_document_count: `{report['active_document_count']}`",
        f"- overall_pass: `{report['overall_pass']}`",
        "",
        "## Integrity checks",
        "",
        f"- current.txt matches health active_index_id: `{checks['current_index_matches_health']}`",
        f"- active profile matches staged manifest source_profile: `{checks['profile_matches_manifest']}`",
        f"- manifest document_count matches health active_document_count: `{checks['document_count_matches_health']}`",
        f"- source lineage declared/detected ref aligned: `{checks['lineage_ref_aligned']}`",
        f"- core validation source id aligned: `{checks['source_id_is_core_validation']}`",
        "",
        "## User-visible checkpoint",
        "",
        "- Open `http://127.0.0.1:8000/health`",
        "- Confirm `active_index_id` is `s15c-core`",
        "- Confirm `active_document_count` is `1201`",
        "- Confirm `active_manifest_path` points to `data/staging/s15c/manifests/staged-manifest.json`",
        "",
        "## Output",
        "",
        f"- JSON: `{REPORT_JSON_PATH.as_posix()}`",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    active_profile = load_yaml(ACTIVE_PROFILE_PATH)
    current_index = CURRENT_INDEX_PATH.read_text(encoding="utf-8").strip()

    health_response = requests.get(f"{BASE_URL}/health", timeout=15)
    health_payload = health_response.json()

    manifest_path = Path(health_payload["active_manifest_path"])
    manifest = load_json(manifest_path)
    manifest_documents = manifest.get("documents") or []
    manifest_profile = manifest.get("source_profile") or {}
    lineage = manifest.get("source_lineage") or {}

    report = {
        "checked_at": utc_now(),
        "base_url": BASE_URL,
        "health_status": health_response.status_code,
        "active_profile_id": active_profile.get("active_profile_id"),
        "active_index_id": health_payload.get("active_index_id"),
        "active_manifest_path": str(manifest_path),
        "active_document_count": health_payload.get("active_document_count"),
        "checks": {
            "current_index_matches_health": current_index == health_payload.get("active_index_id"),
            "profile_matches_manifest": active_profile.get("active_profile_id") == manifest_profile.get("profile_id"),
            "document_count_matches_health": len(manifest_documents) == health_payload.get("active_document_count"),
            "lineage_ref_aligned": lineage.get("declared_git_ref") == lineage.get("detected_git_ref") == "main",
            "source_id_is_core_validation": manifest.get("source_id") == "openshift-docs-core-validation",
        },
    }
    report["overall_pass"] = (
        report["health_status"] == 200
        and all(report["checks"].values())
    )

    REPORT_JSON_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    REPORT_MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
