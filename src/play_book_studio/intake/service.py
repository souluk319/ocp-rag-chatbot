from __future__ import annotations

# intake 품질 판정과 공통 service helper를 모아둔 모듈.

import re


def evaluate_canonical_book_quality(payload: dict[str, object]) -> dict[str, object]:
    sections = [dict(section) for section in (payload.get("sections") or []) if isinstance(section, dict)]
    if not sections:
        return {
            "quality_status": "review",
            "quality_score": 0,
            "quality_flags": ["no_sections"],
            "quality_summary": "섹션이 없어 study asset으로 사용할 수 없습니다.",
        }

    headings = [str(section.get("heading") or "").strip() for section in sections]
    texts = [str(section.get("text") or "").strip() for section in sections]
    page_summary_count = sum(heading == "Page Summary" for heading in headings)
    same_text_count = sum(
        1
        for heading, text in zip(headings, texts)
        if heading and text and text == heading
    )
    short_text_count = sum(1 for text in texts if 0 < len(text) <= 30)
    chapter_footer_count = sum(
        1
        for text in texts
        if re.search(r"(?:^|\n)\s*\d+\s*장\s*\.\s*[^\n]{4,}(?:\n|$)", text)
    )
    toc_artifact_count = sum(
        1
        for text in texts
        if re.search(r"(?:\.\s*){8,}", text) or "table of contents" in text.lower()
    )

    total = max(len(sections), 1)
    page_summary_ratio = page_summary_count / total
    same_text_ratio = same_text_count / total
    short_text_ratio = short_text_count / total
    chapter_footer_ratio = chapter_footer_count / total
    toc_artifact_ratio = toc_artifact_count / total

    flags: list[str] = []
    score = 100
    if page_summary_ratio >= 0.25:
        flags.append("too_many_page_summary_sections")
        score -= 35
    if same_text_ratio >= 0.25:
        flags.append("too_many_heading_only_sections")
        score -= 30
    if len(sections) >= 8 and short_text_ratio >= 0.35:
        flags.append("too_many_short_sections")
        score -= 20
    if len(sections) >= 500:
        flags.append("section_count_too_high")
        score -= 15
    if len(sections) >= 8 and chapter_footer_ratio >= 0.12:
        flags.append("chapter_footer_contamination")
        score -= 20
    if toc_artifact_ratio >= 0.08:
        flags.append("toc_artifacts_remaining")
        score -= 15

    status = "ready" if score >= 70 and not flags else "review"
    summary = (
        "정규화 품질이 충분해 study asset으로 사용할 수 있습니다."
        if status == "ready"
        else "정규화 품질 검토가 필요합니다. section 구조가 아직 불안정합니다."
    )
    return {
        "quality_status": status,
        "quality_score": max(score, 0),
        "quality_flags": flags,
        "quality_summary": summary,
    }


__all__ = ["evaluate_canonical_book_quality"]
