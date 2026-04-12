from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import Settings
from play_book_studio.ingestion.manifest import read_manifest, write_manifest
from play_book_studio.ingestion.models import SourceManifestEntry
from play_book_studio.ingestion.translation_gold_promotion import (
    TRANSLATED_GOLD_PROMOTION_STRATEGY,
    promote_translation_gold,
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _draft_fixture_rows(*, missing_license: bool = False) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    legal_notice_url = "https://example.com/legal"
    license_or_terms = "" if missing_license else "Apache-2.0"
    updated_at = "2026-04-10T12:27:56Z"
    normalized_rows = [
        {
            "book_slug": "monitoring",
            "book_title": "모니터링",
            "heading": "개요",
            "section_level": 1,
            "section_path": ["개요"],
            "anchor": "overview",
            "anchor_id": "overview",
            "source_url": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/monitoring/index",
            "viewer_path": "/docs/ocp/4.20/ko/monitoring/index.html#overview",
            "text": "모니터링 개요입니다.",
            "section_id": "monitoring-overview",
            "semantic_role": "overview",
            "block_kinds": ["paragraph"],
            "source_language": "en",
            "display_language": "ko",
            "translation_status": "translated_ko_draft",
            "translation_stage": "translated_ko_draft",
            "translation_source_language": "en",
            "translation_source_url": "https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html-single/monitoring/index",
            "translation_source_fingerprint": "fp-monitoring",
            "source_id": "openshift_container_platform:4.20:ko:monitoring",
            "source_lane": "official_en_fallback",
            "source_type": "official_doc",
            "source_collection": "core",
            "product": "openshift",
            "version": "4.20",
            "locale": "ko",
            "original_title": "Monitoring",
            "legal_notice_url": legal_notice_url,
            "license_or_terms": license_or_terms,
            "review_status": "unreviewed",
            "trust_score": 1.0,
            "verifiability": "anchor_backed",
            "updated_at": updated_at,
            "cli_commands": [],
            "error_strings": [],
            "k8s_objects": [],
            "operator_names": [],
            "verification_hints": [],
        }
    ]
    chunk_rows = [
        {
            "chunk_id": "monitoring::overview::0",
            "book_slug": "monitoring",
            "book_title": "모니터링",
            "chapter": "모니터링",
            "section": "개요",
            "anchor": "overview",
            "anchor_id": "overview",
            "source_url": normalized_rows[0]["source_url"],
            "viewer_path": normalized_rows[0]["viewer_path"],
            "text": "모니터링 개요입니다.",
            "token_count": 8,
            "ordinal": 0,
            "section_path": ["개요"],
            "chunk_type": "concept",
            "source_id": normalized_rows[0]["source_id"],
            "source_lane": normalized_rows[0]["source_lane"],
            "source_type": normalized_rows[0]["source_type"],
            "source_collection": normalized_rows[0]["source_collection"],
            "product": normalized_rows[0]["product"],
            "version": normalized_rows[0]["version"],
            "locale": normalized_rows[0]["locale"],
            "source_language": normalized_rows[0]["source_language"],
            "display_language": normalized_rows[0]["display_language"],
            "translation_status": "translated_ko_draft",
            "translation_stage": "translated_ko_draft",
            "translation_source_language": normalized_rows[0]["translation_source_language"],
            "translation_source_url": normalized_rows[0]["translation_source_url"],
            "translation_source_fingerprint": normalized_rows[0]["translation_source_fingerprint"],
            "original_title": normalized_rows[0]["original_title"],
            "legal_notice_url": legal_notice_url,
            "license_or_terms": license_or_terms,
            "review_status": "unreviewed",
            "trust_score": 1.0,
            "verifiability": "anchor_backed",
            "updated_at": updated_at,
            "cli_commands": [],
            "error_strings": [],
            "k8s_objects": [],
            "operator_names": [],
            "verification_hints": [],
        }
    ]
    playbook_payload = {
        "book_slug": "monitoring",
        "title": "모니터링",
        "source_uri": normalized_rows[0]["source_url"],
        "source_language": "en",
        "language_hint": "ko",
        "translation_status": "translated_ko_draft",
        "translation_stage": "translated_ko_draft",
        "translation_source_uri": normalized_rows[0]["translation_source_url"],
        "translation_source_language": "en",
        "translation_source_fingerprint": "fp-monitoring",
        "pack_id": "openshift-4-20-core",
        "inferred_version": "4.20",
        "legal_notice_url": legal_notice_url,
        "review_status": "unreviewed",
        "section_count": 1,
        "sections": [
            {
                "section_id": "s1",
                "ordinal": 0,
                "heading": "개요",
                "level": 1,
                "path": ["모니터링"],
                "anchor": "overview",
                "viewer_path": "/docs/ocp/4.20/ko/monitoring/index.html#overview",
                "semantic_role": "overview",
                "blocks": [
                    {
                        "kind": "paragraph",
                        "text": "모니터링 개요입니다.",
                    }
                ],
            }
        ],
        "quality_status": "review_required",
        "quality_score": 0.82,
        "quality_flags": ["machine_translated_draft", "translated_ko_draft"],
        "source_metadata": {
            "source_id": "openshift_container_platform:4.20:ko:monitoring",
            "source_type": "official_doc",
            "source_lane": "official_en_fallback",
            "source_collection": "core",
            "product": "openshift",
            "version": "4.20",
            "trust_score": 1.0,
            "original_url": normalized_rows[0]["source_url"],
            "original_title": "Monitoring",
            "legal_notice_url": legal_notice_url,
            "license_or_terms": license_or_terms,
            "review_status": "unreviewed",
            "verifiability": "anchor_backed",
            "updated_at": updated_at,
            "translation_source_language": "en",
        },
        "anchor_map": {
            "overview": "/docs/ocp/4.20/ko/monitoring/index.html#overview",
        },
    }
    return normalized_rows, chunk_rows, playbook_payload


class TranslationGoldPromotionTests(unittest.TestCase):
    def test_promote_translation_gold_upserts_runtime_outputs_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            entry = SourceManifestEntry(
                book_slug="monitoring",
                title="Monitoring",
                source_url="https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/monitoring/index",
                resolved_source_url="https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/monitoring/index",
                viewer_path="/docs/ocp/4.20/ko/monitoring/index.html",
                high_value=True,
                content_status="translated_ko_draft",
                approval_status="needs_review",
                translation_source_language="en",
                translation_source_url="https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html-single/monitoring/index",
            )
            write_manifest(settings.translation_draft_manifest_path, [entry])
            normalized_rows, chunk_rows, playbook_payload = _draft_fixture_rows()
            _write_jsonl(settings.silver_ko_dir / "translation_drafts" / "normalized_docs.jsonl", normalized_rows)
            _write_jsonl(settings.silver_ko_dir / "translation_drafts" / "chunks.jsonl", chunk_rows)
            _write_jsonl(settings.silver_ko_dir / "translation_drafts" / "playbook_documents.jsonl", [playbook_payload])
            _write_json(
                settings.silver_ko_dir / "translation_drafts" / "playbooks" / "monitoring.json",
                playbook_payload,
            )
            _write_json(
                settings.bronze_dir / "source_bundles" / "monitoring" / "dossier.json",
                {"current_status": {"content_status": "translated_ko_draft", "gap_lane": "translation_first"}},
            )

            report = promote_translation_gold(
                settings,
                refresh_synthesis_report=False,
                sync_qdrant=False,
            )

            self.assertEqual(1, report["summary"]["promoted_count"])
            self.assertEqual(0, report["summary"]["error_count"])

            promoted_entry = read_manifest(settings.source_manifest_path)[0]
            self.assertEqual("approved_ko", promoted_entry.content_status)
            self.assertEqual("approved", promoted_entry.approval_status)
            self.assertEqual("manual_synthesis", promoted_entry.source_type)
            self.assertEqual("applied_playbook", promoted_entry.source_lane)

            playbook_row = json.loads(settings.playbook_documents_path.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual("approved_ko", playbook_row["translation_status"])
            self.assertEqual("approved", playbook_row["review_status"])
            self.assertEqual("ready", playbook_row["quality_status"])
            self.assertEqual("manual_synthesis", playbook_row["source_metadata"]["source_type"])

            dossier = json.loads(
                (settings.bronze_dir / "source_bundles" / "monitoring" / "dossier.json").read_text(encoding="utf-8")
            )
            self.assertEqual("approved_ko", dossier["current_status"]["content_status"])
            self.assertEqual(
                TRANSLATED_GOLD_PROMOTION_STRATEGY,
                dossier["current_status"]["promotion_strategy"],
            )

    def test_promote_translation_gold_rejects_missing_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            entry = SourceManifestEntry(
                book_slug="monitoring",
                title="Monitoring",
                source_url="https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/monitoring/index",
                resolved_source_url="https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/monitoring/index",
                viewer_path="/docs/ocp/4.20/ko/monitoring/index.html",
                high_value=True,
                content_status="translated_ko_draft",
                approval_status="needs_review",
                translation_source_language="en",
                translation_source_url="https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html-single/monitoring/index",
            )
            write_manifest(settings.translation_draft_manifest_path, [entry])
            normalized_rows, chunk_rows, playbook_payload = _draft_fixture_rows(missing_license=True)
            _write_jsonl(settings.silver_ko_dir / "translation_drafts" / "normalized_docs.jsonl", normalized_rows)
            _write_jsonl(settings.silver_ko_dir / "translation_drafts" / "chunks.jsonl", chunk_rows)
            _write_jsonl(settings.silver_ko_dir / "translation_drafts" / "playbook_documents.jsonl", [playbook_payload])
            _write_json(
                settings.silver_ko_dir / "translation_drafts" / "playbooks" / "monitoring.json",
                playbook_payload,
            )

            report = promote_translation_gold(
                settings,
                refresh_synthesis_report=False,
                sync_qdrant=False,
            )

            self.assertEqual(0, report["summary"]["promoted_count"])
            self.assertEqual(1, report["summary"]["error_count"])
            self.assertIn("draft_metadata_incomplete", report["errors"][0]["error"])
            self.assertFalse(settings.source_manifest_path.exists())


if __name__ == "__main__":
    unittest.main()
