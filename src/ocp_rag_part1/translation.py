from __future__ import annotations

import json
import re
from dataclasses import replace
from typing import Iterable

import requests

from .models import NormalizedSection
from .section_keys import assign_section_keys
from .settings import Settings


BLOCK_RE = re.compile(r"(\[CODE\].*?\[/CODE\]|\[TABLE\].*?\[/TABLE\])", re.DOTALL)
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def contains_hangul(text: str) -> bool:
    return bool(HANGUL_RE.search(text or ""))


def normalize_translation_output(text: str) -> str:
    normalized = (text or "").strip()
    normalized = re.sub(r"^\s*(번역|translation)\s*[:：]\s*", "", normalized, flags=re.IGNORECASE)
    return normalized.strip()


def _split_long_paragraph(paragraph: str, *, max_chars: int) -> list[str]:
    stripped = (paragraph or "").strip()
    if len(stripped) <= max_chars:
        return [stripped] if stripped else []

    sentences = [item.strip() for item in SENTENCE_SPLIT_RE.split(stripped) if item.strip()]
    if len(sentences) <= 1:
        return [stripped[i : i + max_chars] for i in range(0, len(stripped), max_chars)]

    chunks: list[str] = []
    current: list[str] = []
    current_length = 0
    for sentence in sentences:
        extra = len(sentence) + (1 if current else 0)
        if current and current_length + extra > max_chars:
            chunks.append(" ".join(current).strip())
            current = [sentence]
            current_length = len(sentence)
            continue
        current.append(sentence)
        current_length += extra
    if current:
        chunks.append(" ".join(current).strip())
    return chunks


def split_text_for_translation(text: str, *, max_chars: int = 1800) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for part in BLOCK_RE.split(text or ""):
        if not part:
            continue
        stripped = part.strip()
        if not stripped:
            continue
        if stripped.startswith("[CODE]") and stripped.endswith("[/CODE]"):
            blocks.append(("raw", stripped))
            continue
        if stripped.startswith("[TABLE]") and stripped.endswith("[/TABLE]"):
            blocks.append(("raw", stripped))
            continue

        paragraphs = [item.strip() for item in re.split(r"\n\s*\n", stripped) if item.strip()]
        current: list[str] = []
        current_length = 0
        for paragraph in paragraphs:
            for piece in _split_long_paragraph(paragraph, max_chars=max_chars):
                extra = len(piece) + (2 if current else 0)
                if current and current_length + extra > max_chars:
                    blocks.append(("translate", "\n\n".join(current).strip()))
                    current = [piece]
                    current_length = len(piece)
                else:
                    current.append(piece)
                    current_length += extra
        if current:
            blocks.append(("translate", "\n\n".join(current).strip()))
    return blocks


class SectionTranslator:
    def __init__(self, settings: Settings) -> None:
        if not settings.llm_endpoint:
            raise ValueError("LLM_ENDPOINT must be configured")
        if not settings.llm_model:
            raise ValueError("LLM_MODEL must be configured")
        self.endpoint = settings.llm_endpoint
        self.model = settings.llm_model
        self.timeout = max(settings.request_timeout_seconds, 180)

    def _generate(self, messages: list[dict[str, str]], *, max_tokens: int) -> str:
        response = requests.post(
            f"{self.endpoint}/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "temperature": 0.0,
                "max_tokens": max_tokens,
                "reasoning": False,
                "chat_template_kwargs": {"enable_thinking": False},
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        choices = payload.get("choices") or []
        if not choices:
            raise ValueError("LLM response is missing choices")
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    parts.append(item["text"])
            content = "\n".join(parts).strip()
        if not isinstance(content, str) or not content.strip():
            raise ValueError("LLM response is missing message content")
        return normalize_translation_output(content)

    def translate_heading(self, heading: str) -> str:
        if not heading or contains_hangul(heading):
            return heading
        messages = [
            {
                "role": "system",
                "content": (
                    "Translate the OpenShift documentation heading into Korean. "
                    "Preserve product names, commands, API names, and version strings. "
                    "Return only the translated heading."
                ),
            },
            {"role": "user", "content": heading},
        ]
        return self._generate(messages, max_tokens=200)

    def translate_prose(self, text: str) -> str:
        if not text or contains_hangul(text):
            return text
        messages = [
            {
                "role": "system",
                "content": (
                    "Translate the following OpenShift documentation prose into natural Korean. "
                    "Do not add explanations. Preserve commands, shell snippets, file paths, "
                    "resource names, URLs, inline code, and version strings exactly as written. "
                    "Return only the translated Korean prose."
                ),
            },
            {"role": "user", "content": text},
        ]
        estimated_tokens = max(400, min(2200, len(text) // 2))
        return self._generate(messages, max_tokens=estimated_tokens)


def translate_section(
    translator: SectionTranslator,
    section: NormalizedSection,
    *,
    max_chars_per_call: int = 1800,
) -> NormalizedSection:
    translated_heading = translator.translate_heading(section.heading)
    translated_blocks: list[str] = []

    for kind, block_text in split_text_for_translation(section.text, max_chars=max_chars_per_call):
        if kind == "raw":
            translated_blocks.append(block_text)
            continue
        translated_blocks.append(translator.translate_prose(block_text))

    translated_text = "\n\n".join(block.strip() for block in translated_blocks if block.strip()).strip()
    return replace(
        section,
        book_title=translator.translate_heading(section.book_title),
        heading=translated_heading,
        text=translated_text or section.text,
    )


def read_sections(path: str | Settings) -> list[NormalizedSection]:
    source = path.normalized_docs_path if isinstance(path, Settings) else path
    rows: list[NormalizedSection] = []
    with open(source, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(NormalizedSection(**json.loads(line)))
    return assign_section_keys(rows)


def write_sections(path: str, sections: Iterable[NormalizedSection]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for section in sections:
            handle.write(json.dumps(section.to_dict(), ensure_ascii=False) + "\n")
