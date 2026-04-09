"""정규화된 HTML section을 canonical AST로 조립하는 helper."""

from __future__ import annotations

import re
from typing import Any

from play_book_studio.config.packs import resolve_ocp_core_pack
from play_book_studio.ingestion.models import (
    CONTENT_STATUS_APPROVED_KO,
    CONTENT_STATUS_TRANSLATED_KO_DRAFT,
    SourceManifestEntry,
)
from play_book_studio.ingestion.translation_lane import build_translation_metadata

from .models import (
    AstProvenance,
    CanonicalDocumentAst,
    CanonicalSectionAst,
    CodeBlock,
    NoteBlock,
    ParagraphBlock,
    PrerequisiteBlock,
    ProcedureBlock,
    ProcedureStep,
    TableBlock,
)


BLOCK_SPLIT_RE = re.compile(
    r"(\[CODE(?:\s+[^\]]+)?\].*?\[/CODE\]|\[TABLE(?:\s+[^\]]+)?\].*?\[/TABLE\])",
    re.DOTALL,
)
MARKER_ATTR_RE = re.compile(r'([a-z_]+)="((?:[^"\\]|\\.)*)"')
NOTE_PREFIX_RE = re.compile(r"^(주의|경고|중요|참고|팁|Warning|Caution|Important|Note|Tip)\s*[:：]\s*(.+)$", re.IGNORECASE)
PROCEDURE_LINE_RE = re.compile(r"^\s*(\d+)\.\s+(.+)$")
SUBSTEP_LINE_RE = re.compile(r"^\s*[-*]\s+(.+)$")
NUMERIC_CALLOUT_RE = re.compile(r"^\d+$")
PREREQUISITE_PREFIXES = ("사전 요구 사항", "사전 요구사항", "Prerequisites")
CODE_BLOCK_RE = re.compile(r"^\[CODE(?P<attrs>[^\]]*)\]\s*(?P<body>.*?)\s*\[/CODE\]$", re.DOTALL)
TABLE_BLOCK_RE = re.compile(r"^\[TABLE(?P<attrs>[^\]]*)\]\s*(?P<body>.*?)\s*\[/TABLE\]$", re.DOTALL)
LEADING_NOISE_BLOCK_RE = (
    re.compile(r"^Red Hat OpenShift Documentation Team(?:\s+법적 공지\s+초록)?$", re.IGNORECASE),
    re.compile(r"^법적 공지(?:\s+초록)?$", re.IGNORECASE),
    re.compile(r"^초록$", re.IGNORECASE),
    re.compile(r"^Legal Notice(?:\s+Abstract)?$", re.IGNORECASE),
)


def _translation_status(entry: SourceManifestEntry) -> str:
    if entry.content_status == CONTENT_STATUS_APPROVED_KO:
        return "approved_ko"
    if entry.content_status == CONTENT_STATUS_TRANSLATED_KO_DRAFT:
        return "translated_ko_draft"
    return "original"


def _split_prerequisite_items(text: str) -> tuple[str, ...]:
    body = text
    for prefix in PREREQUISITE_PREFIXES:
        if body.startswith(prefix):
            body = body[len(prefix) :].lstrip(":： ").strip()
            break
    if not body:
        return ()
    tokens = [part.strip() for part in re.split(r"\s+[•·]\s+|\s+-\s+", body) if part.strip()]
    if len(tokens) <= 1 and "," in body:
        tokens = [part.strip() for part in body.split(",") if part.strip()]
    return tuple(tokens)


def _parse_procedure_block(text: str) -> ProcedureBlock | None:
    raw_lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not raw_lines:
        return None
    steps: list[ProcedureStep] = []
    current_substeps: list[str] = []
    current_step: ProcedureStep | None = None

    def flush_step() -> None:
        nonlocal current_step, current_substeps
        if current_step is None:
            return
        steps.append(
            ProcedureStep(
                ordinal=current_step.ordinal,
                text=current_step.text,
                substeps=tuple(current_substeps),
            )
        )
        current_step = None
        current_substeps = []

    for line in raw_lines:
        step_match = PROCEDURE_LINE_RE.match(line)
        if step_match:
            flush_step()
            current_step = ProcedureStep(
                ordinal=int(step_match.group(1)),
                text=step_match.group(2).strip(),
            )
            continue
        substep_match = SUBSTEP_LINE_RE.match(line)
        if substep_match and current_step is not None:
            current_substeps.append(substep_match.group(1).strip())
            continue
        return None

    flush_step()
    return ProcedureBlock(tuple(steps)) if steps else None


