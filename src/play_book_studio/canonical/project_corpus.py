"""canonical AST를 retrieval/corpus용 평탄 구조로 투영한다."""

from __future__ import annotations

from dataclasses import dataclass

from .models import (
    AnchorBlock,
    CanonicalDocumentAst,
    CodeBlock,
    NoteBlock,
    ParagraphBlock,
    PrerequisiteBlock,
    ProcedureBlock,
    TableBlock,
)


@dataclass(slots=True)
class CorpusSectionProjection:
    section_id: str
    book_slug: str
    book_title: str
    heading: str
    section_level: int
    section_path: tuple[str, ...]
    anchor: str
    source_url: str
    viewer_path: str
    semantic_role: str
    block_kinds: tuple[str, ...]
    source_language: str
    display_language: str
    translation_status: str
    translation_stage: str
    translation_source_language: str
    translation_source_url: str
    translation_source_fingerprint: str
    text: str

    def to_dict(self) -> dict[str, object]:
        return {
            "section_id": self.section_id,
            "book_slug": self.book_slug,
            "book_title": self.book_title,
            "heading": self.heading,
            "section_level": self.section_level,
            "section_path": list(self.section_path),
            "anchor": self.anchor,
            "source_url": self.source_url,
            "viewer_path": self.viewer_path,
            "semantic_role": self.semantic_role,
            "block_kinds": list(self.block_kinds),
            "source_language": self.source_language,
            "display_language": self.display_language,
            "translation_status": self.translation_status,
            "translation_stage": self.translation_stage,
            "translation_source_language": self.translation_source_language,
            "translation_source_url": self.translation_source_url,
            "translation_source_fingerprint": self.translation_source_fingerprint,
            "text": self.text,
        }


def _flatten_block(block) -> str:
    if isinstance(block, ParagraphBlock):
        return block.text.strip()
    if isinstance(block, PrerequisiteBlock):
        if not block.items:
            return ""
        return "사전 요구 사항:\n" + "\n".join(f"- {item}" for item in block.items if item.strip())
    if isinstance(block, ProcedureBlock):
        lines: list[str] = []
        for step in block.steps:
            if not step.text.strip():
                continue
            lines.append(f"{step.ordinal}. {step.text.strip()}")
            for substep in step.substeps:
                if substep.strip():
                    lines.append(f"- {substep.strip()}")
        return "\n".join(lines)
    if isinstance(block, CodeBlock):
        return f"[CODE]\n{block.code.strip()}\n[/CODE]"
    if isinstance(block, NoteBlock):
        label = block.variant.upper()
        title = f" {block.title.strip()}" if block.title.strip() else ""
        return f"[{label}]{title} {block.text.strip()}".strip()
    if isinstance(block, TableBlock):
        rows: list[str] = []
        if block.headers:
            rows.append(" | ".join(header.strip() for header in block.headers))
        rows.extend(" | ".join(cell.strip() for cell in row) for row in block.rows)
        table_text = "\n".join(rows).strip()
        return f"[TABLE]\n{table_text}\n[/TABLE]"
    if isinstance(block, AnchorBlock):
        return ""
    return ""


def project_corpus_sections(document: CanonicalDocumentAst) -> list[CorpusSectionProjection]:
    rows: list[CorpusSectionProjection] = []
    for section in document.sections:
        parts = [_flatten_block(block) for block in section.blocks]
        text = "\n\n".join(part for part in parts if part.strip()).strip()
        rows.append(
            CorpusSectionProjection(
                section_id=section.section_id,
                book_slug=document.book_slug,
                book_title=document.title,
                heading=section.heading,
                section_level=section.level,
                section_path=section.path,
                anchor=section.anchor,
                source_url=section.source_url,
                viewer_path=section.viewer_path,
                semantic_role=section.semantic_role,
                block_kinds=section.block_kinds,
                source_language=document.source_language,
                display_language=document.display_language,
                translation_status=document.translation_status,
                translation_stage=document.provenance.translation_stage,
                translation_source_language=document.provenance.translation_source_language,
                translation_source_url=document.provenance.translation_source_url,
                translation_source_fingerprint=document.provenance.translation_source_fingerprint,
                text=text,
            )
        )
    return rows
