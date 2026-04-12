from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.ingestion.models import (  # noqa: E402
    ChunkRecord,
    NormalizedSection,
    ParsedArtifactRecord,
    SourceManifestEntry,
)


class IngestionModelContractTests(unittest.TestCase):
    def test_source_manifest_entry_serializes_security_defaults(self) -> None:
        payload = SourceManifestEntry(book_slug="nodes", title="Nodes").to_dict()

        self.assertEqual("public", payload["tenant_id"])
        self.assertEqual("core", payload["workspace_id"])
        self.assertEqual(["public"], payload["access_groups"])
        self.assertIn("pack_id", payload)
        self.assertIn("approval_state", payload)
        self.assertIn("publication_state", payload)

    def test_normalized_section_contract_payload_includes_lineage_and_boundary(self) -> None:
        section = NormalizedSection(
            book_slug="nodes",
            book_title="Nodes",
            heading="Overview",
            section_level=1,
            section_path=["Nodes"],
            anchor="overview",
            source_url="https://example.com/nodes",
            viewer_path="/docs/nodes",
            text="Node overview",
            section_id="nodes:overview",
            source_id="src-1",
            updated_at="2026-04-11T00:00:00Z",
            license_or_terms="Apache-2.0",
            legal_notice_url="https://example.com/legal",
            original_title="Nodes",
            parsed_artifact_id="parsed:src-1",
        )

        payload = section.to_contract_dict()

        self.assertEqual("parsed:src-1", payload["parsed_artifact_id"])
        self.assertEqual("public", payload["tenant_id"])
        self.assertEqual("core", payload["workspace_id"])
        self.assertEqual("public", payload["classification"])
        self.assertIn("citation_eligible", payload)

    def test_chunk_record_serializes_boundary_fields(self) -> None:
        chunk = ChunkRecord(
            chunk_id="chunk-1",
            book_slug="nodes",
            book_title="Nodes",
            chapter="Nodes",
            section="Overview",
            anchor="overview",
            source_url="https://example.com/nodes",
            viewer_path="/docs/nodes",
            text="Node overview",
            token_count=12,
            ordinal=0,
            source_id="src-1",
            version="4.20",
            locale="ko",
            parsed_artifact_id="parsed:src-1",
            citation_eligible=True,
            license_or_terms="Apache-2.0",
            legal_notice_url="https://example.com/legal",
            original_title="Nodes",
            updated_at="2026-04-11T00:00:00Z",
        )

        payload = chunk.to_dict()

        self.assertEqual("parsed:src-1", payload["parsed_artifact_id"])
        self.assertEqual(["public"], payload["access_groups"])
        self.assertEqual("public", payload["classification"])
        self.assertTrue(payload["citation_eligible"])

    def test_parsed_artifact_record_normalizes_nested_contracts(self) -> None:
        artifact = ParsedArtifactRecord(
            parsed_artifact_id="parsed:src-1",
            source_ref={"source_id": "src-1"},
            raw_asset_ref={"raw_asset_uri": "https://example.com/nodes"},
            page_refs=({"page_id": "page-1", "page_no": 1},),
            quality_state={"updated_at": "2026-04-11T00:00:00Z"},
            security_envelope={},
            promotion_trace={"updated_at": "2026-04-11T00:00:00Z"},
        )

        payload = artifact.to_dict()

        self.assertEqual("official_doc", payload["source_ref"]["source_type"])
        self.assertEqual("core", payload["security_envelope"]["workspace_id"])
        self.assertEqual("accepted", payload["promotion_trace"]["decision"])


if __name__ == "__main__":
    unittest.main()
