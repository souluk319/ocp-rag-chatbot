from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.canonical import (  # noqa: E402
    build_source_repo_document_ast,
    project_playbook_document,
    validate_document_ast,
    write_playbook_documents,
)
from play_book_studio.config.settings import load_settings  # noqa: E402
from play_book_studio.execution_guard import run_guarded_script  # noqa: E402
from play_book_studio.ingestion.chunking import chunk_sections  # noqa: E402
from play_book_studio.ingestion.models import (  # noqa: E402
    CONTENT_STATUS_EN_ONLY,
    SOURCE_STATE_EN_ONLY,
    SourceManifestEntry,
)
from play_book_studio.ingestion.playbook_materialization import project_playbook_payload_sections  # noqa: E402
from play_book_studio.source_provenance import source_fingerprint_for_entry  # noqa: E402


INPUT_MANIFEST_PATH = ROOT / "manifests" / "ocp420_repo_wide_source_manifest.json"
OUTPUT_ROOT = ROOT / "artifacts" / "official_lane" / "repo_wide_official_source"
CANONICAL_DOCS_DIR = OUTPUT_ROOT / "canonical_documents"
CANONICAL_JSONL_PATH = OUTPUT_ROOT / "canonical_documents.jsonl"
PLAYBOOK_JSONL_PATH = OUTPUT_ROOT / "playbook_documents.jsonl"
PLAYBOOK_BOOKS_DIR = OUTPUT_ROOT / "playbooks"
NORMALIZED_JSONL_PATH = OUTPUT_ROOT / "normalized_docs.jsonl"
CHUNKS_JSONL_PATH = OUTPUT_ROOT / "chunks.jsonl"
BM25_JSONL_PATH = OUTPUT_ROOT / "bm25_corpus.jsonl"
MANIFEST_PATH = OUTPUT_ROOT / "manifest.json"
REPORT_PATH = ROOT / "reports" / "build_logs" / "ocp420_repo_wide_official_structured_report.json"


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load_manifest_payload() -> dict[str, object]:
    payload = json.loads(INPUT_MANIFEST_PATH.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _repo_entry_to_source_manifest_entry(
    row: dict[str, object],
    *,
    source_mirror_root: str,
) -> SourceManifestEntry:
    source_relative_paths = tuple(
        str(item).strip()
        for item in (row.get("source_relative_paths") or [])
        if str(item).strip()
    )
    source_relative_path = str(row.get("source_relative_path") or "").strip()
    source_url = ""
    source_repo = str(row.get("source_repo") or "").strip()
    source_branch = str(row.get("source_branch") or "").strip()
    if source_repo and source_branch and source_relative_path:
        source_url = f"{source_repo.rstrip('/')}/blob/{source_branch}/{source_relative_path}"
    payload = {
        "product_slug": "openshift_container_platform",
        "ocp_version": "4.20",
        "docs_language": "ko",
        "source_kind": "source-first",
        "book_slug": str(row.get("book_slug") or "").strip(),
        "title": str(row.get("title") or "").strip(),
        "index_url": "",
        "source_url": source_url,
        "resolved_source_url": source_url,
        "resolved_language": "en",
        "source_state": SOURCE_STATE_EN_ONLY,
        "source_state_reason": "repo_source_first",
        "catalog_source_label": "repo_topic_map",
        "viewer_path": str(
            (row.get("rebuild_target_paths") or {}).get("viewer_path")
            if isinstance(row.get("rebuild_target_paths"), dict)
            else ""
        ).strip(),
        "high_value": False,
        "vendor_title": str(row.get("title") or "").strip(),
        "content_status": CONTENT_STATUS_EN_ONLY,
        "citation_eligible": False,
        "citation_block_reason": "translation_required",
        "viewer_strategy": "playbook_ast_v1",
        "body_language_guess": "en",
        "fallback_detected": False,
        "approval_status": "unreviewed",
        "source_id": f"repo-topic-map:{str(row.get('book_slug') or '').strip()}",
        "source_lane": "official_source_first",
        "source_type": "official_doc",
        "source_collection": "core",
        "review_status": "unreviewed",
        "trust_score": 1.0,
        "verifiability": "repo_anchor_backed",
        "translation_source_language": "en",
        "translation_target_language": "ko",
        "translation_source_url": source_url,
        "translation_stage": "en_only",
        "primary_input_kind": "source_repo",
        "source_repo": source_repo,
        "source_branch": source_branch,
        "source_binding_kind": str(row.get("source_binding_kind") or "").strip(),
        "source_relative_path": source_relative_path,
        "source_relative_paths": source_relative_paths,
        "source_mirror_root": str(source_mirror_root or "").strip(),
        "fallback_source_url": "",
        "fallback_viewer_path": "",
    }
    payload["source_fingerprint"] = source_fingerprint_for_entry(payload)
    return SourceManifestEntry(**payload)


def _load_entries(*, limit: int | None, slugs: set[str]) -> list[dict[str, object]]:
    manifest = _load_manifest_payload()
    entries = manifest.get("entries") if isinstance(manifest.get("entries"), list) else []
    selected: list[dict[str, object]] = []
    for row in entries:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("book_slug") or "").strip()
        if slugs and slug not in slugs:
            continue
        selected.append(row)
        if limit is not None and len(selected) >= limit:
            break
    return selected


