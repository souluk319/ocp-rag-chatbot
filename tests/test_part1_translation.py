from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.translation import normalize_translation_output, split_text_for_translation


class TranslationTests(unittest.TestCase):
    def test_split_text_for_translation_preserves_code_blocks(self) -> None:
        text = "First paragraph.\n\n[CODE]\noc get nodes\n[/CODE]\n\nSecond paragraph."

        blocks = split_text_for_translation(text, max_chars=40)

        self.assertEqual(
            [
                ("translate", "First paragraph."),
                ("raw", "[CODE]\noc get nodes\n[/CODE]"),
                ("translate", "Second paragraph."),
            ],
            blocks,
        )

    def test_normalize_translation_output_removes_translation_prefix(self) -> None:
        self.assertEqual("한국어 결과", normalize_translation_output("번역: 한국어 결과"))


if __name__ == "__main__":
    unittest.main()
