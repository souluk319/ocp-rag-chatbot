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

    def test_build_validation_report_uses_runtime_baseline_for_derived_playbooks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = Settings(root_dir=root)
            settings.raw_html_dir.mkdir(parents=True, exist_ok=True)
            (settings.raw_html_dir / "backup_and_restore.html").write_text("<html></html>", encoding="utf-8")

            entry = SourceManifestEntry(
                **{
                    **_base_entry().to_dict(),
                    "book_slug": "backup_and_restore",
                    "title": "백업 및 복구",
                    "source_url": "https://example.com/backup_and_restore",
                    "resolved_source_url": "https://example.com/backup_and_restore",
                    "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html",
                    "source_id": "ocp-4.20-ko-backup-and-restore",
                    "original_title": "Backup and restore",
                }
            )
            write_manifest(settings.source_manifest_path, [entry])

            normalized_row = {
                **_base_section().to_contract_dict(),
                "book_slug": "backup_and_restore",
                "book_title": "백업 및 복구",
                "source_url": "https://example.com/backup_and_restore",
                "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html#overview",
                "section_id": "backup_and_restore:overview",
                "source_id": "ocp-4.20-ko-backup-and-restore",
                "original_title": "Backup and restore",
            }
            chunk_row = {
                **_base_chunk().to_dict(),
                "chunk_id": "backup-and-restore:chunk-1",
                "book_slug": "backup_and_restore",
                "book_title": "백업 및 복구",
                "chapter": "백업 및 복구",
                "source_url": "https://example.com/backup_and_restore",
                "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html#overview",
                "source_id": "ocp-4.20-ko-backup-and-restore",
                "original_title": "Backup and restore",
            }
            playbook_row = {
                **_base_playbook_row(),
                "book_slug": "backup_and_restore",
                "title": "백업 및 복구",
                "translation_status": "approved_ko",
                "source_uri": "https://example.com/backup_and_restore",
                "source_metadata": {
                    **dict(_base_playbook_row()["source_metadata"]),
                    "source_id": "ocp-4.20-ko-backup-and-restore",
                    "source_type": "official_doc",
                    "original_url": "https://example.com/backup_and_restore",
                    "original_title": "Backup and restore",
                },
                "sections": [
                    {
                        "section_id": "backup_and_restore:overview",
                        "section_key": "backup_and_restore:overview",
                        "ordinal": 1,
                        "heading": "개요",
                        "anchor": "overview",
                        "semantic_role": "overview",
                        "path": ["개요"],
                        "section_path": ["개요"],
                        "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html#overview",
                        "blocks": [{"kind": "paragraph", "text": "백업과 복구 절차 개요"}],
                    },
                    {
                        "section_id": "backup_and_restore:procedure",
                        "section_key": "backup_and_restore:procedure",
                        "ordinal": 2,
                        "heading": "백업 절차",
                        "anchor": "backup-procedure",
                        "semantic_role": "procedure",
                        "path": ["운영", "백업 절차"],
                        "section_path": ["운영", "백업 절차"],
                        "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html#backup-procedure",
                        "blocks": [{"kind": "code", "code": "cluster-backup.sh /backup"}],
                    },
                ],
            }

            _write_jsonl(settings.normalized_docs_path, [normalized_row])
            _write_jsonl(settings.chunks_path, [chunk_row])
            _write_jsonl(settings.bm25_corpus_path, [dict(chunk_row)])
            _write_jsonl(settings.playbook_documents_path, [playbook_row])

            with (
                patch("play_book_studio.ingestion.validation.qdrant_count", return_value=None),
                patch("play_book_studio.ingestion.validation.qdrant_id_inventory", return_value=(None, None)),
            ):
                runtime_report = build_validation_report(
                    settings,
                    expected_process_subset="high-value",
                    include_qdrant_id_check=False,
                )
                source_subset_report = build_validation_report(
                    settings,
                    expected_process_subset="high-value",
                    artifact_expectation_mode="source_subset",
                    include_qdrant_id_check=False,
                )

        self.assertEqual("runtime_baseline", runtime_report["artifact_expectation_mode"])
        self.assertEqual(1, runtime_report["expected_source_book_count"])
        self.assertEqual(5, runtime_report["expected_derived_book_count"])
        self.assertEqual(6, runtime_report["expected_book_count"])
        self.assertFalse(runtime_report["checks"]["artifact_books_match_expected_subset"])
        self.assertEqual("source_subset", source_subset_report["artifact_expectation_mode"])
        self.assertTrue(source_subset_report["checks"]["artifact_books_match_expected_subset"])


if __name__ == "__main__":
    unittest.main()