def _parse_marker_attrs(text: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for key, value in MARKER_ATTR_RE.findall(text or ""):
        attrs[key.strip().lower()] = value.strip()
    return attrs


def _parse_bool_attr(value: str | None, default: bool) -> bool:
    if value is None or not value.strip():
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def _parse_plaintext_block(text: str):
    cleaned = text.strip()
    if not cleaned:
        return None
    note_match = NOTE_PREFIX_RE.match(cleaned)
    if note_match:
        variant_map = {
            "주의": "warning",
            "경고": "warning",
            "중요": "important",
            "참고": "note",
            "팁": "tip",
            "warning": "warning",
            "caution": "caution",
            "important": "important",
            "note": "note",
            "tip": "tip",
        }
        variant = variant_map.get(note_match.group(1).strip().lower(), "note")
        return NoteBlock(
            text=note_match.group(2).strip(),
            variant=variant,
            title=note_match.group(1).strip(),
        )

    if cleaned.startswith(PREREQUISITE_PREFIXES):
        items = _split_prerequisite_items(cleaned)
        if items:
            return PrerequisiteBlock(items)

    procedure = _parse_procedure_block(cleaned)
    if procedure is not None:
        return procedure

    return ParagraphBlock(cleaned)


def _blocks_from_text(text: str) -> tuple[object, ...]:
    blocks: list[object] = []
    for part in BLOCK_SPLIT_RE.split(text):
        if not part:
            continue
        chunk = part.strip()
        if not chunk:
            continue
        code_match = CODE_BLOCK_RE.match(chunk)
        if code_match:
            attrs = _parse_marker_attrs(code_match.group("attrs"))
            code = code_match.group("body").strip()
            blocks.append(
                CodeBlock(
                    code=code,
                    language=attrs.get("language", "shell") or "shell",
                    copy_text=attrs.get("copy_text", code),
                    wrap_hint=_parse_bool_attr(attrs.get("wrap_hint"), True),
                    overflow_hint=attrs.get("overflow_hint", "toggle") or "toggle",
                    caption=attrs.get("caption", ""),
                )
            )
            continue
        table_match = TABLE_BLOCK_RE.match(chunk)
        if table_match:
            attrs = _parse_marker_attrs(table_match.group("attrs"))
            table_body = table_match.group("body").strip()
            rows = [line.strip() for line in table_body.splitlines() if line.strip()]
            headers: tuple[str, ...] = ()
            table_rows: tuple[tuple[str, ...], ...] = ()
            if rows:
                headers = tuple(cell.strip() for cell in rows[0].split("|"))
                table_rows = tuple(
                    tuple(cell.strip() for cell in row.split("|"))
                    for row in rows[1:]
                )
            blocks.append(TableBlock(headers=headers, rows=table_rows, caption=attrs.get("caption", "")))
            continue
        for paragraph in re.split(r"\n\s*\n+", chunk):
            block = _parse_plaintext_block(paragraph)
            if block is not None:
                blocks.append(block)
    return tuple(blocks)


def _trim_leading_noise_blocks(blocks: tuple[object, ...]) -> tuple[object, ...]:
    trimmed = list(blocks)
    while trimmed:
        first = trimmed[0]
        text = ""
        if isinstance(first, ParagraphBlock):
            text = first.text.strip()
        elif isinstance(first, NoteBlock):
            text = first.text.strip()
        if not text:
            break
        if any(pattern.match(text) for pattern in LEADING_NOISE_BLOCK_RE):
            trimmed.pop(0)
            continue
        break
    return tuple(trimmed)


def _looks_like_block_caption(block: object) -> bool:
    if not isinstance(block, ParagraphBlock):
        return False
    text = block.text.strip()
    if not text or len(text) > 80:
        return False
    if NUMERIC_CALLOUT_RE.fullmatch(text):
        return False
    if re.search(r"[.!?]$", text):
        return False
    if PROCEDURE_LINE_RE.match(text):
        return False
    return True


def _merge_numeric_callouts(blocks: tuple[object, ...]) -> tuple[object, ...]:
    merged: list[object] = []
    index = 0
    while index < len(blocks):
        current = blocks[index]
        next_block = blocks[index + 1] if index + 1 < len(blocks) else None
        if (
            isinstance(current, ParagraphBlock)
            and isinstance(next_block, ParagraphBlock)
            and NUMERIC_CALLOUT_RE.fullmatch(current.text.strip())
        ):
            merged.append(
                ParagraphBlock(f"{current.text.strip()}. {next_block.text.strip()}".strip())
            )
            index += 2
            continue
        merged.append(current)
        index += 1
    return tuple(merged)


def _promote_block_captions(blocks: tuple[object, ...]) -> tuple[object, ...]:
    promoted: list[object] = []
    index = 0
    while index < len(blocks):
        current = blocks[index]
        next_block = blocks[index + 1] if index + 1 < len(blocks) else None
        if _looks_like_block_caption(current) and isinstance(next_block, CodeBlock):
            promoted.append(
                CodeBlock(
                    code=next_block.code,
                    language=next_block.language,
                    copy_text=next_block.copy_text,
                    wrap_hint=next_block.wrap_hint,
                    overflow_hint=next_block.overflow_hint,
                    caption=current.text.strip(),
                )
            )
            index += 2
            continue
        if _looks_like_block_caption(current) and isinstance(next_block, TableBlock):
            promoted.append(
                TableBlock(
                    headers=next_block.headers,
                    rows=next_block.rows,
                    caption=current.text.strip(),
                )
            )
            index += 2
            continue
        promoted.append(current)
        index += 1
    return tuple(promoted)


def _postprocess_blocks(blocks: tuple[object, ...]) -> tuple[object, ...]:
    return _promote_block_captions(_merge_numeric_callouts(blocks))


def _infer_semantic_role(
    *,
    heading: str,
    path: tuple[str, ...],
    blocks: tuple[object, ...],
) -> str:
    joined = " ".join((*path, heading)).lower()
    if "개요" in joined or "소개" in joined or heading.lower() == "overview":
        return "overview"
    if any(isinstance(block, ProcedureBlock) for block in blocks):
        return "procedure"
    if any(token in joined for token in ("절차", "설치", "구성", "설정", "배포", "업데이트", "백업", "복구", "문제 해결", "troubleshoot")):
        return "procedure"
    if any(token in joined for token in ("api", "reference", "참조", "spec", "status", "매개변수")):
        return "reference"
    if any(token in joined for token in ("개념", "이해", "아키텍처", "노드", "operator", "operators", "mco")):
        return "concept"
    if len(path) == 1 and path[0].lower() in {"overview", "개요"}:
        return "overview"
    return "unknown"


def _unique_anchor(anchor: str, seen_anchors: dict[str, int]) -> str:
    base = anchor.strip() or "section"
    ordinal = seen_anchors.get(base, 0) + 1
    seen_anchors[base] = ordinal
    if ordinal == 1:
        return base
    return f"{base}-{ordinal}"


def build_web_document_ast(
    *,
    entry: SourceManifestEntry,
    book_title: str,
    parsed_sections: list[dict[str, Any]],
) -> CanonicalDocumentAst:
    pack = resolve_ocp_core_pack(
        version=entry.ocp_version or "4.20",
        language=entry.docs_language or "ko",
    )
    sections: list[CanonicalSectionAst] = []
    seen_anchors: dict[str, int] = {}
    for ordinal, section in enumerate(parsed_sections, start=1):
        heading = str(section["heading"]).strip()
        anchor = _unique_anchor(str(section["anchor"]).strip(), seen_anchors)
        text = str(section["text"]).strip()
        path = tuple(str(part).strip() for part in section["section_path"] if str(part).strip())
        blocks = _postprocess_blocks(_trim_leading_noise_blocks(_blocks_from_text(text)))
        semantic_role = _infer_semantic_role(heading=heading, path=path, blocks=blocks)
        sections.append(
            CanonicalSectionAst(
                section_id=f"{entry.book_slug}:{anchor}",
                ordinal=ordinal,
                heading=heading,
                level=int(section["section_level"]),
                path=path,
                anchor=anchor,
                source_url=entry.source_url,
                viewer_path=f"{entry.viewer_path}#{anchor}",
                semantic_role=semantic_role,
                blocks=blocks,
            )
        )

    provenance_notes: list[str] = []
    if entry.fallback_detected:
        provenance_notes.append("fallback_detected")
    if entry.source_state_reason.strip():
        provenance_notes.append(entry.source_state_reason.strip())
    translation = build_translation_metadata(entry, content_status=entry.content_status)

    return CanonicalDocumentAst(
        doc_id=f"{entry.book_slug}:{entry.ocp_version}:{entry.docs_language}",
        book_slug=entry.book_slug,
        title=book_title,
        source_type="web",
        source_url=entry.source_url,
        viewer_base_path=entry.viewer_path,
        source_language=entry.resolved_language or entry.docs_language or "ko",
        display_language=entry.docs_language or "ko",
        translation_status=_translation_status(entry),
        pack_id=pack.pack_id,
        pack_label=pack.pack_label,
        inferred_product=pack.product_key,
        inferred_version=pack.version,
        sections=tuple(sections),
        provenance=AstProvenance(
            source_fingerprint=entry.source_fingerprint,
            parser_name="canonical_html_v1",
            parser_version="1.0",
            source_state=entry.source_state,
            content_status=entry.content_status,
            translation_stage=str(translation["stage"]),
            translation_source_language=str(translation["source_language"]),
            translation_target_language=str(translation["target_language"]),
            translation_source_url=str(translation["source_url"]),
            translation_source_fingerprint=str(translation["source_fingerprint"]),
            notes=tuple(provenance_notes),
        ),
    )
