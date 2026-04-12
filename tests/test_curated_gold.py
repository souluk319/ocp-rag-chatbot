from __future__ import annotations

import json
import re
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
from play_book_studio.config.validation import read_jsonl
from play_book_studio.ingestion import chunking
from play_book_studio.ingestion.curated_gold import (
    apply_curated_backup_restore_gold,
    apply_curated_etcd_gold,
    apply_curated_installing_on_any_platform_gold,
    apply_curated_machine_configuration_gold,
    apply_curated_monitoring_gold,
    apply_curated_operators_gold,
)
from play_book_studio.ingestion.manifest import read_manifest, write_manifest
from play_book_studio.ingestion.models import SourceManifestEntry


class _FakeTokenizer:
    def __init__(self) -> None:
        self.model_max_length = 64

    def __call__(self, text: str, **_: object) -> dict[str, list[int]]:
        return {"input_ids": [ord(char) for char in text]}

    def decode(self, token_ids: list[int]) -> str:
        return "".join(chr(token_id) for token_id in token_ids)


class _FakeSentenceModel:
    def __init__(self) -> None:
        self.tokenizer = _FakeTokenizer()


class _SchemaValidator:
    def __init__(self, root_schema: dict[str, object]) -> None:
        self.root_schema = root_schema

    def validate(self, payload: object, schema: dict[str, object] | None = None, path: str = "$") -> None:
        schema = self.root_schema if schema is None else schema
        if "$ref" in schema:
            ref = str(schema["$ref"])
            target = ref.split("/")[-1]
            self.validate(payload, self.root_schema["$defs"][target], path)
            return
        if "anyOf" in schema:
            errors: list[str] = []
            for candidate in schema["anyOf"]:
                try:
                    self.validate(payload, candidate, path)
                    return
                except AssertionError as exc:
                    errors.append(str(exc))
            raise AssertionError(errors[0] if errors else f"{path}: anyOf failed")

        expected_type = schema.get("type")
        if expected_type == "object":
            if not isinstance(payload, dict):
                raise AssertionError(f"{path}: expected object")
            properties = schema.get("properties", {})
            for key in schema.get("required", []):
                if key not in payload:
                    raise AssertionError(f"{path}: missing '{key}'")
            if schema.get("additionalProperties") is False:
                extras = sorted(set(payload) - set(properties))
                if extras:
                    raise AssertionError(f"{path}: unexpected {extras}")
            for key, value in payload.items():
                child = properties.get(key)
                additional = schema.get("additionalProperties")
                if child is None and isinstance(additional, dict):
                    child = additional
                if child is not None:
                    self.validate(value, child, f"{path}.{key}")
            return

        if expected_type == "array":
            if not isinstance(payload, (list, tuple)):
                raise AssertionError(f"{path}: expected array")
            items = schema.get("items")
            if isinstance(items, dict):
                for index, item in enumerate(payload):
                    self.validate(item, items, f"{path}[{index}]")
            return

        if expected_type == "string":
            if not isinstance(payload, str):
                raise AssertionError(f"{path}: expected string")
            min_length = schema.get("minLength")
            if min_length is not None and len(payload) < int(min_length):
                raise AssertionError(f"{path}: shorter than minLength")
            pattern = schema.get("pattern")
            if pattern and re.match(str(pattern), payload) is None:
                raise AssertionError(f"{path}: pattern mismatch")
        elif expected_type == "integer":
            if not isinstance(payload, int) or isinstance(payload, bool):
                raise AssertionError(f"{path}: expected integer")
        elif expected_type == "number":
            if not isinstance(payload, (int, float)) or isinstance(payload, bool):
                raise AssertionError(f"{path}: expected number")

        if "enum" in schema and payload not in schema["enum"]:
            raise AssertionError(f"{path}: enum mismatch")
        if "minimum" in schema and payload < schema["minimum"]:
            raise AssertionError(f"{path}: below minimum")
        if "maximum" in schema and payload > schema["maximum"]:
            raise AssertionError(f"{path}: above maximum")


