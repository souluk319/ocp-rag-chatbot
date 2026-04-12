from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import Settings
from play_book_studio.config.validation import build_validation_report
from play_book_studio.ingestion.manifest import write_manifest
from play_book_studio.ingestion.models import ChunkRecord, NormalizedSection, SourceManifestEntry


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _base_entry() -> SourceManifestEntry:
    return SourceManifestEntry(
        book_slug="nodes",
        title="노드",
        source_url="https://example.com/nodes",
        resolved_source_url="https://example.com/nodes",
        viewer_path="/docs/ocp/4.20/ko/nodes/index.html",
        source_state="published_native",
        source_state_reason="ok",
        high_value=True,
        source_fingerprint="fp-nodes",
        source_id="ocp-4.20-ko-nodes",
        source_lane="official_ko",
        source_type="official_doc",
        source_collection="core",
        original_title="Nodes",
        legal_notice_url="https://example.com/legal",
        license_or_terms="Apache-2.0",
        review_status="approved",
        content_status="approved_ko",
        citation_eligible=True,
        updated_at="2026-04-11T00:00:00Z",
        pack_id="openshift-4.20-core",
        pack_version="4.20",
        bundle_scope="official",
        classification="public",
        access_groups=("public",),
        provider_egress_policy="unspecified",
        approval_state="approved",
        publication_state="published",
    )


def _base_section() -> NormalizedSection:
    return NormalizedSection(
        book_slug="nodes",
        book_title="노드",
        heading="개요",
        section_level=1,
        section_path=["노드"],
        anchor="overview",
        source_url="https://example.com/nodes",
        viewer_path="/docs/ocp/4.20/ko/nodes/index.html#overview",
        text="노드 개요",
        section_id="nodes:overview",
        source_id="ocp-4.20-ko-nodes",
        source_lane="official_ko",
        source_type="official_doc",
        source_collection="core",
        product="openshift",
        version="4.20",
        locale="ko",
        original_title="Nodes",
        legal_notice_url="https://example.com/legal",
        license_or_terms="Apache-2.0",
        review_status="approved",
        trust_score=1.0,
        verifiability="anchor_backed",
        updated_at="2026-04-11T00:00:00Z",
        parsed_artifact_id="parsed:ocp-4.20-ko-nodes",
        tenant_id="public",
        workspace_id="core",
        parent_pack_id="openshift-4.20-core",
        pack_version="4.20",
        bundle_scope="official",
        classification="public",
        access_groups=("public",),
        provider_egress_policy="unspecified",
        approval_state="approved",
        publication_state="published",
        redaction_state="not_required",
    )


def _base_chunk() -> ChunkRecord:
    return ChunkRecord(
        chunk_id="chunk-1",
        book_slug="nodes",
        book_title="노드",
        chapter="노드",
        section="개요",
        anchor="overview",
        source_url="https://example.com/nodes",
        viewer_path="/docs/ocp/4.20/ko/nodes/index.html#overview",
        text="노드 개요",
        token_count=10,
        ordinal=0,
        source_id="ocp-4.20-ko-nodes",
        source_lane="official_ko",
        source_type="official_doc",
        source_collection="core",
        product="openshift",
        version="4.20",
        locale="ko",
        original_title="Nodes",
        legal_notice_url="https://example.com/legal",
        license_or_terms="Apache-2.0",
        review_status="approved",
        trust_score=1.0,
        verifiability="anchor_backed",
        updated_at="2026-04-11T00:00:00Z",
        parsed_artifact_id="parsed:ocp-4.20-ko-nodes",
        tenant_id="public",
        workspace_id="core",
        parent_pack_id="openshift-4.20-core",
        pack_version="4.20",
        bundle_scope="official",
        classification="public",
        access_groups=("public",),
        provider_egress_policy="unspecified",
        approval_state="approved",
        publication_state="published",
        redaction_state="not_required",
        citation_eligible=True,
    )


