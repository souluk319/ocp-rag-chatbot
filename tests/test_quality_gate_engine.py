from __future__ import annotations

import sys
import unittest
from pathlib import Path

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
    PrerequisiteBlock,
    ProcedureBlock,
    ProcedureStep,
    TableBlock,
)
from play_book_studio.ingestion.quality_gate import evaluate_document_quality


class QualityGateEngineTests(unittest.TestCase):
    def _base_document(self) -> CanonicalDocumentAst:
        return CanonicalDocumentAst(
            doc_id="ocp-4-20-backup",
            book_slug="backup_and_restore",
            title="백업 및 복구",
            source_type="repo",
            source_url="https://example.com/backup",
            viewer_base_path="/docs/ocp/4.20/ko/backup_and_restore/index.html",
            source_language="ko",
            display_language="ko",
            translation_status="approved_ko",
            pack_id="openshift-4.20-core",
            pack_label="OpenShift 4.20",
            inferred_product="openshift",
            inferred_version="4.20",
            sections=(
                CanonicalSectionAst(
                    section_id="backup:overview",
                    ordinal=1,
                    heading="개요",
                    level=1,
                    path=("백업 및 복구", "개요"),
                    anchor="overview",
                    source_url="https://example.com/backup",
                    viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html#overview",
                    semantic_role="concept",
                    blocks=(
                        ParagraphBlock("컨트롤 플레인과 etcd 백업 전략을 설명합니다."),
                        NoteBlock("운영 중에는 정기 점검이 필요합니다.", variant="note"),
                    ),
                ),
                CanonicalSectionAst(
                    section_id="backup:procedure",
                    ordinal=2,
                    heading="절차",
                    level=1,
                    path=("백업 및 복구", "절차"),
                    anchor="procedure",
                    source_url="https://example.com/backup",
                    viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html#procedure",
                    semantic_role="procedure",
                    blocks=(
                        PrerequisiteBlock(("cluster-admin 권한", "SSH 접근")),
                        ProcedureBlock(
                            (
                                ProcedureStep(1, "etcd 스냅샷을 생성합니다."),
                                ProcedureStep(2, "백업 파일을 외부 저장소로 복사합니다."),
                            )
                        ),
                        CodeBlock("cluster-backup.sh /backup"),
                        TableBlock(("항목", "설명"), (("백업 경로", "/backup"),)),
                    ),
                ),
            ),
            provenance=AstProvenance(
                source_id="ocp-4.20-ko-backup",
                source_lane="vendor_official_source",
                source_type="official_doc",
                source_collection="core",
                source_fingerprint="fp-backup",
                parsed_artifact_id="parsed:backup",
                review_status="approved",
                translation_stage="approved_ko",
                tenant_id="public",
                workspace_id="core",
                pack_id="openshift-4.20-core",
                access_groups=("public",),
                provider_egress_policy="local_only",
                approval_state="approved",
                publication_state="published",
                citation_eligible=True,
            ),
        )

    def test_gold_document_can_be_promoted_when_chat_metrics_are_strong(self) -> None:
        result = evaluate_document_quality(
            self._base_document(),
            chat_metrics={
                "citation_accuracy": 0.96,
                "faithfulness": 0.94,
                "answer_relevance": 0.92,
                "context_precision": 0.88,
                "context_recall": 0.87,
            },
        )

        self.assertEqual("gold", result.quality_verdict)
        self.assertEqual("promoted", result.final_verdict)
        self.assertTrue(result.promotion_ready)
        self.assertEqual((), result.fail_gates)
        self.assertGreaterEqual(result.total_score, 90.0)

    def test_missing_landing_and_citation_marks_blocked_artifact(self) -> None:
        document = self._base_document()
        document.sections = tuple(
            CanonicalSectionAst(
                section_id=section.section_id,
                ordinal=section.ordinal,
                heading=section.heading,
                level=section.level,
                path=section.path,
                anchor="",
                source_url=section.source_url,
                viewer_path="",
                semantic_role=section.semantic_role,
                blocks=section.blocks,
            )
            for section in document.sections
        )
        document.provenance.citation_eligible = False

        result = evaluate_document_quality(document)

        self.assertEqual("blocked_artifact", result.quality_verdict)
        self.assertIn("chat", result.fail_gates)
        issue_codes = {issue.code for issue in result.issues}
        self.assertIn("citation_landing_unavailable", issue_codes)

    def test_official_english_without_translation_completion_is_blocked(self) -> None:
        document = self._base_document()
        document.source_language = "en"
        document.display_language = "ko"
        document.translation_status = "original"
        document.provenance.translation_stage = "en_only"

        result = evaluate_document_quality(document)

        self.assertEqual("blocked_artifact", result.quality_verdict)
        self.assertIn("fidelity", result.fail_gates)
        self.assertIn("translation_incomplete", {issue.code for issue in result.issues})

    def test_missing_boundary_identity_triggers_governance_fail_gate(self) -> None:
        document = self._base_document()
        document.provenance.source_lane = ""
        document.provenance.tenant_id = ""
        document.provenance.workspace_id = ""
        document.provenance.pack_id = ""
        document.provenance.access_groups = ()

        result = evaluate_document_quality(document)

        self.assertEqual("blocked_artifact", result.quality_verdict)
        self.assertIn("governance", result.fail_gates)
        issue_codes = {issue.code for issue in result.issues}
        self.assertIn("missing_source_lane", issue_codes)
        self.assertIn("missing_boundary_identity", issue_codes)
        self.assertIn("missing_access_groups", issue_codes)


if __name__ == "__main__":
    unittest.main()
