# ingestion 산출물의 제목/본문/경로 품질을 검사해서 data quality 리포트를 만든다.
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup

from .audit_rules import CJK_IDEOGRAPH_RE, HANGUL_JAMO_RE, HANGUL_SYLLABLE_RE, looks_like_mojibake_title
from .manifest import read_manifest, runtime_catalog_entries
from .validation import read_jsonl


def _read_html_heading(path: Path) -> str:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    heading = soup.select_one("main#main-content article h1") or soup.select_one("article h1")
    if heading is not None:
        return " ".join(heading.get_text(" ", strip=True).split())
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    return " ".join(title.split())


def _viewer_path_matches_slug(viewer_path: str, slug: str, *, settings) -> bool:
    template = getattr(settings, "viewer_path_template", "/docs/ocp/{version}/{lang}/{slug}/index.html")
    version = getattr(settings, "ocp_version", "4.20")
    language = getattr(settings, "docs_language", "ko")
    return viewer_path == template.format(version=version, lang=language, slug=slug)


def _source_url_matches_slug(source_url: str, slug: str, *, settings) -> bool:
    template = getattr(
        settings,
        "book_url_template",
        "https://docs.redhat.com/{lang}/documentation/openshift_container_platform/{version}/html-single/{slug}/index",
    )
    version = getattr(settings, "ocp_version", "4.20")
    language = getattr(settings, "docs_language", "ko")
    return source_url == template.format(version=version, lang=language, slug=slug)


def _chunk_text_quality(rows: list[dict]) -> dict[str, object]:
    total_rows = len(rows)
    hangul_rows = 0
    suspicious_rows = 0
    suspicious_examples: list[dict[str, str]] = []
    per_book_totals: Counter[str] = Counter()
    per_book_suspicious: Counter[str] = Counter()

    for row in rows:
        text = str(row.get("text", ""))
        book_slug = str(row.get("book_slug", ""))
        per_book_totals[book_slug] += 1
        if HANGUL_SYLLABLE_RE.search(text):
            hangul_rows += 1
        suspicious_score = (
            len(HANGUL_JAMO_RE.findall(text))
            + len(CJK_IDEOGRAPH_RE.findall(text))
            + text.count("�") * 3
        )
        if suspicious_score >= 4:
            suspicious_rows += 1
            per_book_suspicious[book_slug] += 1
            if len(suspicious_examples) < 5:
                suspicious_examples.append(
                    {
                        "book_slug": book_slug,
                        "section": str(row.get("section", "")),
                        "text_preview": text[:200],
                    }
                )

    suspicious_books: list[dict[str, object]] = []
    for book_slug, total in per_book_totals.items():
        suspicious = per_book_suspicious.get(book_slug, 0)
        if suspicious == 0:
            continue
        suspicious_books.append(
            {
                "book_slug": book_slug,
                "suspicious_chunk_count": suspicious,
                "chunk_count": total,
                "suspicious_ratio": round(suspicious / total, 4),
            }
        )
    suspicious_books.sort(key=lambda item: (-float(item["suspicious_ratio"]), item["book_slug"]))

    return {
        "chunk_count": total_rows,
        "hangul_chunk_ratio": round(hangul_rows / max(total_rows, 1), 4),
        "suspicious_chunk_count": suspicious_rows,
        "suspicious_chunk_ratio": round(suspicious_rows / max(total_rows, 1), 4),
        "suspicious_books": suspicious_books[:20],
        "suspicious_examples": suspicious_examples,
    }


