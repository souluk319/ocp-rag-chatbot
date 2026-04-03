from __future__ import annotations

import json
import re
from collections import Counter

from .manifest import read_manifest
from .validation import read_jsonl


HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")


def _contains_hangul(text: str) -> bool:
    return bool(HANGUL_RE.search(text or ""))


def classify_book_language_policy(
    *,
    book_slug: str,
    title: str,
    high_value: bool,
    section_count: int,
    hangul_section_ratio: float,
) -> dict[str, object]:
    importance_tier = "high" if high_value else "normal"

    if hangul_section_ratio >= 0.8:
        language_status = "ko_first"
        retrieval_policy = "normal"
        viewer_policy = "normal"
        translation_priority = "none"
        recommended_action = "keep"
        rationale = "한국어 본문 비중이 충분하므로 기본 코퍼스로 유지합니다."
    elif hangul_section_ratio >= 0.3:
        language_status = "mixed"
        retrieval_policy = "allow_with_warning"
        viewer_policy = "show_language_badge"
        translation_priority = "high" if high_value else "medium"
        recommended_action = "translate_candidate"
        rationale = (
            "한국어와 영어가 혼합되어 있어 citation 시 언어 상태 안내가 필요하며, "
            "중요도가 높으면 우선 번역 후보로 다룹니다."
        )
    elif high_value:
        language_status = "en_first"
        retrieval_policy = "allow_with_warning"
        viewer_policy = "show_language_badge"
        translation_priority = "urgent"
        recommended_action = "translate_priority"
        rationale = (
            "운영/교육 핵심 문서인데 영문 비중이 높으므로 기본 검색은 유지하되, "
            "답변과 viewer에 경고를 붙이고 번역 우선 대상으로 지정합니다."
        )
    else:
        language_status = "en_first"
        retrieval_policy = "exclude_default"
        viewer_policy = "show_language_badge"
        translation_priority = "low"
        recommended_action = "exclude_default"
        rationale = (
            "영문 비중이 높고 우선순위가 낮으므로 기본 검색에서는 제외하고 "
            "정책 검토 시에만 다시 활성화합니다."
        )

    return {
        "book_slug": book_slug,
        "title": title,
        "importance_tier": importance_tier,
        "section_count": section_count,
        "hangul_section_ratio": round(hangul_section_ratio, 4),
        "language_status": language_status,
        "retrieval_policy": retrieval_policy,
        "viewer_policy": viewer_policy,
        "translation_priority": translation_priority,
        "recommended_action": recommended_action,
        "rationale": rationale,
    }


def build_language_policy_report(settings) -> dict[str, object]:
    manifest = read_manifest(settings.source_manifest_path)
    normalized_docs = read_jsonl(settings.normalized_docs_path)

    section_counts: Counter[str] = Counter()
    hangul_section_counts: Counter[str] = Counter()
    titles_by_slug: dict[str, str] = {}

    for row in normalized_docs:
        book_slug = str(row["book_slug"])
        section_counts[book_slug] += 1
        if _contains_hangul(str(row.get("text", ""))):
            hangul_section_counts[book_slug] += 1
        titles_by_slug.setdefault(book_slug, str(row.get("book_title", "")))

    books: list[dict[str, object]] = []
    action_counts: Counter[str] = Counter()
    retrieval_policy_counts: Counter[str] = Counter()

    for entry in manifest:
        section_count = section_counts.get(entry.book_slug, 0)
        hangul_ratio = hangul_section_counts.get(entry.book_slug, 0) / max(section_count, 1)
        policy = classify_book_language_policy(
            book_slug=entry.book_slug,
            title=titles_by_slug.get(entry.book_slug, entry.title),
            high_value=entry.high_value,
            section_count=section_count,
            hangul_section_ratio=hangul_ratio,
        )
        action_counts[str(policy["recommended_action"])] += 1
        retrieval_policy_counts[str(policy["retrieval_policy"])] += 1
        books.append(policy)

    books.sort(
        key=lambda item: (
            {"urgent": 0, "high": 1, "medium": 2, "low": 3, "none": 4}.get(
                str(item["translation_priority"]), 99
            ),
            float(item["hangul_section_ratio"]),
            str(item["book_slug"]),
        )
    )

    return {
        "book_count": len(books),
        "summary": {
            "recommended_action_counts": dict(action_counts),
            "retrieval_policy_counts": dict(retrieval_policy_counts),
            "translate_priority_books": [
                item["book_slug"]
                for item in books
                if item["recommended_action"] == "translate_priority"
            ],
            "exclude_default_books": [
                item["book_slug"]
                for item in books
                if item["recommended_action"] == "exclude_default"
            ],
        },
        "books": books,
    }


def write_language_policy_report(settings) -> dict[str, object]:
    report = build_language_policy_report(settings)
    settings.language_policy_report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report


def load_language_policy_map(settings) -> dict[str, dict[str, object]]:
    if not settings.language_policy_report_path.exists():
        return {}
    payload = json.loads(settings.language_policy_report_path.read_text(encoding="utf-8"))
    books = payload.get("books", [])
    if not isinstance(books, list):
        return {}
    result: dict[str, dict[str, object]] = {}
    for item in books:
        if not isinstance(item, dict):
            continue
        book_slug = item.get("book_slug")
        if isinstance(book_slug, str) and book_slug:
            result[book_slug] = item
    return result


def describe_language_policy(policy: dict[str, object] | None) -> dict[str, str]:
    policy = policy or {}
    language_status = str(policy.get("language_status", "unknown"))
    recommended_action = str(policy.get("recommended_action", "review"))
    translation_priority = str(policy.get("translation_priority", "none"))

    if language_status == "ko_first":
        return {
            "badge": "한국어 우선",
            "tone": "normal",
            "note": "한국어 본문 비중이 높은 문서입니다.",
        }
    if language_status == "mixed":
        return {
            "badge": "혼합 문서",
            "tone": "warn",
            "note": "한국어와 영어 본문이 섞여 있습니다. 인용 내용을 한 번 더 확인하는 것이 좋습니다.",
        }
    if language_status == "en_first" and recommended_action == "exclude_default":
        return {
            "badge": "영문 우선 · 기본 검색 제외",
            "tone": "warn",
            "note": "영문 원문 비중이 높아 기본 검색에서는 제외되는 문서입니다.",
        }
    if language_status == "en_first":
        priority_label = "번역 우선" if translation_priority == "urgent" else "검토 필요"
        return {
            "badge": f"영문 우선 · {priority_label}",
            "tone": "warn",
            "note": "영문 원문 비중이 높은 문서입니다. 현재는 내부 viewer로 제공되지만 번역 우선 대상입니다.",
        }
    return {
        "badge": "언어 상태 점검 필요",
        "tone": "warn",
        "note": "문서 언어 상태를 자동 판정하지 못했습니다.",
    }
