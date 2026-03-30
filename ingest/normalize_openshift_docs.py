from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_INCLUDE_DIRS = [
    "installing",
    "post_installation_configuration",
    "updating",
    "disconnected",
    "support",
]

DEFAULT_EXCLUDE_PREFIXES = (
    "osd_",
    "rosa_",
    "microshift_",
    "cloud_experts_",
)

DEFAULT_EXCLUDE_PATH_FRAGMENTS = (
    "/rosa-",
    "/rosa_",
    "-rosa-",
    "_rosa_",
    "/osd-",
    "/osd_",
    "-osd-",
    "_osd_",
    "/microshift-",
    "/microshift_",
    "-microshift-",
    "_microshift_",
    "/support/remote_health_monitoring/",
    "/support/troubleshooting/rosa-",
    "/support/troubleshooting/troubleshooting-osd-",
    "/support/troubleshooting/sd-",
)

DEFAULT_EXCLUDE_DIRS = {
    "modules",
    "snippets",
    "_topic_maps",
    "_images",
    "_templates",
    "_attributes",
    "_stylesheets",
    "_javascripts",
    "_converters",
    "_gemfiles",
    "ocm",
    "hosted_control_planes",
    "lightspeed",
    "migration_toolkit_for_containers",
    "contributing_to_docs",
}


@dataclass
class NormalizedDocument:
    document_id: str
    title: str
    source_id: str
    source_type: str
    source_url: str
    local_path: str
    normalized_path: str
    product: str
    version: str
    category: str
    language: str
    trust_level: str
    collected_at: str
    checksum: str
    top_level_dir: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize selected openshift-docs AsciiDoc content into plain text files for OpenDocuments indexing."
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path("../openshift-docs"),
        help="Path to the openshift-docs checkout",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./data/normalized/openshift-docs-p0"),
        help="Directory where normalized text files will be written",
    )
    parser.add_argument(
        "--manifest-out",
        type=Path,
        default=Path("./data/manifests/openshift-docs-p0.json"),
        help="Path to the generated manifest JSON file",
    )
    parser.add_argument(
        "--include-dir",
        action="append",
        dest="include_dirs",
        help="Top-level openshift-docs directory to include. Repeat to add more.",
    )
    parser.add_argument(
        "--source-id",
        default="openshift-docs-p0",
        help="Source identifier written to the manifest",
    )
    parser.add_argument(
        "--exclude-fragment",
        action="append",
        dest="exclude_fragments",
        help="Case-insensitive path fragment to exclude. Repeat to add more.",
    )
    parser.add_argument(
        "--version-label",
        default="4.x",
        help="Version label stored in the manifest",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List selected files without writing output",
    )
    parser.add_argument(
        "--show-documents",
        action="store_true",
        help="When used with --dry-run, print the full document list instead of a summary.",
    )
    return parser.parse_args()


def should_skip_top_level(name: str) -> bool:
    if name in DEFAULT_EXCLUDE_DIRS:
        return True
    return any(name.startswith(prefix) for prefix in DEFAULT_EXCLUDE_PREFIXES)


def normalize_match_path(relative_path: Path) -> str:
    return f"/{relative_path.as_posix().lower()}"


def skip_reason_for_path(relative_path: Path, exclude_fragments: list[str]) -> str | None:
    top_level = relative_path.parts[0]
    if should_skip_top_level(top_level):
        return f"top_level:{top_level}"

    normalized_path = normalize_match_path(relative_path)
    for fragment in exclude_fragments:
        if fragment.lower() in normalized_path:
            return f"path_fragment:{fragment}"
    return None


def collect_source_files(source_root: Path, include_dirs: list[str]) -> list[Path]:
    files: list[Path] = []
    for dirname in include_dirs:
        top_dir = source_root / dirname
        if not top_dir.exists():
            print(f"[warn] missing include dir: {top_dir}")
            continue
        files.extend(sorted(top_dir.rglob("*.adoc")))
    return files


def strip_asciidoc(text: str) -> str:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith(":"):
            continue
        if line.startswith("//"):
            continue
        if line.startswith("include::"):
            continue
        if line.startswith("ifdef::") or line.startswith("ifndef::") or line.startswith("endif::"):
            continue
        line = re.sub(r"^=+\s+", "", line)
        line = re.sub(r"xref:([^\[]+)\[([^\]]*)\]", r"\2", line)
        line = re.sub(r"link:([^\[]+)\[([^\]]*)\]", r"\2", line)
        line = re.sub(r"<<[^,>]+,([^>]+)>>", r"\1", line)
        line = re.sub(r"\{[^}]+\}", "", line)
        line = line.replace("`", "")
        lines.append(line)

    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def extract_title(source_text: str, fallback: str) -> str:
    for line in source_text.splitlines():
        if line.startswith("="):
            return re.sub(r"^=+\s+", "", line).strip() or fallback
    return fallback


