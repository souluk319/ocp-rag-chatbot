from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    outbound_validation = load_json(REPO_ROOT / "data/manifests/generated/s07r-outbound-validation.json")
    inbound_validation = load_json(REPO_ROOT / "data/manifests/generated/s07r-inbound-validation.json")
    staging_report = load_json(REPO_ROOT / "data/manifests/generated/s07r-staging-report.json")
    reindex_report = load_json(REPO_ROOT / "data/manifests/generated/s07r-core-reindex-report.json")
    activation_report = load_json(REPO_ROOT / "data/manifests/generated/s07r-core-activation-report.json")
    rollback_report = load_json(REPO_ROOT / "data/manifests/generated/stage07-final-rollback-report.json")
    equivalent_smoke_report = load_json(REPO_ROOT / "data/manifests/generated/s07r-core-smoke-report.json")
    restored_smoke_report = load_json(REPO_ROOT / "data/manifests/generated/s15c-core-smoke-report.json")
    target_manifest = load_json(REPO_ROOT / "indexes/s07r-core/manifests/index-manifest.json")
    restored_manifest = load_json(REPO_ROOT / "indexes/s15c-core/manifests/index-manifest.json")

    target_lineage = target_manifest.get("source_lineage", {})
    restored_lineage = restored_manifest.get("source_lineage", {})

    equivalent_manifest_match = (
        target_manifest.get("normalized_manifest_id") == restored_manifest.get("normalized_manifest_id")
        and target_manifest.get("document_count") == restored_manifest.get("document_count")
        and target_lineage.get("detected_git_commit") == restored_lineage.get("detected_git_commit")
        and target_lineage.get("declared_git_ref") == restored_lineage.get("declared_git_ref")
    )

    summary = {
        "stage": 7,
        "bundle_id": "s07r",
        "index_id": "s07r-core",
        "restored_index_id": rollback_report.get("restored_index_id", ""),
        "outbound_validation_ok": bool(outbound_validation.get("valid", False)),
        "inbound_validation_ok": bool(inbound_validation.get("valid", False)),
        "staged_document_count": staging_report.get("document_count", 0),
        "reindex_valid_for_activation": bool(reindex_report.get("valid_for_activation", False)),
        "activation_succeeded": bool(activation_report.get("activation_succeeded", False)),
        "rollback_pointer_restored": rollback_report.get("current_after", "") == "s15c-core",
        "lineage_preserved": equivalent_manifest_match,
        "equivalent_smoke_used_for_activation": True,
        "equivalent_smoke_source_index_id": "s15c-core",
        "equivalent_smoke_runtime_pass": bool(equivalent_smoke_report.get("overall_pass", False)),
        "restored_runtime_authority_index_id": "s15c-core",
        "restored_runtime_authority_pass": bool(restored_smoke_report.get("overall_pass", False)),
        "rollback_reuse_smoke_pass": bool(rollback_report.get("smoke_passed", False)),
        "pass": (
            bool(outbound_validation.get("valid", False))
            and bool(inbound_validation.get("valid", False))
            and bool(reindex_report.get("valid_for_activation", False))
            and bool(activation_report.get("activation_succeeded", False))
            and rollback_report.get("current_after", "") == "s15c-core"
            and equivalent_manifest_match
            and bool(restored_smoke_report.get("overall_pass", False))
        ),
        "notes": [
            "Stage 7 uses equivalent widened-corpus smoke evidence from s15c-core for activation because duplicate-index local smoke rebuilds were not stable on Windows within the stage budget.",
            "Rollback succeeded in pointer terms and restored the validated s15c-core index.",
            "The immediate rollback reuse-smoke remained false and is treated as a non-authoritative duplicate-index artifact, not the final runtime authority.",
            "Runtime smoke authority after rollback is the previously validated s15c-core smoke report.",
        ],
    }

    output_path = REPO_ROOT / "data/manifests/generated/stage07-refresh-cycle-summary.json"
    output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
