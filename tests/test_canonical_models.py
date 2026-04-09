from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.canonical.models import (
    AstProvenance,
    CanonicalDocumentAst,
    CanonicalSectionAst,
    CodeBlock,
    NoteBlock,
    ParagraphBlock,
    PlaybookDocumentArtifact,
    PrerequisiteBlock,
    ProcedureBlock,
    ProcedureStep,
    TableBlock,
)
from play_book_studio.canonical.project_corpus import project_corpus_sections
from play_book_studio.canonical.project_playbook import project_playbook_document
from play_book_studio.canonical.translate import translate_document_ast
from play_book_studio.canonical.validate import validate_document_ast


class CanonicalModelTests(unittest.TestCase):
    def _sample_document(self) -> CanonicalDocumentAst:
        return CanonicalDocumentAst(
            doc_id="ocp-4-20-nodes",
            book_slug="nodes",
            title="노드",
            source_type="web",
            source_url="https://example.com/nodes",
            viewer_base_path="/docs/ocp/4.20/ko/nodes/index.html",
            source_language="ko",
            display_language="ko",
            translation_status="approved_ko",
            pack_id="openshift-4-20-core",
            pack_label="OpenShift 4.20",
            inferred_product="openshift",
            inferred_version="4.20",
            sections=(
                CanonicalSectionAst(
                    section_id="nodes:overview",
                    ordinal=1,
                    heading="노드 구성",
                    level=2,
                    path=("노드", "노드 구성"),
                    anchor="overview",
                    source_url="https://example.com/nodes",
                    viewer_path="/docs/ocp/4.20/ko/nodes/index.html#overview",
                    semantic_role="concept",
                    blocks=(
                        ParagraphBlock("노드는 컨트롤 플레인과 워커로 나뉩니다."),
                        PrerequisiteBlock(("cluster-admin 권한", "oc CLI 설치")),
                        ProcedureBlock(
                            (
                                ProcedureStep(1, "노드 상태를 확인합니다."),
                                ProcedureStep(2, "필요 시 drain을 진행합니다.", ("cordon 상태 확인",)),
                            )
                        ),
                        CodeBlock("oc get nodes"),
                        NoteBlock("운영 중에는 drain 전 workload 영향을 확인합니다.", variant="warning"),
                        TableBlock(("이름", "역할"), (("master-0", "control-plane"), ("worker-0", "worker"))),
                    ),
                ),
            ),
            provenance=AstProvenance(
                source_fingerprint="fingerprint-1",
                parser_name="canonical_html_v1",
                parser_version="1.0",
                source_state="published_native",
                content_status="approved_ko",
                translation_stage="approved_ko",
                translation_source_language="ko",
                translation_target_language="ko",
                translation_source_url="https://example.com/nodes",
                translation_source_fingerprint="fingerprint-1",
            ),
        )

    def test_document_to_dict_serializes_typed_blocks(self) -> None:
        payload = self._sample_document().to_dict()

        self.assertEqual("nodes", payload["book_slug"])
        self.assertEqual("approved_ko", payload["translation_status"])
        self.assertEqual("approved_ko", payload["provenance"]["translation_stage"])
        self.assertEqual("concept", payload["sections"][0]["semantic_role"])
        self.assertEqual(
            ["paragraph", "prerequisite", "procedure", "code", "note", "table"],
            payload["sections"][0]["block_kinds"],
        )

    def test_project_corpus_sections_flattens_blocks_with_markers(self) -> None:
        rows = project_corpus_sections(self._sample_document())

        self.assertEqual(1, len(rows))
        self.assertEqual("nodes:overview", rows[0].section_id)
        self.assertIn("사전 요구 사항:", rows[0].text)
        self.assertIn("[CODE]", rows[0].text)
        self.assertIn("[WARNING]", rows[0].text)
        self.assertIn("[TABLE]", rows[0].text)
        self.assertEqual(("paragraph", "prerequisite", "procedure", "code", "note", "table"), rows[0].block_kinds)
        self.assertEqual("approved_ko", rows[0].translation_stage)
        self.assertEqual("ko", rows[0].display_language)

    def test_project_playbook_document_preserves_blocks(self) -> None:
        artifact = project_playbook_document(self._sample_document())

        self.assertIsInstance(artifact, PlaybookDocumentArtifact)
        self.assertEqual("nodes", artifact.book_slug)
        self.assertEqual("OpenShift 4.20", "OpenShift 4.20")
        self.assertEqual(6, len(artifact.sections[0].blocks))
        self.assertEqual("approved_ko", artifact.translation_status)
        self.assertEqual("https://example.com/nodes", artifact.translation_source_uri)

    def test_validate_document_ast_reports_duplicate_section_ids(self) -> None:
        document = self._sample_document()
        document.sections = (
            document.sections[0],
            CanonicalSectionAst(
                section_id="nodes:overview",
                ordinal=2,
                heading="중복",
                level=2,
                path=("노드", "중복"),
                anchor="dup",
                source_url="https://example.com/nodes",
                viewer_path="/docs/ocp/4.20/ko/nodes/index.html#dup",
                semantic_role="reference",
                blocks=(ParagraphBlock("중복 section"),),
            ),
        )
        issues = validate_document_ast(document)

        self.assertTrue(any(issue.code == "duplicate_section_id" for issue in issues))

    def test_translate_document_ast_rebuilds_korean_leaf_texts_without_touching_code(self) -> None:
        document = CanonicalDocumentAst(
            doc_id="nodes-en",
            book_slug="nodes",
            title="Nodes",
            source_type="web",
            source_url="https://example.com/nodes",
            viewer_base_path="/docs/ocp/4.20/ko/nodes/index.html",
            source_language="en",
            display_language="ko",
            translation_status="original",
            pack_id="openshift-4-20-core",
            pack_label="OpenShift 4.20",
            inferred_product="openshift",
            inferred_version="4.20",
            sections=(
                CanonicalSectionAst(
                    section_id="nodes:overview",
                    ordinal=1,
                    heading="Overview",
                    level=2,
                    path=("Nodes", "Overview"),
                    anchor="overview",
                    source_url="https://example.com/nodes",
                    viewer_path="/docs/ocp/4.20/ko/nodes/index.html#overview",
                    semantic_role="concept",
                    blocks=(
                        ParagraphBlock("The node manages workloads."),
                        CodeBlock("oc get nodes", caption="Example command"),
                        TableBlock(("Name", "Role"), (("master-0", "control-plane"),)),
                    ),
                ),
            ),
            provenance=AstProvenance(
                source_fingerprint="fp-en-1",
                parser_name="canonical_html_v1",
                parser_version="1.0",
                source_state="fallback_to_en",
                content_status="translated_ko_draft",
                translation_stage="en_only",
                translation_source_language="en",
                translation_target_language="ko",
                translation_source_url="https://example.com/nodes",
                translation_source_fingerprint="fp-en-1",
            ),
        )

        translations = {
            "doc.title": "노드",
            "s0.heading": "개요",
            "s0.path.0": "노드",
            "s0.path.1": "개요",
            "s0.b0.paragraph": "노드는 워크로드를 관리합니다.",
            "s0.b1.code.caption": "예시 명령",
            "s0.b2.table.header.0": "이름",
            "s0.b2.table.header.1": "역할",
            "s0.b2.table.cell.0.1": "컨트롤 플레인",
        }

        class FakeLLMClient:
            def __init__(self, settings) -> None:
                self.settings = settings

            def generate(self, messages):
                payload = json.loads(messages[1]["content"])
                if "items" in payload:
                    return json.dumps(
                        {
                            "items": [
                                {
                                    "id": item["id"],
                                    "text": translations.get(item["id"], item["text"]),
                                }
                                for item in payload["items"]
                            ]
                        },
                        ensure_ascii=False,
                    )
                return json.dumps(payload, ensure_ascii=False)

        with patch("play_book_studio.canonical.translate.LLMClient", FakeLLMClient):
            translated = translate_document_ast(document, settings=object())

        self.assertEqual("노드", translated.title)
        self.assertEqual("개요", translated.sections[0].heading)
        self.assertEqual("노드는 워크로드를 관리합니다.", translated.sections[0].blocks[0].text)
        self.assertEqual("예시 명령", translated.sections[0].blocks[1].caption)
        self.assertEqual("oc get nodes", translated.sections[0].blocks[1].code)
        self.assertEqual(("이름", "역할"), translated.sections[0].blocks[2].headers)
        self.assertEqual(("master-0", "컨트롤 플레인"), translated.sections[0].blocks[2].rows[0])
        self.assertEqual("translated_ko_draft", translated.translation_status)
        self.assertEqual("en", translated.provenance.translation_source_language)


if __name__ == "__main__":
    unittest.main()