class CuratedGoldTests(unittest.TestCase):
    def _schema(self, name: str) -> dict[str, object]:
        return json.loads((ROOT / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8"))

    def _assert_valid(self, name: str, payload: dict[str, object]) -> None:
        validator = _SchemaValidator(self._schema(name))
        validator.validate(payload)

    def _assert_curated_provenance_contract(
        self,
        section: dict[str, object],
        chunk: dict[str, object],
        playbook: dict[str, object],
        *,
        source_id: str,
    ) -> None:
        expected_parsed_artifact_id = f"parsed:{source_id}"
        for row in (section, chunk):
            self.assertEqual(expected_parsed_artifact_id, row["parsed_artifact_id"])
            self.assertEqual("public", row["tenant_id"])
            self.assertEqual("core", row["workspace_id"])
            self.assertEqual("official", row["bundle_scope"])
            self.assertEqual("public", row["classification"])
            self.assertEqual(["public"], row["access_groups"])
            self.assertEqual("unspecified", row["provider_egress_policy"])
            self.assertEqual("approved", row["approval_state"])
            self.assertEqual("published", row["publication_state"])
            self.assertEqual("not_required", row["redaction_state"])

        source_metadata = playbook["source_metadata"]
        self.assertEqual(expected_parsed_artifact_id, source_metadata["parsed_artifact_id"])
        self.assertEqual("public", source_metadata["tenant_id"])
        self.assertEqual("core", source_metadata["workspace_id"])
        self.assertEqual("official", source_metadata["bundle_scope"])
        self.assertEqual("public", source_metadata["classification"])
        self.assertEqual(["public"], source_metadata["access_groups"])
        self.assertEqual("unspecified", source_metadata["provider_egress_policy"])
        self.assertEqual("approved", source_metadata["approval_state"])
        self.assertEqual("published", source_metadata["publication_state"])
        self.assertEqual("not_required", source_metadata["redaction_state"])

    def test_apply_curated_etcd_gold_upserts_all_active_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            settings.source_catalog_path.parent.mkdir(parents=True, exist_ok=True)

            existing_manifest = SourceManifestEntry(
                book_slug="architecture",
                title="아키텍처",
                source_url="https://example.com/architecture",
                resolved_source_url="https://example.com/architecture",
                viewer_path="/docs/ocp/4.20/ko/architecture/index.html",
                content_status="approved_ko",
                approval_status="approved",
                citation_eligible=True,
                high_value=True,
            )
            write_manifest(settings.source_manifest_path, [existing_manifest])

            existing_section = {
                "book_slug": "architecture",
                "book_title": "아키텍처",
                "heading": "개요",
                "section_level": 1,
                "section_path": ["개요"],
                "anchor": "overview",
                "anchor_id": "overview",
                "source_url": "https://example.com/architecture",
                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                "text": "arch",
                "section_id": "architecture:overview",
                "semantic_role": "overview",
                "block_kinds": ["paragraph"],
                "source_language": "ko",
                "display_language": "ko",
                "translation_status": "approved_ko",
                "translation_stage": "approved_ko",
                "translation_source_language": "ko",
                "translation_source_url": "https://example.com/architecture",
                "translation_source_fingerprint": "x",
                "source_id": "architecture",
                "source_lane": "official_ko",
                "source_type": "official_doc",
                "source_collection": "core",
                "product": "openshift",
                "version": "4.20",
                "locale": "ko",
                "original_title": "아키텍처",
                "legal_notice_url": "",
                "license_or_terms": "",
                "review_status": "approved",
                "trust_score": 1.0,
                "verifiability": "anchor_backed",
                "updated_at": "",
                "cli_commands": [],
                "error_strings": [],
                "k8s_objects": [],
                "operator_names": [],
                "verification_hints": [],
            }
            for path in settings.normalized_docs_candidates:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(existing_section, ensure_ascii=False) + "\n", encoding="utf-8")

            for path in (settings.chunks_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")
            for path in (settings.bm25_corpus_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")
            for path in (settings.playbook_documents_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")

            with patch.object(chunking, "load_sentence_model", return_value=_FakeSentenceModel()):
                report = apply_curated_etcd_gold(settings, refresh_synthesis_report=False)

            self.assertEqual("etcd", report["book_slug"])
            self.assertGreater(report["section_count"], 0)
            self.assertGreater(report["chunk_count"], 0)
            self.assertEqual(1, report["manifest_before_count"])
            self.assertEqual(2, report["manifest_after_count"])

            normalized_rows = read_jsonl(settings.normalized_docs_path)
            chunk_rows = read_jsonl(settings.chunks_path)
            bm25_rows = read_jsonl(settings.bm25_corpus_path)
            playbook_rows = read_jsonl(settings.playbook_documents_path)
            manifest_rows = read_manifest(settings.source_manifest_path)

            etcd_sections = [row for row in normalized_rows if row["book_slug"] == "etcd"]
            etcd_chunks = [row for row in chunk_rows if row["book_slug"] == "etcd"]
            etcd_bm25 = [row for row in bm25_rows if row["book_slug"] == "etcd"]
            self.assertTrue(etcd_sections)
            self.assertTrue(etcd_chunks)
            self.assertTrue(etcd_bm25)
            self.assertEqual(1, sum(1 for row in playbook_rows if row["book_slug"] == "etcd"))
            self.assertEqual(["architecture", "etcd"], [entry.book_slug for entry in manifest_rows])
            self.assertEqual(
                "manual_synthesis",
                [entry.source_type for entry in manifest_rows if entry.book_slug == "etcd"][0],
            )

            self._assert_valid("document", etcd_sections[0])
            self._assert_valid("chunk", etcd_chunks[0])
            etcd_playbook = next(row for row in playbook_rows if row["book_slug"] == "etcd")
            self._assert_valid("manualbook", etcd_playbook)
            self.assertEqual("ready", etcd_playbook["quality_status"])
            self.assertEqual("approved", etcd_playbook["review_status"])
            self._assert_curated_provenance_contract(
                etcd_sections[0],
                etcd_chunks[0],
                etcd_playbook,
                source_id="openshift_container_platform:4.20:ko:etcd:curated_gold_v1",
            )

    def test_apply_curated_backup_restore_gold_upserts_all_active_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            settings.source_catalog_path.parent.mkdir(parents=True, exist_ok=True)

            existing_manifest = SourceManifestEntry(
                book_slug="architecture",
                title="아키텍처",
                source_url="https://example.com/architecture",
                resolved_source_url="https://example.com/architecture",
                viewer_path="/docs/ocp/4.20/ko/architecture/index.html",
                content_status="approved_ko",
                approval_status="approved",
                citation_eligible=True,
                high_value=True,
            )
            write_manifest(settings.source_manifest_path, [existing_manifest])

            existing_section = {
                "book_slug": "architecture",
                "book_title": "아키텍처",
                "heading": "개요",
                "section_level": 1,
                "section_path": ["개요"],
                "anchor": "overview",
                "anchor_id": "overview",
                "source_url": "https://example.com/architecture",
                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                "text": "arch",
                "section_id": "architecture:overview",
                "semantic_role": "overview",
                "block_kinds": ["paragraph"],
                "source_language": "ko",
                "display_language": "ko",
                "translation_status": "approved_ko",
                "translation_stage": "approved_ko",
                "translation_source_language": "ko",
                "translation_source_url": "https://example.com/architecture",
                "translation_source_fingerprint": "x",
                "source_id": "architecture",
                "source_lane": "official_ko",
                "source_type": "official_doc",
                "source_collection": "core",
                "product": "openshift",
                "version": "4.20",
                "locale": "ko",
                "original_title": "아키텍처",
                "legal_notice_url": "",
                "license_or_terms": "",
                "review_status": "approved",
                "trust_score": 1.0,
                "verifiability": "anchor_backed",
                "updated_at": "",
                "cli_commands": [],
                "error_strings": [],
                "k8s_objects": [],
                "operator_names": [],
                "verification_hints": [],
            }
            for path in settings.normalized_docs_candidates:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(existing_section, ensure_ascii=False) + "\n", encoding="utf-8")

            for path in (settings.chunks_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")
            for path in (settings.bm25_corpus_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")
            for path in (settings.playbook_documents_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")

            with patch.object(chunking, "load_sentence_model", return_value=_FakeSentenceModel()):
                report = apply_curated_backup_restore_gold(settings, refresh_synthesis_report=False)

            self.assertEqual("backup_and_restore", report["book_slug"])
            self.assertGreater(report["section_count"], 0)
            self.assertGreater(report["chunk_count"], 0)
            self.assertEqual(1, report["manifest_before_count"])
            self.assertEqual(2, report["manifest_after_count"])

            normalized_rows = read_jsonl(settings.normalized_docs_path)
            chunk_rows = read_jsonl(settings.chunks_path)
            bm25_rows = read_jsonl(settings.bm25_corpus_path)
            playbook_rows = read_jsonl(settings.playbook_documents_path)
            manifest_rows = read_manifest(settings.source_manifest_path)

            backup_sections = [row for row in normalized_rows if row["book_slug"] == "backup_and_restore"]
            backup_chunks = [row for row in chunk_rows if row["book_slug"] == "backup_and_restore"]
            backup_bm25 = [row for row in bm25_rows if row["book_slug"] == "backup_and_restore"]
            self.assertTrue(backup_sections)
            self.assertTrue(backup_chunks)
            self.assertTrue(backup_bm25)
            self.assertEqual(1, sum(1 for row in playbook_rows if row["book_slug"] == "backup_and_restore"))
            self.assertEqual(["architecture", "backup_and_restore"], [entry.book_slug for entry in manifest_rows])
            self.assertEqual(
                "manual_synthesis",
                [entry.source_type for entry in manifest_rows if entry.book_slug == "backup_and_restore"][0],
            )

            self._assert_valid("document", backup_sections[0])
            self._assert_valid("chunk", backup_chunks[0])
            backup_playbook = next(row for row in playbook_rows if row["book_slug"] == "backup_and_restore")
            self._assert_valid("manualbook", backup_playbook)
            self.assertEqual("ready", backup_playbook["quality_status"])
            self.assertEqual("approved", backup_playbook["review_status"])
            self._assert_curated_provenance_contract(
                backup_sections[0],
                backup_chunks[0],
                backup_playbook,
                source_id="openshift_container_platform:4.20:ko:backup_and_restore:curated_gold_v1",
            )

    def test_apply_curated_machine_configuration_gold_upserts_all_active_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            settings.source_catalog_path.parent.mkdir(parents=True, exist_ok=True)

            existing_manifest = SourceManifestEntry(
                book_slug="architecture",
                title="아키텍처",
                source_url="https://example.com/architecture",
                resolved_source_url="https://example.com/architecture",
                viewer_path="/docs/ocp/4.20/ko/architecture/index.html",
                content_status="approved_ko",
                approval_status="approved",
                citation_eligible=True,
                high_value=True,
            )
            write_manifest(settings.source_manifest_path, [existing_manifest])

            existing_section = {
                "book_slug": "architecture",
                "book_title": "아키텍처",
                "heading": "개요",
                "section_level": 1,
                "section_path": ["개요"],
                "anchor": "overview",
                "anchor_id": "overview",
                "source_url": "https://example.com/architecture",
                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                "text": "arch",
                "section_id": "architecture:overview",
                "semantic_role": "overview",
                "block_kinds": ["paragraph"],
                "source_language": "ko",
                "display_language": "ko",
                "translation_status": "approved_ko",
                "translation_stage": "approved_ko",
                "translation_source_language": "ko",
                "translation_source_url": "https://example.com/architecture",
                "translation_source_fingerprint": "x",
                "source_id": "architecture",
                "source_lane": "official_ko",
                "source_type": "official_doc",
                "source_collection": "core",
                "product": "openshift",
                "version": "4.20",
                "locale": "ko",
                "original_title": "아키텍처",
                "legal_notice_url": "",
                "license_or_terms": "",
                "review_status": "approved",
                "trust_score": 1.0,
                "verifiability": "anchor_backed",
                "updated_at": "",
                "cli_commands": [],
                "error_strings": [],
                "k8s_objects": [],
                "operator_names": [],
                "verification_hints": [],
            }
            for path in settings.normalized_docs_candidates:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(existing_section, ensure_ascii=False) + "\n", encoding="utf-8")

            for path in (settings.chunks_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")
            for path in (settings.bm25_corpus_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")
            for path in (settings.playbook_documents_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")

            with patch.object(chunking, "load_sentence_model", return_value=_FakeSentenceModel()):
                report = apply_curated_machine_configuration_gold(
                    settings,
                    refresh_synthesis_report=False,
                )

            self.assertEqual("machine_configuration", report["book_slug"])
            self.assertGreater(report["section_count"], 0)
            self.assertGreater(report["chunk_count"], 0)
            self.assertEqual(1, report["manifest_before_count"])
            self.assertEqual(2, report["manifest_after_count"])

            normalized_rows = read_jsonl(settings.normalized_docs_path)
            chunk_rows = read_jsonl(settings.chunks_path)
            bm25_rows = read_jsonl(settings.bm25_corpus_path)
            playbook_rows = read_jsonl(settings.playbook_documents_path)
            manifest_rows = read_manifest(settings.source_manifest_path)

            machine_sections = [row for row in normalized_rows if row["book_slug"] == "machine_configuration"]
            machine_chunks = [row for row in chunk_rows if row["book_slug"] == "machine_configuration"]
            machine_bm25 = [row for row in bm25_rows if row["book_slug"] == "machine_configuration"]
            self.assertTrue(machine_sections)
            self.assertTrue(machine_chunks)
            self.assertTrue(machine_bm25)
            self.assertEqual(1, sum(1 for row in playbook_rows if row["book_slug"] == "machine_configuration"))
            self.assertEqual(["architecture", "machine_configuration"], [entry.book_slug for entry in manifest_rows])
            self.assertEqual(
                "manual_synthesis",
                [entry.source_type for entry in manifest_rows if entry.book_slug == "machine_configuration"][0],
            )

            self._assert_valid("document", machine_sections[0])
            self._assert_valid("chunk", machine_chunks[0])
            machine_playbook = next(row for row in playbook_rows if row["book_slug"] == "machine_configuration")
            self._assert_valid("manualbook", machine_playbook)
            self.assertEqual("ready", machine_playbook["quality_status"])
            self.assertEqual("approved", machine_playbook["review_status"])
            self._assert_curated_provenance_contract(
                machine_sections[0],
                machine_chunks[0],
                machine_playbook,
                source_id="openshift_container_platform:4.20:ko:machine_configuration:curated_gold_v1",
            )

    def test_apply_curated_operators_gold_upserts_all_active_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            settings.source_catalog_path.parent.mkdir(parents=True, exist_ok=True)

            existing_manifest = SourceManifestEntry(
                book_slug="architecture",
                title="아키텍처",
                source_url="https://example.com/architecture",
                resolved_source_url="https://example.com/architecture",
                viewer_path="/docs/ocp/4.20/ko/architecture/index.html",
                content_status="approved_ko",
                approval_status="approved",
                citation_eligible=True,
                high_value=True,
            )
            write_manifest(settings.source_manifest_path, [existing_manifest])

            existing_section = {
                "book_slug": "architecture",
                "book_title": "아키텍처",
                "heading": "개요",
                "section_level": 1,
                "section_path": ["개요"],
                "anchor": "overview",
                "anchor_id": "overview",
                "source_url": "https://example.com/architecture",
                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                "text": "arch",
                "section_id": "architecture:overview",
                "semantic_role": "overview",
                "block_kinds": ["paragraph"],
                "source_language": "ko",
                "display_language": "ko",
                "translation_status": "approved_ko",
                "translation_stage": "approved_ko",
                "translation_source_language": "ko",
                "translation_source_url": "https://example.com/architecture",
                "translation_source_fingerprint": "x",
                "source_id": "architecture",
                "source_lane": "official_ko",
                "source_type": "official_doc",
                "source_collection": "core",
                "product": "openshift",
                "version": "4.20",
                "locale": "ko",
                "original_title": "아키텍처",
                "legal_notice_url": "",
                "license_or_terms": "",
                "review_status": "approved",
                "trust_score": 1.0,
                "verifiability": "anchor_backed",
                "updated_at": "",
                "cli_commands": [],
                "error_strings": [],
                "k8s_objects": [],
                "operator_names": [],
                "verification_hints": [],
            }
            for path in settings.normalized_docs_candidates:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(existing_section, ensure_ascii=False) + "\n", encoding="utf-8")

            for path in (settings.chunks_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")
            for path in (settings.bm25_corpus_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")
            for path in (settings.playbook_documents_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")

            with patch.object(chunking, "load_sentence_model", return_value=_FakeSentenceModel()):
                report = apply_curated_operators_gold(
                    settings,
                    refresh_synthesis_report=False,
                )

            self.assertEqual("operators", report["book_slug"])
            self.assertGreater(report["section_count"], 0)
            self.assertGreater(report["chunk_count"], 0)
            self.assertEqual(1, report["manifest_before_count"])
            self.assertEqual(2, report["manifest_after_count"])

            normalized_rows = read_jsonl(settings.normalized_docs_path)
            chunk_rows = read_jsonl(settings.chunks_path)
            bm25_rows = read_jsonl(settings.bm25_corpus_path)
            playbook_rows = read_jsonl(settings.playbook_documents_path)
            manifest_rows = read_manifest(settings.source_manifest_path)

            operator_sections = [row for row in normalized_rows if row["book_slug"] == "operators"]
            operator_chunks = [row for row in chunk_rows if row["book_slug"] == "operators"]
            operator_bm25 = [row for row in bm25_rows if row["book_slug"] == "operators"]
            self.assertTrue(operator_sections)
            self.assertTrue(operator_chunks)
            self.assertTrue(operator_bm25)
            self.assertEqual(1, sum(1 for row in playbook_rows if row["book_slug"] == "operators"))
            self.assertEqual(["architecture", "operators"], [entry.book_slug for entry in manifest_rows])
            self.assertEqual(
                "manual_synthesis",
                [entry.source_type for entry in manifest_rows if entry.book_slug == "operators"][0],
            )

            self._assert_valid("document", operator_sections[0])
            self._assert_valid("chunk", operator_chunks[0])
            operators_playbook = next(row for row in playbook_rows if row["book_slug"] == "operators")
            self._assert_valid("manualbook", operators_playbook)
            self.assertEqual("ready", operators_playbook["quality_status"])
            self.assertEqual("approved", operators_playbook["review_status"])
            self._assert_curated_provenance_contract(
                operator_sections[0],
                operator_chunks[0],
                operators_playbook,
                source_id="openshift_container_platform:4.20:ko:operators:curated_gold_v1",
            )

    def test_apply_curated_monitoring_gold_upserts_all_active_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            settings.source_catalog_path.parent.mkdir(parents=True, exist_ok=True)

            existing_manifest = SourceManifestEntry(
                book_slug="architecture",
                title="아키텍처",
                source_url="https://example.com/architecture",
                resolved_source_url="https://example.com/architecture",
                viewer_path="/docs/ocp/4.20/ko/architecture/index.html",
                content_status="approved_ko",
                approval_status="approved",
                citation_eligible=True,
                high_value=True,
            )
            write_manifest(settings.source_manifest_path, [existing_manifest])

            existing_section = {
                "book_slug": "architecture",
                "book_title": "아키텍처",
                "heading": "개요",
                "section_level": 1,
                "section_path": ["개요"],
                "anchor": "overview",
                "anchor_id": "overview",
                "source_url": "https://example.com/architecture",
                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                "text": "arch",
                "section_id": "architecture:overview",
                "semantic_role": "overview",
                "block_kinds": ["paragraph"],
                "source_language": "ko",
                "display_language": "ko",
                "translation_status": "approved_ko",
                "translation_stage": "approved_ko",
                "translation_source_language": "ko",
                "translation_source_url": "https://example.com/architecture",
                "translation_source_fingerprint": "x",
                "source_id": "architecture",
                "source_lane": "official_ko",
                "source_type": "official_doc",
                "source_collection": "core",
                "product": "openshift",
                "version": "4.20",
                "locale": "ko",
                "original_title": "아키텍처",
                "legal_notice_url": "",
                "license_or_terms": "",
                "review_status": "approved",
                "trust_score": 1.0,
                "verifiability": "anchor_backed",
                "updated_at": "",
                "cli_commands": [],
                "error_strings": [],
                "k8s_objects": [],
                "operator_names": [],
                "verification_hints": [],
            }
            for path in settings.normalized_docs_candidates:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(existing_section, ensure_ascii=False) + "\n", encoding="utf-8")

            for path in (settings.chunks_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")
            for path in (settings.bm25_corpus_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")
            for path in (settings.playbook_documents_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")

            with patch.object(chunking, "load_sentence_model", return_value=_FakeSentenceModel()):
                report = apply_curated_monitoring_gold(
                    settings,
                    refresh_synthesis_report=False,
                )

            self.assertEqual("monitoring", report["book_slug"])
            self.assertGreater(report["section_count"], 0)
            self.assertGreater(report["chunk_count"], 0)
            self.assertEqual(1, report["manifest_before_count"])
            self.assertEqual(2, report["manifest_after_count"])

            normalized_rows = read_jsonl(settings.normalized_docs_path)
            chunk_rows = read_jsonl(settings.chunks_path)
            bm25_rows = read_jsonl(settings.bm25_corpus_path)
            playbook_rows = read_jsonl(settings.playbook_documents_path)
            manifest_rows = read_manifest(settings.source_manifest_path)

            monitoring_sections = [row for row in normalized_rows if row["book_slug"] == "monitoring"]
            monitoring_chunks = [row for row in chunk_rows if row["book_slug"] == "monitoring"]
            monitoring_bm25 = [row for row in bm25_rows if row["book_slug"] == "monitoring"]
            self.assertTrue(monitoring_sections)
            self.assertTrue(monitoring_chunks)
            self.assertTrue(monitoring_bm25)
            self.assertEqual(1, sum(1 for row in playbook_rows if row["book_slug"] == "monitoring"))
            self.assertEqual(["architecture", "monitoring"], [entry.book_slug for entry in manifest_rows])
            self.assertEqual(
                "manual_synthesis",
                [entry.source_type for entry in manifest_rows if entry.book_slug == "monitoring"][0],
            )

            self._assert_valid("document", monitoring_sections[0])
            self._assert_valid("chunk", monitoring_chunks[0])
            monitoring_playbook = next(row for row in playbook_rows if row["book_slug"] == "monitoring")
            self._assert_valid("manualbook", monitoring_playbook)
            self.assertEqual("ready", monitoring_playbook["quality_status"])
            self.assertEqual("approved", monitoring_playbook["review_status"])
            self._assert_curated_provenance_contract(
                monitoring_sections[0],
                monitoring_chunks[0],
                monitoring_playbook,
                source_id="openshift_container_platform:4.20:ko:monitoring:curated_gold_v1",
            )

    def test_apply_curated_installing_on_any_platform_gold_upserts_all_active_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            settings.source_catalog_path.parent.mkdir(parents=True, exist_ok=True)

            existing_manifest = SourceManifestEntry(
                book_slug="architecture",
                title="아키텍처",
                source_url="https://example.com/architecture",
                resolved_source_url="https://example.com/architecture",
                viewer_path="/docs/ocp/4.20/ko/architecture/index.html",
                content_status="approved_ko",
                approval_status="approved",
                citation_eligible=True,
                high_value=True,
            )
            write_manifest(settings.source_manifest_path, [existing_manifest])

            existing_section = {
                "book_slug": "architecture",
                "book_title": "아키텍처",
                "heading": "개요",
                "section_level": 1,
                "section_path": ["개요"],
                "anchor": "overview",
                "anchor_id": "overview",
                "source_url": "https://example.com/architecture",
                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                "text": "arch",
                "section_id": "architecture:overview",
                "semantic_role": "overview",
                "block_kinds": ["paragraph"],
                "source_language": "ko",
                "display_language": "ko",
                "translation_status": "approved_ko",
                "translation_stage": "approved_ko",
                "translation_source_language": "ko",
                "translation_source_url": "https://example.com/architecture",
                "translation_source_fingerprint": "x",
                "source_id": "architecture",
                "source_lane": "official_ko",
                "source_type": "official_doc",
                "source_collection": "core",
                "product": "openshift",
                "version": "4.20",
                "locale": "ko",
                "original_title": "아키텍처",
                "legal_notice_url": "",
                "license_or_terms": "",
                "review_status": "approved",
                "trust_score": 1.0,
                "verifiability": "anchor_backed",
                "updated_at": "",
                "cli_commands": [],
                "error_strings": [],
                "k8s_objects": [],
                "operator_names": [],
                "verification_hints": [],
            }
            for path in settings.normalized_docs_candidates:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(existing_section, ensure_ascii=False) + "\n", encoding="utf-8")

            for path in (settings.chunks_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")
            for path in (settings.bm25_corpus_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")
            for path in (settings.playbook_documents_path,):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")

            with patch.object(chunking, "load_sentence_model", return_value=_FakeSentenceModel()):
                report = apply_curated_installing_on_any_platform_gold(
                    settings,
                    refresh_synthesis_report=False,
                )

            self.assertEqual("installing_on_any_platform", report["book_slug"])
            self.assertGreater(report["section_count"], 0)
            self.assertGreater(report["chunk_count"], 0)
            self.assertEqual(1, report["manifest_before_count"])
            self.assertEqual(2, report["manifest_after_count"])

            normalized_rows = read_jsonl(settings.normalized_docs_path)
            chunk_rows = read_jsonl(settings.chunks_path)
            bm25_rows = read_jsonl(settings.bm25_corpus_path)
            playbook_rows = read_jsonl(settings.playbook_documents_path)
            manifest_rows = read_manifest(settings.source_manifest_path)

            install_sections = [
                row for row in normalized_rows if row["book_slug"] == "installing_on_any_platform"
            ]
            install_chunks = [
                row for row in chunk_rows if row["book_slug"] == "installing_on_any_platform"
            ]
            install_bm25 = [
                row for row in bm25_rows if row["book_slug"] == "installing_on_any_platform"
            ]
            self.assertTrue(install_sections)
            self.assertTrue(install_chunks)
            self.assertTrue(install_bm25)
            self.assertEqual(
                1,
                sum(1 for row in playbook_rows if row["book_slug"] == "installing_on_any_platform"),
            )
            self.assertEqual(
                ["architecture", "installing_on_any_platform"],
                [entry.book_slug for entry in manifest_rows],
            )
            self.assertEqual(
                "manual_synthesis",
                [
                    entry.source_type
                    for entry in manifest_rows
                    if entry.book_slug == "installing_on_any_platform"
                ][0],
            )

            self._assert_valid("document", install_sections[0])
            self._assert_valid("chunk", install_chunks[0])
            install_playbook = next(
                row for row in playbook_rows if row["book_slug"] == "installing_on_any_platform"
            )
            self._assert_valid("manualbook", install_playbook)
            self.assertEqual("ready", install_playbook["quality_status"])
            self.assertEqual("approved", install_playbook["review_status"])
            self._assert_curated_provenance_contract(
                install_sections[0],
                install_chunks[0],
                install_playbook,
                source_id="openshift_container_platform:4.20:ko:installing_on_any_platform:curated_gold_v1",
            )


if __name__ == "__main__":
    unittest.main()
