from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag.answering import Answerer, Part3Answerer
from ocp_rag.retrieval import Part2Retriever, Retriever


class CoreV2NamesTests(unittest.TestCase):
    def test_retriever_alias_points_to_canonical_class(self) -> None:
        self.assertIs(Retriever, Part2Retriever)

    def test_answerer_alias_points_to_canonical_class(self) -> None:
        self.assertIs(Answerer, Part3Answerer)


if __name__ == "__main__":
    unittest.main()
