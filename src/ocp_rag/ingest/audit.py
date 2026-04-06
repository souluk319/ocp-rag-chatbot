from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup
from ocp_rag.shared.io import read_jsonl

from .manifest import read_manifest, write_manifest
from .models import SourceManifestEntry


HANGUL_SYLLABLE_RE = re.compile(r"[가-힣]")
HANGUL_JAMO_RE = re.compile(r"[ㄱ-ㅎㅏ-ㅣ]")
CJK_IDEOGRAPH_RE = re.compile(r"[\u4e00-\u9fff]")
SUSPICIOUS_TITLE_CHAR_RE = re.compile(r"[�]|[ㄱ-ㅎㅏ-ㅣ]|[\u4e00-\u9fff]")
LATIN_LETTER_RE = re.compile(r"[A-Za-z]")
LANGUAGE_FALLBACK_RE = re.compile(
    r"This content is not available in (the )?selected language|"
    r"이 콘텐츠는 선택한 언어로 제공되지 않습니다",
    re.IGNORECASE,
)


def looks_like_mojibake_title(text: str) -> bool:
    cleaned = " ".join((text or "").split()).strip()
    if not cleaned:
        return False
    if SUSPICIOUS_TITLE_CHAR_RE.search(cleaned):
        return True
    question_marks = cleaned.count("?")
    return question_marks >= 2


def _read_html_heading(path: Path) -> str:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    heading = soup.select_one("main#main-content article h1") or soup.select_one("article h1")
    if heading is not None:
        return " ".join(heading.get_text(" ", strip=True).split())
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    return " ".join(title.split())


def _viewer_path_matches_slug(viewer_path: str, slug: str) -> bool:
    return viewer_path == f"/docs/ocp/4.20/ko/{slug}/index.html"


def _source_url_matches_slug(source_url: str, slug: str) -> bool:
    return source_url.endswith(f"/html-single/{slug}/index")


def _hangul_ratio(texts: list[str]) -> float:
    if not texts:
        return 0.0
    hangul = sum(int(bool(HANGUL_SYLLABLE_RE.search(text or ""))) for text in texts)
    return round(hangul / len(texts), 4)


def _is_english_like_title(text: str) -> bool:
    cleaned = " ".join((text or "").split()).strip()
    if not cleaned:
        return False
    return bool(LATIN_LETTER_RE.search(cleaned)) and not bool(HANGUL_SYLLABLE_RE.search(cleaned))


def _body_language_guess(*, hangul_chunk_ratio: float, fallback_detected: bool) -> str:
    if fallback_detected or hangul_chunk_ratio < 0.05:
        return "en_only"
    if hangul_chunk_ratio < 0.85:
        return "mixed"
    return "ko"


def _classify_content_status(
    *,
    section_count: int,
    chunk_count: int,
    hangul_section_ratio: float,
    hangul_chunk_ratio: float,
    title_english_like: bool,
    fallback_detected: bool,
) -> tuple[str, str]:
    if section_count == 0 or chunk_count == 0:
        return "blocked", "missing normalized sections or chunks"
    if fallback_detected:
        return "en_only", "vendor page reports selected-language fallback"
    if hangul_chunk_ratio < 0.05:
        return "en_only", "chunk text is effectively non-Korean"
    if hangul_chunk_ratio < 0.85 or hangul_section_ratio < 0.85:
        return "mixed", "book mixes Korean and non-Korean body text"
    if title_english_like:
        return "mixed", "book title is English-like even though body is mostly Korean"
    return "approved_ko", ""


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
    manifest = read_manifest(settings.source_manifest_path)
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

        viewer_ok = _viewer_path_matches_slug(entry.viewer_path, slug)
        source_ok = _source_url_matches_slug(entry.source_url, slug)
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


