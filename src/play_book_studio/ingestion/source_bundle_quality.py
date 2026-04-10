# bronze source bundle의 제련 준비 상태를 평가한다.
from __future__ import annotations

import json
from pathlib import Path

from play_book_studio.config.settings import Settings


def _bundle_root(settings: Settings) -> Path:
    return settings.bronze_dir / "source_bundles"


def _safe_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _bundle_quality_row(bundle_dir: Path) -> dict[str, object]:
    manifest = _safe_json(bundle_dir / "bundle_manifest.json")
    dossier = _safe_json(bundle_dir / "dossier.json")
    issue_candidates = _safe_json(bundle_dir / "issue_pr_candidates.json")
    repo_artifact_count = len(manifest.get("repo_artifacts", []))
    exact_issue_pr_count = len(issue_candidates.get("exact_slug", []))
    related_issue_pr_count = len(issue_candidates.get("related_terms", []))
    ko_doc = dict(manifest.get("official_docs", {})).get("ko", {})
    en_doc = dict(manifest.get("official_docs", {})).get("en", {})
    current_status = dict(dossier.get("current_status", {}))
    gap_lane = str(current_status.get("gap_lane", ""))
    ko_fallback_banner = bool(ko_doc.get("contains_language_fallback_banner", False))
    has_en_html = bool(en_doc.get("artifact_path")) and int(en_doc.get("content_length", 0)) > 0

    if repo_artifact_count == 0:
        readiness = "source_expansion_needed"
        recommended_action = "expand alias/title repo search before translation or synthesis"
    elif gap_lane == "translation_first" or ko_fallback_banner:
        readiness = "translation_ready" if has_en_html else "source_expansion_needed"
        recommended_action = (
            "translate from official EN with repo sidecars and review gate"
            if readiness == "translation_ready"
            else "recover official EN body before translation"
        )
    else:
        readiness = "manual_review_ready"
        recommended_action = "compose reviewed KO/manualbook from harvested evidence"

    return {
        "book_slug": bundle_dir.name,
        "content_status": str(current_status.get("content_status", "")),
        "gap_lane": gap_lane,
        "ko_fallback_banner": ko_fallback_banner,
        "has_en_html": has_en_html,
        "repo_artifact_count": repo_artifact_count,
        "exact_issue_pr_count": exact_issue_pr_count,
        "related_issue_pr_count": related_issue_pr_count,
        "readiness": readiness,
        "recommended_action": recommended_action,
    }


def build_source_bundle_quality_report(settings: Settings) -> dict[str, object]:
    root = _bundle_root(settings)
    bundles = []
    if root.exists():
        for bundle_dir in sorted(path for path in root.iterdir() if path.is_dir()):
            required = [
                bundle_dir / "bundle_manifest.json",
                bundle_dir / "dossier.json",
                bundle_dir / "issue_pr_candidates.json",
            ]
            if not all(path.exists() for path in required):
                continue
            bundles.append(_bundle_quality_row(bundle_dir))

    counts = {
        "translation_ready": sum(1 for item in bundles if item["readiness"] == "translation_ready"),
        "manual_review_ready": sum(1 for item in bundles if item["readiness"] == "manual_review_ready"),
        "source_expansion_needed": sum(1 for item in bundles if item["readiness"] == "source_expansion_needed"),
    }
    return {
        "bundle_count": len(bundles),
        "counts": counts,
        "bundles": bundles,
    }

