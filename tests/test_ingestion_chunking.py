from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.ingestion import chunking
from play_book_studio.ingestion.chunking import TokenCounter
from play_book_studio.ingestion.models import NormalizedSection
from play_book_studio.config.settings import Settings


class _FakeTokenizer:
    def __init__(self) -> None:
        self.model_max_length = 8
        self.calls: list[str] = []

    def __call__(self, text: str, **_: object) -> dict[str, list[int]]:
        self.calls.append(text)
        return {"input_ids": [ord(char) for char in text]}


class _FakeSentenceModel:
    def __init__(self) -> None:
        self.tokenizer = _FakeTokenizer()


class ChunkingTests(unittest.TestCase):
    def test_invalid_sentence_model_raises_instead_of_falling_back_silently(self) -> None:
        counter = TokenCounter("definitely-not-a-real-sentence-model")
        with self.assertRaises(ValueError):
            counter.count("테스트 문장")

    def test_token_counter_splits_very_long_text_before_tokenizing(self) -> None:
        fake_model = _FakeSentenceModel()
        long_text = ("abcde " * 700).strip()
        with patch.object(chunking, "load_sentence_model", return_value=fake_model):
            counter = TokenCounter("dragonkue/bge-m3-ko")
            token_ids = counter.encode(long_text)

        self.assertGreater(len(fake_model.tokenizer.calls), 1)
        self.assertTrue(all(len(piece) <= 2000 for piece in fake_model.tokenizer.calls))
        self.assertEqual(len(token_ids), sum(len(piece) for piece in fake_model.tokenizer.calls))

    def test_reference_heavy_books_use_larger_chunk_profile(self) -> None:
        fake_model = _FakeSentenceModel()
        reference_section = NormalizedSection(
            book_slug="metadata_apis",
            book_title="Metadata API",
            heading="status reference",
            section_level=2,
            section_path=["Metadata API", "status reference"],
            anchor="status-reference",
            source_url="https://example.com/metadata",
            viewer_path="/docs/ocp/4.20/ko/metadata_apis/index.html#status-reference",
            text="\n\n".join(["x" * 100 for _ in range(5)]),
        )
        normal_section = NormalizedSection(
            book_slug="nodes",
            book_title="노드",
            heading="pod overview",
            section_level=2,
            section_path=["노드", "pod overview"],
            anchor="pod-overview",
            source_url="https://example.com/nodes",
            viewer_path="/docs/ocp/4.20/ko/nodes/index.html#pod-overview",
            text="\n\n".join(["x" * 100 for _ in range(5)]),
        )
        settings = Settings(root_dir=ROOT)
        with patch.object(chunking, "load_sentence_model", return_value=fake_model):
            reference_chunks = chunking.chunk_sections([reference_section], settings)
            normal_chunks = chunking.chunk_sections([normal_section], settings)

        self.assertLess(len(reference_chunks), len(normal_chunks))


if __name__ == "__main__":
    unittest.main()
