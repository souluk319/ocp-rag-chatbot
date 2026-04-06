from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag.ingest import chunking
from ocp_rag.ingest.chunking import TokenCounter


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


if __name__ == "__main__":
    unittest.main()
