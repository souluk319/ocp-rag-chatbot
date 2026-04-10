"""canonical AST를 사람이 읽는 플레이북 문서 구조로 투영한다."""

from __future__ import annotations

import json
from pathlib import Path

from .models import CanonicalDocumentAst, PlaybookDocumentArtifact, PlaybookSectionArtifact


def project_playbook_document(document: CanonicalDocumentAst) -> PlaybookDocumentArtifact:
    sections = tuple(
        PlaybookSectionArtifact(
            section_id=section.section_id,
            ordinal=section.ordinal,
            heading=section.heading,
            level=section.level,
            path=section.path,
            anchor=section.anchor,
            viewer_path=section.viewer_path,
            semantic_role=section.semantic_role,
            blocks=section.blocks,
        )
        for section in document.sections
    )
    quality_status = {
        "approved_ko": "ready",
        "translated_ko_draft": "review_required",
        "original": "translation_required",
    }.get(document.translation_status, "draft")
    quality_flags = list(document.notes)
    if document.translation_status != "approved_ko":
        quality_flags.append(document.translation_status)
    anchor_map = {
        section.anchor: section.viewer_path
        for section in document.sections
        if section.anchor.strip()
    }
    source_metadata = {
        "source_type": document.provenance.source_type or document.source_type,
        "source_lane": document.provenance.source_lane,
        "product": document.provenance.product or document.inferred_product,
        "version": document.provenance.version or document.inferred_version,
        "trust_score": document.provenance.trust_score,
        "original_url": document.source_url,
        "original_title": document.provenance.original_title or document.title,
        "translation_source_language": document.provenance.translation_source_language,
    }
    return PlaybookDocumentArtifact(
        book_slug=document.book_slug,
        title=document.title,
        source_uri=document.source_url,
        source_language=document.source_language,
        language_hint=document.display_language,
        translation_status=document.translation_status,
        translation_stage=document.provenance.translation_stage,
        translation_source_uri=document.provenance.translation_source_url or document.source_url,
        translation_source_language=document.provenance.translation_source_language or document.source_language,
        translation_source_fingerprint=document.provenance.translation_source_fingerprint,
        pack_id=document.pack_id,
        inferred_version=document.inferred_version,
        legal_notice_url=document.provenance.legal_notice_url,
        review_status=document.provenance.review_status,
        sections=sections,
        quality_status=quality_status,
        quality_flags=tuple(quality_flags),
        source_metadata=source_metadata,
        anchor_map=anchor_map,
    )


def write_playbook_documents(
    path: Path,
    books_dir: Path,
    documents: list[PlaybookDocumentArtifact],
) -> None:
    books_dir.mkdir(parents=True, exist_ok=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for document in documents:
            payload = document.to_dict()
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
            (books_dir / f"{document.book_slug}.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