def build_source_url(relative_path: Path) -> str:
    relative = relative_path.as_posix()
    return f"https://github.com/openshift/openshift-docs/blob/main/{relative}"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_document_id(relative_path: Path) -> str:
    return hashlib.sha1(relative_path.as_posix().encode("utf-8")).hexdigest()


def classify_category(relative_path: Path) -> str:
    top_level = relative_path.parts[0] if relative_path.parts else "other"
    mapping = {
        "installing": "install",
        "post_installation_configuration": "install",
        "updating": "upgrade",
        "upgrading": "upgrade",
        "networking": "networking",
        "security": "security",
        "storage": "storage",
        "backup_and_restore": "troubleshooting",
        "support": "troubleshooting",
        "observability": "troubleshooting",
    }
    return mapping.get(top_level, "other")


def write_normalized_file(output_dir: Path, relative_path: Path, title: str, body: str) -> Path:
    target = output_dir / relative_path.with_suffix(".txt")
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = f"Title: {title}\nSource Path: {relative_path.as_posix()}\n\n{body}\n"
    target.write_text(payload, encoding="utf-8")
    return target


def normalize_documents(args: argparse.Namespace) -> int:
    source_root = args.source_root.resolve()
    output_dir = args.output_dir.resolve()
    manifest_out = args.manifest_out.resolve()
    include_dirs = args.include_dirs or DEFAULT_INCLUDE_DIRS
    exclude_fragments = args.exclude_fragments or list(DEFAULT_EXCLUDE_PATH_FRAGMENTS)
    collected_at = datetime.now(timezone.utc).isoformat()

    if not source_root.exists():
        raise SystemExit(f"source root does not exist: {source_root}")

    source_files = collect_source_files(source_root, include_dirs)
    documents: list[NormalizedDocument] = []
    skipped = Counter()

    for source_file in source_files:
        relative_path = source_file.relative_to(source_root)
        skip_reason = skip_reason_for_path(relative_path, exclude_fragments)
        if skip_reason:
            skipped[skip_reason] += 1
            continue

        source_text = source_file.read_text(encoding="utf-8", errors="ignore")
        title = extract_title(source_text, source_file.stem)
        body = strip_asciidoc(source_text)
        if not body:
            skipped["empty_body"] += 1
            continue

        normalized_path = output_dir / relative_path.with_suffix(".txt")
        checksum = sha256_text(body)
        document = NormalizedDocument(
            document_id=stable_document_id(relative_path),
            title=title,
            source_id=args.source_id,
            source_type="git_mirror",
            source_url=build_source_url(relative_path),
            local_path=str(source_file),
            normalized_path=str(normalized_path),
            product="ocp",
            version=args.version_label,
            category=classify_category(relative_path),
            language="en",
            trust_level="official",
            collected_at=collected_at,
            checksum=checksum,
            top_level_dir=relative_path.parts[0],
        )
        documents.append(document)

        if not args.dry_run:
            write_normalized_file(output_dir, relative_path, title, body)

    manifest = {
        "manifest_id": f"{args.source_id}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "source_root": str(source_root),
        "source_id": args.source_id,
        "collected_at": collected_at,
        "scanned_adoc_count": len(source_files),
        "document_count": len(documents),
        "top_level_counts": dict(sorted(Counter(doc.top_level_dir for doc in documents).items())),
        "category_counts": dict(sorted(Counter(doc.category for doc in documents).items())),
        "skipped_counts": dict(sorted(skipped.items())),
        "documents": [document.__dict__ for document in documents],
    }

    if args.dry_run:
        if args.show_documents:
            print(json.dumps(manifest, indent=2))
            return 0

        summary = {key: value for key, value in manifest.items() if key != "documents"}
        summary["sample_documents"] = [
            {
                "title": document.title,
                "category": document.category,
                "top_level_dir": document.top_level_dir,
                "local_path": document.local_path,
            }
            for document in documents[:15]
        ]
        print(json.dumps(summary, indent=2))
        return 0

    manifest_out.parent.mkdir(parents=True, exist_ok=True)
    manifest_out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[ok] normalized {len(documents)} documents")
    print(f"[ok] manifest written to {manifest_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(normalize_documents(parse_args()))