def build_source_approval_report(settings) -> dict[str, object]:
    manifest = read_manifest(settings.source_manifest_path)
    normalized_docs = read_jsonl(settings.normalized_docs_path)
    chunks = read_jsonl(settings.chunks_path)

    sections_by_book: dict[str, list[dict]] = {}
    for row in normalized_docs:
        sections_by_book.setdefault(str(row["book_slug"]), []).append(row)

    chunks_by_book: dict[str, list[dict]] = {}
    for row in chunks:
        chunks_by_book.setdefault(str(row["book_slug"]), []).append(row)

    per_book: list[dict[str, object]] = []
    counts: Counter[str] = Counter()

    for entry in manifest:
        section_rows = sections_by_book.get(entry.book_slug, [])
        chunk_rows = chunks_by_book.get(entry.book_slug, [])
        html_path = settings.raw_html_dir / f"{entry.book_slug}.html"
        raw_html = html_path.read_text(encoding="utf-8") if html_path.exists() else ""
        fallback_detected = bool(LANGUAGE_FALLBACK_RE.search(raw_html))
        hangul_section_ratio = _hangul_ratio([str(row.get("text", "")) for row in section_rows])
        hangul_chunk_ratio = _hangul_ratio([str(row.get("text", "")) for row in chunk_rows])
        title_english_like = _is_english_like_title(entry.title)
        content_status, citation_block_reason = _classify_content_status(
            section_count=len(section_rows),
            chunk_count=len(chunk_rows),
            hangul_section_ratio=hangul_section_ratio,
            hangul_chunk_ratio=hangul_chunk_ratio,
            title_english_like=title_english_like,
            fallback_detected=fallback_detected,
        )
        body_language_guess = _body_language_guess(
            hangul_chunk_ratio=hangul_chunk_ratio,
            fallback_detected=fallback_detected,
        )
        citation_eligible = content_status == "approved_ko"
        approval_status = "approved" if citation_eligible else "needs_review"
        viewer_strategy = "internal_text"

        record = {
            "book_slug": entry.book_slug,
            "title": entry.title,
            "vendor_title": entry.vendor_title or entry.title,
            "high_value": entry.high_value,
            "section_count": len(section_rows),
            "chunk_count": len(chunk_rows),
            "hangul_section_ratio": hangul_section_ratio,
            "hangul_chunk_ratio": hangul_chunk_ratio,
            "title_english_like": title_english_like,
            "fallback_detected": fallback_detected,
            "body_language_guess": body_language_guess,
            "content_status": content_status,
            "citation_eligible": citation_eligible,
            "citation_block_reason": citation_block_reason,
            "viewer_strategy": viewer_strategy,
            "approval_status": approval_status,
            "approval_notes": "",
            "source_url": entry.source_url,
            "viewer_path": entry.viewer_path,
        }
        counts[content_status] += 1
        per_book.append(record)

    per_book.sort(
        key=lambda item: (
            {"approved_ko": 0, "mixed": 1, "en_only": 2, "blocked": 3}.get(
                str(item["content_status"]),
                9,
            ),
            -int(bool(item["high_value"])),
            str(item["book_slug"]),
        )
    )

    high_value_issues = [
        item
        for item in per_book
        if item["high_value"] and item["content_status"] != "approved_ko"
    ]

    return {
        "summary": {
            "book_count": len(per_book),
            "approved_ko_count": counts["approved_ko"],
            "mixed_count": counts["mixed"],
            "en_only_count": counts["en_only"],
            "blocked_count": counts["blocked"],
            "high_value_issue_count": len(high_value_issues),
        },
        "high_value_issues": high_value_issues,
        "books": per_book,
    }


def build_approved_manifest(
    settings,
    *,
    allowed_statuses: tuple[str, ...] = ("approved_ko",),
) -> list[SourceManifestEntry]:
    approval_report = build_source_approval_report(settings)
    books = approval_report["books"]
    entries: list[SourceManifestEntry] = []

    for item in books:
        if item["content_status"] not in allowed_statuses:
            continue
        entries.append(
            SourceManifestEntry(
                book_slug=str(item["book_slug"]),
                title=str(item["title"]),
                source_url=str(item["source_url"]),
                viewer_path=str(item["viewer_path"]),
                high_value=bool(item["high_value"]),
                vendor_title=str(item["vendor_title"]),
                content_status=str(item["content_status"]),
                citation_eligible=bool(item["citation_eligible"]),
                citation_block_reason=str(item["citation_block_reason"]),
                viewer_strategy=str(item["viewer_strategy"]),
                body_language_guess=str(item["body_language_guess"]),
                hangul_section_ratio=float(item["hangul_section_ratio"]),
                hangul_chunk_ratio=float(item["hangul_chunk_ratio"]),
                approval_status=str(item["approval_status"]),
                approval_notes=str(item["approval_notes"]),
            )
        )
    return entries


def write_approved_manifest(
    path: Path,
    entries: list[SourceManifestEntry],
) -> None:
    write_manifest(path, entries)
