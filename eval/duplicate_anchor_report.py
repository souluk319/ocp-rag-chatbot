from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report duplicate section anchors and titles inside a normalized manifest.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    documents = payload.get("documents", [])

    duplicate_anchor_documents = []
    duplicate_title_documents = []

    for document in documents:
        sections = document.get("sections", []) or []
        anchor_counts = Counter(str(section.get("section_anchor", "")).strip() for section in sections if str(section.get("section_anchor", "")).strip())
        title_counts = Counter(str(section.get("section_title", "")).strip().lower() for section in sections if str(section.get("section_title", "")).strip())

        duplicate_anchors = sorted(anchor for anchor, count in anchor_counts.items() if count > 1)
        duplicate_titles = sorted(title for title, count in title_counts.items() if count > 1)

        if duplicate_anchors:
            duplicate_anchor_documents.append(
                {
                    "document_id": document.get("document_id", ""),
                    "document_path": document.get("local_path", "") or document.get("source_url", ""),
                    "duplicate_anchors": duplicate_anchors,
                }
            )
        if duplicate_titles:
            duplicate_title_documents.append(
                {
                    "document_id": document.get("document_id", ""),
                    "document_path": document.get("local_path", "") or document.get("source_url", ""),
                    "duplicate_titles": duplicate_titles,
                }
            )

    report = {
        "manifest_path": str(args.manifest.resolve()),
        "document_count": len(documents),
        "documents_with_duplicate_anchors": len(duplicate_anchor_documents),
        "documents_with_duplicate_titles": len(duplicate_title_documents),
        "duplicate_anchor_documents": duplicate_anchor_documents[:50],
        "duplicate_title_documents": duplicate_title_documents[:50],
    }

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
