from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from deployment.stage11_activation_utils import document_path_from_record, ensure_index_layout
from deployment.stage11_bundle_utils import (
    extract_source_manifest_version,
    load_json,
    repo_relative,
    repo_root,
    sha256_file,
    utc_now,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Stage 11 activation index artifact from a staged bundle.")
    parser.add_argument("staging", type=Path)
    parser.add_argument("--index-root", type=Path, default=repo_root() / "indexes")
    parser.add_argument("--index-id", default="")
    parser.add_argument("--smoke-set", type=Path, default=repo_root() / "deployment" / "activation-smoke-case-ids.json")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def required_path(path: Path, label: str) -> Path:
    if not path.exists():
        raise SystemExit(f"Missing required {label}: {path}")
    return path


def main() -> int:
    args = parse_args()
    staging_path = args.staging.resolve()
    if not staging_path.exists():
        raise SystemExit(f"Staging path does not exist: {staging_path}")

    bundle_manifest_path = required_path(staging_path / "manifests" / "bundle-manifest.json", "bundle manifest")
    approval_path = required_path(staging_path / "manifests" / "approval.json", "approval record")
    source_manifest_path = required_path(staging_path / "manifests" / "source-manifest.yaml", "source manifest")
    staging_report_path = required_path(staging_path / "reports" / "staging-report.json", "staging report")

    staged_manifest_path = staging_path / "manifests" / "staged-manifest.json"
    if not staged_manifest_path.exists():
        staged_manifest_path = required_path(staging_path / "manifests" / "normalized-manifest.json", "staged manifest")

    approval = load_json(approval_path)
    if not approval.get("approved_for_import"):
        raise SystemExit("The staged bundle is not approved for import.")

    bundle_manifest = load_json(bundle_manifest_path)
    staged_manifest = load_json(staged_manifest_path)
    staging_report = load_json(staging_report_path)
    bundle_entries = {
        str(item.get("document_id", "")).strip(): item
        for item in bundle_manifest.get("files", [])
        if str(item.get("document_id", "")).strip()
    }

    bundle_id = str(bundle_manifest.get("bundle_id", staging_path.name)).strip() or staging_path.name
    index_id = args.index_id.strip() or bundle_id
    index_dir = (args.index_root / index_id).resolve()
    if index_dir.exists():
        if not args.force:
            raise SystemExit(f"Index path already exists: {index_dir}")
        shutil.rmtree(index_dir)
    ensure_index_layout(index_dir)

    errors: list[str] = []
    warnings: list[str] = []
    index_documents: list[dict[str, Any]] = []
    verified_document_count = 0
    verified_view_count = 0
    top_level_counter: Counter[str] = Counter()
    category_counter: Counter[str] = Counter()

    for document in staged_manifest.get("documents", []):
        document_id = str(document.get("document_id", "")).strip()
        if not document_id:
            errors.append("Encountered staged document without document_id.")
            continue

        bundle_entry = bundle_entries.get(document_id)
        if not bundle_entry:
            errors.append(f"Bundle manifest is missing document entry for {document_id}.")
            continue

        normalized_path = Path(str(document.get("normalized_path", "")).strip())
        html_path = Path(str(document.get("html_path", "")).strip())
        document_path = document_path_from_record(document)
        if not document_path:
            errors.append(f"Unable to derive document_path for {document_id}.")
            continue

        entry: dict[str, Any] = {
            "document_id": document_id,
            "document_path": document_path,
            "title": document.get("title", ""),
            "source_id": document.get("source_id", ""),
            "source_url": document.get("source_url", ""),
            "viewer_url": document.get("viewer_url", ""),
            "normalized_path": str(normalized_path),
            "html_path": str(html_path),
            "category": document.get("category", ""),
            "version": document.get("version", ""),
            "top_level_dir": document.get("top_level_dir", ""),
            "trust_level": document.get("trust_level", ""),
            "checksum": bundle_entry.get("checksum", document.get("checksum", "")),
            "html_checksum": bundle_entry.get("view_checksum", ""),
            "section_count": int(document.get("section_count", 0) or 0),
        }

        top_level_counter[str(entry["top_level_dir"])] += 1
        category_counter[str(entry["category"])] += 1

        if not normalized_path.exists():
            errors.append(f"Missing staged normalized document: {normalized_path}")
        else:
            verified_document_count += 1
            expected_checksum = str(entry["checksum"]).strip()
            if expected_checksum and sha256_file(normalized_path) != expected_checksum:
                errors.append(f"Normalized document checksum mismatch: {document_path}")

        if not html_path.exists():
            errors.append(f"Missing staged HTML view: {html_path}")
        else:
            verified_view_count += 1
            expected_html_checksum = str(entry["html_checksum"]).strip()
            if expected_html_checksum and sha256_file(html_path) != expected_html_checksum:
                errors.append(f"HTML view checksum mismatch: {document_path}")

        if not entry["viewer_url"]:
            warnings.append(f"viewer_url is empty for {document_path}")

        index_documents.append(entry)

    created_at = utc_now()
    index_manifest = {
        "index_id": index_id,
        "bundle_id": bundle_id,
        "source_id": staged_manifest.get("source_id", ""),
        "normalized_manifest_id": staged_manifest.get("manifest_id", ""),
        "source_manifest_version": extract_source_manifest_version(source_manifest_path),
        "created_at": created_at,
        "state": "staged",
        "state_note": "Reindex artifact prepared; activation not yet performed.",
        "index_kind": "stage11-manifest-backed-index",
        "staging_path": repo_relative(staging_path),
        "bundle_manifest_path": repo_relative(bundle_manifest_path),
        "staged_manifest_path": repo_relative(staged_manifest_path),
        "staging_report_path": repo_relative(staging_report_path),
        "approval_path": repo_relative(approval_path),
        "activation_smoke_case_ids_path": repo_relative(args.smoke_set),
        "document_count": len(index_documents),
        "verified_document_count": verified_document_count,
        "verified_view_count": verified_view_count,
        "top_level_counts": dict(sorted(top_level_counter.items())),
        "category_counts": dict(sorted(category_counter.items())),
        "documents": index_documents,
    }

    reindex_report = {
        "index_id": index_id,
        "bundle_id": bundle_id,
        "index_path": repo_relative(index_dir),
        "staging_path": repo_relative(staging_path),
        "created_at": created_at,
        "document_count": len(index_documents),
        "verified_document_count": verified_document_count,
        "verified_view_count": verified_view_count,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "valid_for_activation": not errors,
        "staging_summary": staging_report.get("summary", {}),
    }

    shutil.copy2(bundle_manifest_path, index_dir / "manifests" / "bundle-manifest.json")
    shutil.copy2(approval_path, index_dir / "manifests" / "approval.json")
    shutil.copy2(staged_manifest_path, index_dir / "manifests" / "staged-manifest.json")
    shutil.copy2(source_manifest_path, index_dir / "manifests" / "source-manifest.yaml")
    write_json(index_dir / "manifests" / "index-manifest.json", index_manifest)
    write_json(index_dir / "reports" / "reindex-report.json", reindex_report)

    if args.output:
        write_json(args.output, reindex_report)

    print(json.dumps(reindex_report, ensure_ascii=False, indent=2))
    return 0 if reindex_report["valid_for_activation"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