def _canonical_path(slug: str) -> Path:
    return CANONICAL_DOCS_DIR / f"{slug}.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--slugs", nargs="*", default=[])
    args = parser.parse_args()

    settings = load_settings(ROOT)
    manifest_payload = _load_manifest_payload()
    source_mirror_root = str(manifest_payload.get("source_mirror_root") or "").strip()
    entries = _load_entries(limit=args.limit, slugs={str(slug).strip() for slug in args.slugs if str(slug).strip()})
    print(json.dumps({"stage": "load", "entry_count": len(entries)}, ensure_ascii=False))

    canonical_rows: list[dict[str, object]] = []
    playbook_artifacts = []
    playbook_payloads = []
    normalized_rows: list[dict[str, object]] = []
    chunk_rows: list[dict[str, object]] = []
    output_entries: list[dict[str, object]] = []
    failures: list[dict[str, str]] = []

    for index, row in enumerate(entries, start=1):
        slug = str(row.get("book_slug") or "").strip()
        entry = _repo_entry_to_source_manifest_entry(row, source_mirror_root=source_mirror_root)
        source_paths = [
            (ROOT / "tmp_source" / "openshift-docs-enterprise-4.20" / relative_path).resolve()
            for relative_path in entry.source_relative_paths
        ] or [
            (ROOT / "tmp_source" / "openshift-docs-enterprise-4.20" / entry.source_relative_path).resolve()
        ]
        try:
            document = build_source_repo_document_ast(
                entry=entry,
                source_paths=source_paths,
                fallback_title=entry.title or slug,
            )
            issues = validate_document_ast(document)
            errors = [issue for issue in issues if issue.severity == "error"]
            if errors:
                raise ValueError(", ".join(issue.code for issue in errors[:5]))
            canonical_payload = document.to_dict()
            canonical_rows.append(canonical_payload)
            _canonical_path(slug).parent.mkdir(parents=True, exist_ok=True)
            _canonical_path(slug).write_text(
                json.dumps(canonical_payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            playbook_artifact = project_playbook_document(document)
            playbook_artifacts.append(playbook_artifact)
            playbook_payload = playbook_artifact.to_dict()
            playbook_payloads.append(playbook_payload)
            normalized_sections = project_playbook_payload_sections(playbook_payload)
            normalized_rows.extend(section.to_dict() for section in normalized_sections)
            chunks = chunk_sections(normalized_sections, settings)
            chunk_rows.extend(chunk.to_dict() for chunk in chunks)
            output_entries.append(
                {
                    "book_slug": slug,
                    "title": playbook_payload["title"],
                    "canonical_document_path": str(_canonical_path(slug)),
                    "playbook_document_path": str(PLAYBOOK_BOOKS_DIR / f"{slug}.json"),
                    "section_count": len(document.sections),
                    "chunk_count": len(chunks),
                    "parser_route": "source_repo_first",
                    "parser_backend": "canonical_source_repo_v1",
                    "source_lane": "official_source_first",
                    "primary_input_kind": "source_repo",
                    "source_repo": entry.source_repo,
                    "source_branch": entry.source_branch,
                    "source_binding_kind": entry.source_binding_kind,
                    "source_relative_paths": list(entry.source_relative_paths),
                }
            )
            print(
                json.dumps(
                    {
                        "stage": "build",
                        "index": index,
                        "total": len(entries),
                        "book_slug": slug,
                        "sections": len(document.sections),
                        "chunks": len(chunks),
                    },
                    ensure_ascii=False,
                )
            )
        except Exception as exc:  # noqa: BLE001
            failures.append({"book_slug": slug, "error": str(exc)})
            print(json.dumps({"stage": "error", "book_slug": slug, "error": str(exc)}, ensure_ascii=False))

    _write_jsonl(CANONICAL_JSONL_PATH, canonical_rows)
    write_playbook_documents(PLAYBOOK_JSONL_PATH, PLAYBOOK_BOOKS_DIR, playbook_artifacts)
    _write_jsonl(NORMALIZED_JSONL_PATH, normalized_rows)
    _write_jsonl(CHUNKS_JSONL_PATH, chunk_rows)
    _write_jsonl(BM25_JSONL_PATH, chunk_rows)

    manifest_payload = {
        "status": "ok" if not failures else "partial",
        "source_strategy": "repo_wide_official_source_first_structured",
        "input_manifest_path": str(INPUT_MANIFEST_PATH),
        "output_root": str(OUTPUT_ROOT),
        "entry_count": len(entries),
        "processed_count": len(playbook_payloads),
        "failure_count": len(failures),
        "canonical_document_count": len(canonical_rows),
        "playbook_document_count": len(playbook_payloads),
        "normalized_section_count": len(normalized_rows),
        "chunk_count": len(chunk_rows),
        "entries": output_entries,
        "failures": failures,
    }
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest_payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(
        run_guarded_script(
            main,
            __file__,
            launcher_hint="scripts/codex_python.ps1",
        )
    )
