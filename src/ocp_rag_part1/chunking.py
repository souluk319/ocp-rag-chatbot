from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass

from .models import ChunkRecord, NormalizedSection
from .sentence_model import load_sentence_model
from .settings import Settings


def _split_text_for_tokenizer(text: str, max_chars: int) -> list[str]:
    if max_chars <= 0 or len(text) <= max_chars:
        return [text]

    parts: list[str] = []
    remaining = text
    minimum_split = max(1, max_chars // 2)

    while len(remaining) > max_chars:
        split_at = remaining.rfind("\n", 0, max_chars + 1)
        if split_at < minimum_split:
            split_at = remaining.rfind(" ", 0, max_chars + 1)
        if split_at < minimum_split:
            split_at = max_chars

        piece = remaining[:split_at].strip()
        if not piece:
            piece = remaining[:max_chars]
            split_at = max_chars
        parts.append(piece)
        remaining = remaining[split_at:].lstrip()

    if remaining.strip():
        parts.append(remaining.strip())
    return parts


@dataclass(slots=True)
class TokenCounter:
    model_name: str
    _encoder: object | None = None
    _load_error: Exception | None = None

    def _get_encoder(self):
        if self._encoder is None and self._load_error is None:
            try:
                self._encoder = load_sentence_model(self.model_name)
            except Exception as exc:  # noqa: BLE001
                self._load_error = exc
        if self._load_error is not None:
            raise ValueError(
                f"Failed to load sentence-transformer model '{self.model_name}'."
            ) from self._load_error
        return self._encoder

    def _get_tokenizer(self):
        return self._get_encoder().tokenizer

    def encode(self, text: str) -> list[int]:
        tokenizer = self._get_tokenizer()
        model_max_length = getattr(tokenizer, "model_max_length", 0)
        if not isinstance(model_max_length, int) or model_max_length <= 0:
            model_max_length = 2048
        max_chars = max(2000, model_max_length * 3)

        token_ids: list[int] = []
        for piece in _split_text_for_tokenizer(text, max_chars):
            encoded = tokenizer(
                piece,
                add_special_tokens=False,
                return_attention_mask=False,
                return_token_type_ids=False,
                verbose=False,
            )
            token_ids.extend(encoded["input_ids"])
        return token_ids

    def count(self, text: str) -> int:
        return len(self.encode(text))


def _section_prefix(section: NormalizedSection) -> str:
    path = " > ".join(part for part in section.section_path if part)
    if path:
        return f"{section.book_title}\n{path}\n\n"
    return f"{section.book_title}\n\n"


def _split_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    in_block = False
    end_tag = ""

    def flush() -> None:
        nonlocal current
        chunk = "\n".join(current).strip()
        if chunk:
            blocks.append(chunk)
        current = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped in {"[CODE]", "[TABLE]"}:
            flush()
            in_block = True
            end_tag = "[/CODE]" if stripped == "[CODE]" else "[/TABLE]"
            current.append(stripped)
            continue
        if in_block:
            current.append(line)
            if stripped == end_tag:
                flush()
                in_block = False
                end_tag = ""
            continue
        if stripped == "":
            flush()
            continue
        current.append(line)
    flush()
    return blocks


def _hard_split_text(text: str, token_counter: TokenCounter, chunk_size: int) -> list[str]:
    tokens = token_counter.encode(text)
    if len(tokens) <= chunk_size:
        return [text]
    tokenizer = token_counter._get_tokenizer()
    parts: list[str] = []
    for start in range(0, len(tokens), chunk_size):
        piece = tokenizer.decode(tokens[start : start + chunk_size]).strip()
        if piece:
            parts.append(piece)
    return parts


def chunk_sections(sections: list[NormalizedSection], settings: Settings) -> list[ChunkRecord]:
    token_counter = TokenCounter(settings.embedding_model)
    chunks: list[ChunkRecord] = []

    for section in sections:
        prefix = _section_prefix(section)
        blocks = _split_blocks(section.text)
        current_blocks: list[str] = []
        current_tokens = 0
        ordinal = 0

        def finalize() -> None:
            nonlocal current_blocks, current_tokens, ordinal
            if not current_blocks:
                return
            body = "\n\n".join(current_blocks).strip()
            final_text = f"{prefix}{body}".strip()
            token_count = token_counter.count(final_text)
            raw_key = f"{section.book_slug}:{section.anchor}:{ordinal}:{final_text}"
            chunk_id = str(uuid.uuid5(uuid.NAMESPACE_URL, raw_key))
            chunks.append(
                ChunkRecord(
                    chunk_id=chunk_id,
                    book_slug=section.book_slug,
                    book_title=section.book_title,
                    chapter=section.section_path[0] if section.section_path else section.book_title,
                    section=section.heading,
                    anchor=section.anchor,
                    source_url=section.source_url,
                    viewer_path=section.viewer_path,
                    text=final_text,
                    token_count=token_count,
                    ordinal=ordinal,
                )
            )
            ordinal += 1
            if settings.chunk_overlap <= 0:
                current_blocks = []
                current_tokens = 0
                return
            overlap_blocks: list[str] = []
            overlap_tokens = 0
            for block in reversed(current_blocks):
                block_tokens = token_counter.count(block)
                if overlap_tokens >= settings.chunk_overlap:
                    break
                overlap_blocks.insert(0, block)
                overlap_tokens += block_tokens
            current_blocks = overlap_blocks
            current_tokens = overlap_tokens

        for block in blocks:
            block_tokens = token_counter.count(block)
            if block_tokens > settings.chunk_size and block.startswith("[CODE]"):
                finalize()
                current_blocks = [block]
                current_tokens = block_tokens
                finalize()
                continue
            if block_tokens > settings.chunk_size:
                finalize()
                for piece in _hard_split_text(block, token_counter, settings.chunk_size):
                    current_blocks = [piece]
                    current_tokens = token_counter.count(piece)
                    finalize()
                continue
            if current_tokens and current_tokens + block_tokens > settings.chunk_size:
                finalize()
            current_blocks.append(block)
            current_tokens += block_tokens

        finalize()

    return chunks
