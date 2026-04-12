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

    def test_split_blocks_preserves_attributed_code_markers(self) -> None:
        text = """
        소개 문단입니다.

        [CODE language="yaml" wrap_hint="true"]
        kind: Pod
        metadata:
          name: demo
        [/CODE]

        다음 설명입니다.
        """.strip()

        blocks = chunking._split_blocks(text)

        self.assertEqual(3, len(blocks))
        self.assertEqual("소개 문단입니다.", blocks[0])
        self.assertTrue(blocks[1].startswith('[CODE language="yaml" wrap_hint="true"]'))
        self.assertTrue(blocks[1].endswith("[/CODE]"))
        self.assertEqual("다음 설명입니다.", blocks[2])

    def test_chunk_sections_preserve_operational_metadata(self) -> None:
        fake_model = _FakeSentenceModel()
        section = NormalizedSection(
            book_slug="ingress",
            book_title="Ingress troubleshooting",
            heading="Router check",
            section_level=2,
            section_path=["Ingress troubleshooting", "Router check"],
            anchor="router-check",
            source_url="https://example.com/ingress",
            viewer_path="/docs/ocp/4.20/ko/ingress/index.html#router-check",
            text="확인: Route 상태를 점검합니다.\n\n[CODE]\noc get pods -n openshift-ingress\n[/CODE]",
            source_id="src-1",
            source_lane="official_ko",
            source_type="official_doc",
            source_collection="core",
            product="openshift",
            version="4.20",
            locale="ko",
            cli_commands=("oc get pods -n openshift-ingress",),
            error_strings=("ImagePullBackOff",),
            k8s_objects=("Route", "Deployment"),
            operator_names=("Ingress Operator",),
            verification_hints=("확인: Route 상태를 점검합니다.", "oc get pods -n openshift-ingress"),
        )
        settings = Settings(root_dir=ROOT)

        with patch.object(chunking, "load_sentence_model", return_value=fake_model):
            chunks = chunking.chunk_sections([section], settings)

        self.assertEqual(1, len(chunks))
        chunk = chunks[0]
        self.assertEqual(("oc get pods -n openshift-ingress",), chunk.cli_commands)
        self.assertEqual(("ImagePullBackOff",), chunk.error_strings)
        self.assertEqual(("Route", "Deployment"), chunk.k8s_objects)
        self.assertEqual(("Ingress Operator",), chunk.operator_names)
        self.assertEqual(
            ("확인: Route 상태를 점검합니다.", "oc get pods -n openshift-ingress"),
            chunk.verification_hints,
        )
        self.assertEqual("src-1", chunk.source_id)
        self.assertEqual("official_doc", chunk.source_type)
        self.assertEqual(["oc get pods -n openshift-ingress"], chunk.to_dict()["cli_commands"])
        self.assertEqual(["ImagePullBackOff"], chunk.to_dict()["error_strings"])
        self.assertEqual(["Route", "Deployment"], chunk.to_dict()["k8s_objects"])
        self.assertEqual(["Ingress Operator"], chunk.to_dict()["operator_names"])
        self.assertEqual(
            ["확인: Route 상태를 점검합니다.", "oc get pods -n openshift-ingress"],
            chunk.to_dict()["verification_hints"],
        )


if __name__ == "__main__":
    unittest.main()