def _base_playbook_row() -> dict[str, object]:
    return {
        "book_slug": "nodes",
        "title": "노드",
        "version": "4.20",
        "locale": "ko",
        "source_uri": "https://example.com/nodes",
        "legal_notice_url": "https://example.com/legal",
        "review_status": "approved",
        "source_metadata": {
            "source_id": "ocp-4.20-ko-nodes",
            "source_type": "official_doc",
            "source_lane": "official_ko",
            "source_collection": "core",
            "product": "openshift",
            "version": "4.20",
            "trust_score": 1.0,
            "original_url": "https://example.com/nodes",
            "original_title": "Nodes",
            "legal_notice_url": "https://example.com/legal",
            "license_or_terms": "Apache-2.0",
            "review_status": "approved",
            "verifiability": "anchor_backed",
            "updated_at": "2026-04-11T00:00:00Z",
            "parsed_artifact_id": "parsed:ocp-4.20-ko-nodes",
            "tenant_id": "public",
            "workspace_id": "core",
            "pack_id": "openshift-4.20-core",
            "pack_version": "4.20",
            "bundle_scope": "official",
            "classification": "public",
            "access_groups": ["public"],
            "provider_egress_policy": "unspecified",
            "approval_state": "approved",
            "publication_state": "published",
            "redaction_state": "not_required",
        },
    }


class ValidationGateTests(unittest.TestCase):
    def _build_report(self, root: Path, *, corrupt: bool = False) -> dict[str, object]:
        settings = Settings(root_dir=root)
        settings.raw_html_dir.mkdir(parents=True, exist_ok=True)
        (settings.raw_html_dir / "nodes.html").write_text("<html></html>", encoding="utf-8")

        entry = _base_entry()
        write_manifest(settings.source_manifest_path, [entry])

        if corrupt:
            payload = json.loads(settings.source_manifest_path.read_text(encoding="utf-8"))
            payload["entries"][0]["tenant_id"] = ""
            settings.source_manifest_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        normalized_row = _base_section().to_contract_dict()
        chunk_row = _base_chunk().to_dict()
        bm25_row = dict(chunk_row)
        playbook_row = _base_playbook_row()

        if corrupt:
            normalized_row["parsed_artifact_id"] = ""
            chunk_row["classification"] = ""
            playbook_row["source_metadata"]["provider_egress_policy"] = ""

        _write_jsonl(settings.normalized_docs_path, [normalized_row])
        _write_jsonl(settings.chunks_path, [chunk_row])
        _write_jsonl(settings.bm25_corpus_path, [bm25_row])
        _write_jsonl(settings.playbook_documents_path, [playbook_row])

        with (
            patch("play_book_studio.ingestion.validation.qdrant_count", return_value=None),
            patch("play_book_studio.ingestion.validation.qdrant_id_inventory", return_value=(None, None)),
        ):
            return build_validation_report(
                settings,
                expected_process_subset="high-value",
                include_qdrant_id_check=False,
            )

    def test_build_validation_report_marks_parsed_and_security_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report = self._build_report(Path(tmpdir), corrupt=False)

        self.assertTrue(report["checks"]["parsed_lineage_complete"])
        self.assertTrue(report["checks"]["security_boundary_complete"])
        self.assertEqual(0, report["parsed_lineage_missing_rows"])
        self.assertEqual(0, report["security_boundary_missing_rows"])

    def test_build_validation_report_flags_missing_parsed_and_security_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report = self._build_report(Path(tmpdir), corrupt=True)

        self.assertFalse(report["checks"]["parsed_lineage_complete"])
        self.assertFalse(report["checks"]["security_boundary_complete"])
        self.assertGreater(report["parsed_lineage_missing_rows"], 0)
        self.assertGreater(report["security_boundary_missing_rows"], 0)
        self.assertIn("parsed_artifact_id", report["metadata_missing_by_field"]["normalized_parsed"])
        self.assertIn("tenant_id", report["metadata_missing_by_field"]["manifest_security"])


if __name__ == "__main__":
    unittest.main()
