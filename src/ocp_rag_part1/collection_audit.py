from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from .language_policy import load_language_policy_map
from .manifest import read_manifest


BOOK_XML_LANG_RE = re.compile(r'xml:lang="([^"]+)" class="book"')


def extract_book_xml_lang(raw_html: str) -> str:
    match = BOOK_XML_LANG_RE.search(raw_html or "")
    if not match:
        return ""
    return match.group(1).strip()


def classify_collection_status(*, source_url: str, xml_lang: str, raw_exists: bool) -> str:
    normalized_url = (source_url or "").strip().lower()
    normalized_lang = (xml_lang or "").strip().lower()
    is_ko_url = "/ko/documentation/" in normalized_url

    if not raw_exists:
        return "missing_raw_html"
    if not is_ko_url:
        return "collector_misroute"
    if normalized_lang.startswith("ko"):
        return "ko_variant_ok"
    if normalized_lang.startswith("en"):
        return "vendor_english_fallback"
    return "unknown_language_state"


def build_collection_audit_report(settings) -> dict[str, object]:
    manifest = read_manifest(settings.source_manifest_path)
    language_policy_map = load_language_policy_map(settings)

    books: list[dict[str, object]] = []
    status_counts: Counter[str] = Counter()

    for entry in manifest:
        raw_path = settings.raw_html_dir / f"{entry.book_slug}.html"
        raw_exists = raw_path.exists()
        raw_html = raw_path.read_text(encoding="utf-8", errors="ignore") if raw_exists else ""
        xml_lang = extract_book_xml_lang(raw_html)
        collection_status = classify_collection_status(
            source_url=entry.source_url,
            xml_lang=xml_lang,
            raw_exists=raw_exists,
        )
        status_counts[collection_status] += 1

        policy = language_policy_map.get(entry.book_slug, {})
        books.append(
            {
                "book_slug": entry.book_slug,
                "title": entry.title,
                "high_value": entry.high_value,
                "source_url": entry.source_url,
                "raw_html_path": str(raw_path),
                "raw_exists": raw_exists,
                "xml_lang": xml_lang,
                "collection_status": collection_status,
                "language_status": str(policy.get("language_status", "")),
                "retrieval_policy": str(policy.get("retrieval_policy", "")),
                "recommended_action": str(policy.get("recommended_action", "")),
                "translation_priority": str(policy.get("translation_priority", "")),
            }
        )

    books.sort(
        key=lambda item: (
            {
                "vendor_english_fallback": 0,
                "collector_misroute": 1,
                "missing_raw_html": 2,
                "unknown_language_state": 3,
                "ko_variant_ok": 4,
            }.get(str(item["collection_status"]), 99),
            str(item["book_slug"]),
        )
    )

    vendor_fallback_books = [
        item["book_slug"]
        for item in books
        if item["collection_status"] == "vendor_english_fallback"
    ]
    translate_priority_books = [
        item["book_slug"]
        for item in books
        if item["recommended_action"] == "translate_priority"
    ]
    exclude_default_books = [
        item["book_slug"]
        for item in books
        if item["recommended_action"] == "exclude_default"
    ]

    return {
        "book_count": len(books),
        "summary": {
            "collection_status_counts": dict(status_counts),
            "vendor_fallback_books": vendor_fallback_books,
            "translate_priority_books": translate_priority_books,
            "exclude_default_books": exclude_default_books,
            "collector_misroute_books": [
                item["book_slug"]
                for item in books
                if item["collection_status"] == "collector_misroute"
            ],
            "missing_raw_html_books": [
                item["book_slug"]
                for item in books
                if item["collection_status"] == "missing_raw_html"
            ],
        },
        "books": books,
    }


def write_collection_audit_report(settings) -> dict[str, object]:
    report = build_collection_audit_report(settings)
    settings.collection_audit_report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report