def build_data_quality_report(settings) -> dict[str, object]:
    manifest = runtime_catalog_entries(read_manifest(settings.source_catalog_path), settings)
    normalized_docs = read_jsonl(settings.normalized_docs_path)
    chunks = read_jsonl(settings.chunks_path)
    bm25_rows = read_jsonl(settings.bm25_corpus_path)
    preprocessing_log = json.loads(settings.preprocessing_log_path.read_text(encoding="utf-8"))

    normalized_titles: dict[str, str] = {}
    for row in normalized_docs:
        slug = str(row["book_slug"])
        normalized_titles.setdefault(slug, str(row["book_title"]))

    chunk_titles: dict[str, str] = {}
    for row in chunks:
        slug = str(row["book_slug"])
        chunk_titles.setdefault(slug, str(row["book_title"]))

    preprocessing_titles = {
        str(item.get("book_slug")): str(item.get("title", ""))
        for item in preprocessing_log.get("per_book_stats", [])
        if item.get("book_slug")
    }

    raw_html_titles: dict[str, str] = {}
    for entry in manifest:
        html_path = settings.raw_html_dir / f"{entry.book_slug}.html"
        if html_path.exists():
            raw_html_titles[entry.book_slug] = _read_html_heading(html_path)

    per_book: list[dict[str, object]] = []
    manifest_mojibake = 0
    preprocessing_mojibake = 0
    normalized_mojibake = 0
    chunk_mojibake = 0
    raw_html_mojibake = 0
    manifest_raw_mismatch = 0
    normalized_raw_mismatch = 0
    chunk_raw_mismatch = 0
    bad_viewer_paths = 0
    bad_source_urls = 0

    for entry in manifest:
        slug = entry.book_slug
        manifest_title = entry.title
        preprocessing_title = preprocessing_titles.get(slug, "")
        normalized_title = normalized_titles.get(slug, "")
        chunk_title = chunk_titles.get(slug, "")
        raw_html_title = raw_html_titles.get(slug, "")

        manifest_flag = looks_like_mojibake_title(manifest_title)
        preprocessing_flag = looks_like_mojibake_title(preprocessing_title)
        normalized_flag = looks_like_mojibake_title(normalized_title)
        chunk_flag = looks_like_mojibake_title(chunk_title)
        raw_html_flag = looks_like_mojibake_title(raw_html_title)

        manifest_mojibake += int(manifest_flag)
        preprocessing_mojibake += int(preprocessing_flag)
        normalized_mojibake += int(normalized_flag)
        chunk_mojibake += int(chunk_flag)
        raw_html_mojibake += int(raw_html_flag)

        manifest_match = bool(raw_html_title) and manifest_title == raw_html_title
        normalized_match = bool(raw_html_title) and normalized_title == raw_html_title
        chunk_match = bool(raw_html_title) and chunk_title == raw_html_title

        manifest_raw_mismatch += int(bool(raw_html_title) and not manifest_match)
        normalized_raw_mismatch += int(bool(raw_html_title) and not normalized_match)
        chunk_raw_mismatch += int(bool(raw_html_title) and not chunk_match)

        viewer_ok = _viewer_path_matches_slug(entry.viewer_path, slug, settings=settings)
        source_ok = _source_url_matches_slug(entry.source_url, slug, settings=settings)
        bad_viewer_paths += int(not viewer_ok)
        bad_source_urls += int(not source_ok)

        if any(
            (
                manifest_flag,
                preprocessing_flag,
                normalized_flag,
                chunk_flag,
                raw_html_flag,
                not viewer_ok,
                not source_ok,
                bool(raw_html_title) and not manifest_match,
            )
        ):
            per_book.append(
                {
                    "book_slug": slug,
                    "manifest_title": manifest_title,
                    "preprocessing_title": preprocessing_title,
                    "normalized_title": normalized_title,
                    "chunk_title": chunk_title,
                    "raw_html_title": raw_html_title,
                    "manifest_title_mojibake": manifest_flag,
                    "preprocessing_title_mojibake": preprocessing_flag,
                    "normalized_title_mojibake": normalized_flag,
                    "chunk_title_mojibake": chunk_flag,
                    "raw_html_title_mojibake": raw_html_flag,
                    "manifest_matches_raw_html": manifest_match,
                    "normalized_matches_raw_html": normalized_match,
                    "chunk_matches_raw_html": chunk_match,
                    "viewer_path_ok": viewer_ok,
                    "source_url_ok": source_ok,
                }
            )

    text_audit = _chunk_text_quality(chunks)

    return {
        "artifact_scope": {
            "manifest_count": len(manifest),
            "normalized_doc_count": len(normalized_docs),
            "chunk_count": len(chunks),
            "bm25_row_count": len(bm25_rows),
            "raw_html_count": len(raw_html_titles),
        },
        "title_audit": {
            "manifest_mojibake_count": manifest_mojibake,
            "preprocessing_log_mojibake_count": preprocessing_mojibake,
            "normalized_title_mojibake_count": normalized_mojibake,
            "chunk_title_mojibake_count": chunk_mojibake,
            "raw_html_title_mojibake_count": raw_html_mojibake,
            "manifest_raw_html_mismatch_count": manifest_raw_mismatch,
            "normalized_raw_html_mismatch_count": normalized_raw_mismatch,
            "chunk_raw_html_mismatch_count": chunk_raw_mismatch,
        },
        "path_audit": {
            "bad_viewer_path_count": bad_viewer_paths,
            "bad_source_url_count": bad_source_urls,
        },
        "text_audit": text_audit,
        "sample_issues": per_book[:25],
        "checks": {
            "raw_html_titles_clean": raw_html_mojibake == 0,
            "normalized_titles_clean": normalized_mojibake == 0,
            "chunk_titles_clean": chunk_mojibake == 0,
            "manifest_titles_clean": manifest_mojibake == 0,
            "preprocessing_titles_clean": preprocessing_mojibake == 0,
            "viewer_paths_valid": bad_viewer_paths == 0,
            "source_urls_valid": bad_source_urls == 0,
            "chunk_text_suspicious_ratio_below_1pct": text_audit["suspicious_chunk_ratio"] < 0.01,
        },
    }
