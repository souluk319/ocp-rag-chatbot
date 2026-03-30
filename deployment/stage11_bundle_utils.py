from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
NORMALIZED_ROOT = REPO_ROOT / "data" / "normalized"
VIEWS_ROOT = REPO_ROOT / "data" / "views"


def repo_root() -> Path:
    return REPO_ROOT


def repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_source_manifest_version(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"(?m)^version:\s*([^\n#]+)", text)
    return match.group(1).strip() if match else "unknown"


def _bundle_relative_from_root(path: Path, root: Path, prefix: str) -> str:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"{path} is not under {root}") from exc
    return f"{prefix}/{relative.as_posix()}"


def normalized_bundle_relative(document: dict[str, Any]) -> str:
    return _bundle_relative_from_root(Path(document["normalized_path"]), NORMALIZED_ROOT, "documents")


def view_bundle_relative(document: dict[str, Any]) -> str:
    return _bundle_relative_from_root(Path(document["html_path"]), VIEWS_ROOT, "views")


def build_document_snapshot(document: dict[str, Any]) -> dict[str, Any]:
    normalized_path = Path(document["normalized_path"])
    html_path = Path(document["html_path"])
    return {
        "document_id": document["document_id"],
        "title": document.get("title", ""),
        "source_id": document.get("source_id", ""),
        "category": document.get("category", ""),
        "version": document.get("version", ""),
        "checksum": sha256_file(normalized_path) if normalized_path.exists() else document.get("checksum", ""),
        "html_checksum": sha256_file(html_path) if html_path.exists() else "",
        "normalized_relative_path": normalized_bundle_relative(document),
        "view_relative_path": view_bundle_relative(document),
        "viewer_url": document.get("viewer_url", ""),
        "source_url": document.get("source_url", ""),
        "source_mirror_id": document.get("source_mirror_id", ""),
        "source_profile_id": document.get("source_profile_id", ""),
        "source_git_ref": document.get("source_git_ref", ""),
        "source_git_commit": document.get("source_git_commit", ""),
        "target_minor": document.get("target_minor", ""),
        "top_level_dir": document.get("top_level_dir", ""),
    }


def current_manifest_documents(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [build_document_snapshot(document) for document in manifest.get("documents", [])]


def build_document_index(records: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(record.get("document_id", "")): record
        for record in records
        if str(record.get("document_id", "")).strip()
    }


def load_manifest_documents(manifest_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    manifest = load_json(manifest_path)
    documents = current_manifest_documents(manifest)
    return manifest, documents, build_document_index(documents)


def load_baseline_documents(baseline_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    baseline = load_json(baseline_path)
    documents = list(baseline.get("documents", []))
    return baseline, documents, build_document_index(documents)


def changed_document_fields(current: dict[str, Any], previous: dict[str, Any]) -> list[str]:
    keys = (
        "checksum",
        "html_checksum",
        "normalized_relative_path",
        "view_relative_path",
        "viewer_url",
        "category",
        "version",
        "title",
    )
    return [key for key in keys if current.get(key) != previous.get(key)]


def diff_documents(
    current_documents: dict[str, dict[str, Any]],
    baseline_documents: dict[str, dict[str, Any]],
    *,
    mode: str,
) -> list[dict[str, Any]]:
    if mode not in {"delta", "seed"}:
        raise ValueError(f"unsupported mode: {mode}")

    changes: list[dict[str, Any]] = []
    if mode == "seed":
        for document_id in sorted(current_documents):
            current = current_documents[document_id]
            changes.append(
                {
                    "document_id": document_id,
                    "action": "added",
                    "current": current,
                    "previous": None,
                    "changed_fields": list(changed_document_fields(current, {})),
                }
            )
        return changes

    all_ids = sorted(set(current_documents) | set(baseline_documents))
    for document_id in all_ids:
        current = current_documents.get(document_id)
        previous = baseline_documents.get(document_id)
        if current and not previous:
            changes.append(
                {
                    "document_id": document_id,
                    "action": "added",
                    "current": current,
                    "previous": None,
                    "changed_fields": list(changed_document_fields(current, {})),
                }
            )
            continue
        if previous and not current:
            changes.append(
                {
                    "document_id": document_id,
                    "action": "removed",
                    "current": None,
                    "previous": previous,
                    "changed_fields": [],
                }
            )
            continue
        assert current is not None and previous is not None
        changed_fields = changed_document_fields(current, previous)
        if changed_fields:
            changes.append(
                {
                    "document_id": document_id,
                    "action": "changed",
                    "current": current,
                    "previous": previous,
                    "changed_fields": changed_fields,
                }
            )
    return changes


def iter_payload_files(bundle_root: Path) -> Iterable[Path]:
    for path in sorted(bundle_root.rglob("*")):
        if path.is_file() and path.name != "checksums.sha256":
            yield path


def write_checksum_manifest(bundle_root: Path) -> Path:
    lines: list[str] = []
    for path in iter_payload_files(bundle_root):
        relative = path.relative_to(bundle_root).as_posix()
        lines.append(f"{sha256_file(path)}  {relative}")
    checksum_path = bundle_root / "checksums.sha256"
    checksum_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return checksum_path
