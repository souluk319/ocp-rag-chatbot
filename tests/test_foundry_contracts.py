from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.canonical import project_playbook_document
from play_book_studio.config.settings import Settings
from play_book_studio.ingestion import chunking
from play_book_studio.ingestion.chunking import chunk_sections
from play_book_studio.ingestion.models import ParsedArtifactRecord, SourceManifestEntry
from play_book_studio.ingestion.normalize import extract_document_ast, extract_sections


class _FakeTokenizer:
    def __init__(self) -> None:
        self.model_max_length = 8

    def __call__(self, text: str, **_: object) -> dict[str, list[int]]:
        return {"input_ids": [ord(char) for char in text]}


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
            if not ref.startswith("#/$defs/"):
                raise AssertionError(f"{path}: unsupported ref {ref}")
            target = str(ref).split("/")[-1]
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
            raise AssertionError(errors[0] if errors else f"{path}: anyOf validation failed")

        expected_type = schema.get("type")
        if expected_type == "object":
            if not isinstance(payload, dict):
                raise AssertionError(f"{path}: expected object")
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            for key in required:
                if key not in payload:
                    raise AssertionError(f"{path}: missing required property '{key}'")
            if schema.get("additionalProperties") is False:
                extras = sorted(set(payload) - set(properties))
                if extras:
                    raise AssertionError(f"{path}: unexpected properties {extras}")
            for key, value in payload.items():
                child_schema = properties.get(key)
                additional = schema.get("additionalProperties")
                if child_schema is None and isinstance(additional, dict):
                    child_schema = additional
                if child_schema is not None:
                    self.validate(value, child_schema, f"{path}.{key}")
            return

        if expected_type == "array":
            if not isinstance(payload, (list, tuple)):
                raise AssertionError(f"{path}: expected array")
            item_schema = schema.get("items")
            if isinstance(item_schema, dict):
                for index, item in enumerate(payload):
                    self.validate(item, item_schema, f"{path}[{index}]")
            return

        if expected_type == "string":
            if not isinstance(payload, str):
                raise AssertionError(f"{path}: expected string")
            min_length = schema.get("minLength")
            if min_length is not None and len(payload) < int(min_length):
                raise AssertionError(f"{path}: shorter than minLength {min_length}")
            pattern = schema.get("pattern")
            if pattern and re.match(str(pattern), payload) is None:
                raise AssertionError(f"{path}: value '{payload}' does not match pattern {pattern}")
        elif expected_type == "integer":
            if not isinstance(payload, int) or isinstance(payload, bool):
                raise AssertionError(f"{path}: expected integer")
        elif expected_type == "number":
            if not isinstance(payload, (int, float)) or isinstance(payload, bool):
                raise AssertionError(f"{path}: expected number")

        if "enum" in schema and payload not in schema["enum"]:
            raise AssertionError(f"{path}: value '{payload}' not in enum {schema['enum']}")
        if "minimum" in schema and payload < schema["minimum"]:
            raise AssertionError(f"{path}: value {payload} is smaller than minimum {schema['minimum']}")
        if "maximum" in schema and payload > schema["maximum"]:
            raise AssertionError(f"{path}: value {payload} is larger than maximum {schema['maximum']}")


class FoundryContractTests(unittest.TestCase):
    def _load_schema(self, name: str) -> dict[str, object]:
        return json.loads((ROOT / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8"))

    def _assert_schema_valid(self, name: str, payload: dict[str, object]) -> None:
        validator = _SchemaValidator(self._load_schema(name))
        try:
            validator.validate(payload)
        except AssertionError as exc:
            self.fail(f"{name} schema validation failed:\n{exc}")

    def test_foundry_contract_payloads_validate_against_schemas(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>Ingress troubleshooting</h1>
                <h2 id="router-check">Router check</h2>
                <p>확인: Route 상태를 점검합니다.</p>
                <p>ImagePullBackOff 가 발생하면 Deployment 상태도 함께 확인합니다.</p>
                <p>Machine Config Operator 와 Ingress Operator 로그를 검토합니다.</p>
                <pre><code>$ oc get pods -n openshift-ingress
kubectl describe deployment router-default -n openshift-ingress</code></pre>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="ingress",
            title="Ingress troubleshooting",
            source_url="https://example.com/ingress",
            viewer_path="/docs/ingress/index.html",
            source_id="src-1",
            source_lane="official_ko",
            source_type="official_doc",
            source_collection="core",
            legal_notice_url="https://example.com/legal",
            license_or_terms="OpenShift documentation is licensed under the Apache License 2.0.",
            updated_at="2026-04-10T00:00:00Z",
            review_status="approved",
            high_value=True,
        )

        sections = extract_sections(html, entry)
        self.assertEqual(1, len(sections))
        document_payload = sections[0].to_contract_dict()
        self._assert_schema_valid("document", document_payload)

        document = extract_document_ast(html, entry)
        manualbook_payload = project_playbook_document(document).to_dict()
        self._assert_schema_valid("manualbook", manualbook_payload)

        settings = Settings(root_dir=ROOT)
        with patch.object(chunking, "load_sentence_model", return_value=_FakeSentenceModel()):
            chunks = chunk_sections(sections, settings)

        self.assertGreaterEqual(len(chunks), 1)
        for chunk in chunks:
            self._assert_schema_valid("chunk", chunk.to_dict())

        parsed_artifact = ParsedArtifactRecord(
            parsed_artifact_id="parsed:src-1",
            source_ref={
                "source_id": entry.source_id,
                "source_type": entry.source_type,
                "source_lane": entry.source_lane,
                "source_collection": entry.source_collection,
                "product": entry.product_slug,
                "version": entry.ocp_version,
                "locale": entry.docs_language,
            },
            raw_asset_ref={
                "raw_asset_uri": entry.source_url,
                "source_fingerprint": "fp-1",
                "raw_asset_hash": "sha256:demo",
            },
            parser_route="html_native",
            parser_backend="canonical_html_v1",
            parser_version="1.0",
            page_refs=(
                {
                    "page_id": "page-1",
                    "page_no": 1,
                    "asset_ref": f"{entry.source_url}#page=1",
                    "text_length": len(html),
                    "ocr_confidence": 1.0,
                },
            ),
            layout_blocks=(
                {
                    "block_id": "block-1",
                    "page_no": 1,
                    "kind": "article",
                    "bbox": [0, 0, 100, 100],
                    "text": "Router check",
                    "confidence": 0.99,
                },
            ),
            section_trace_hints=(
                {
                    "section_id": sections[0].section_id,
                    "page_no": 1,
                    "block_ids": ["block-1"],
                },
            ),
            quality_state={
                "parse_status": "parsed",
                "review_status": entry.review_status,
                "trust_score": 1.0,
                "updated_at": entry.updated_at,
            },
            security_envelope={
                "tenant_id": "public",
                "workspace_id": "core",
                "pack_id": "openshift-4.20-core",
                "classification": "public",
                "access_groups": ["public"],
                "provider_egress_policy": "unspecified",
                "redaction_state": "not_required",
            },
            promotion_trace={
                "source_stage": "bronze_raw",
                "target_stage": "bronze_parsed",
                "decision": "accepted",
                "updated_at": entry.updated_at,
            },
        )
        self._assert_schema_valid("parsed_artifact", parsed_artifact.to_dict())

    def test_parsed_artifact_schema_rejects_missing_security_envelope(self) -> None:
        payload = ParsedArtifactRecord(
            parsed_artifact_id="parsed:src-1",
            source_ref={
                "source_id": "src-1",
                "source_type": "official_doc",
                "source_lane": "official_ko",
                "source_collection": "core",
                "product": "openshift_container_platform",
                "version": "4.20",
                "locale": "ko",
            },
            raw_asset_ref={
                "raw_asset_uri": "https://example.com/nodes",
                "source_fingerprint": "fp-1",
                "raw_asset_hash": "sha256:test",
            },
            page_refs=({"page_id": "page-1", "page_no": 1},),
            quality_state={
                "parse_status": "parsed",
                "review_status": "approved",
                "trust_score": 1.0,
                "updated_at": "2026-04-11T00:00:00Z",
            },
            security_envelope={
                "tenant_id": "public",
                "workspace_id": "core",
                "pack_id": "openshift-4.20-core",
                "classification": "public",
                "access_groups": ["public"],
                "provider_egress_policy": "unspecified",
                "redaction_state": "not_required",
            },
            promotion_trace={
                "source_stage": "bronze_raw",
                "target_stage": "bronze_parsed",
                "decision": "accepted",
                "updated_at": "2026-04-11T00:00:00Z",
            },
        ).to_dict()
        del payload["security_envelope"]

        validator = _SchemaValidator(self._load_schema("parsed_artifact"))
        with self.assertRaisesRegex(AssertionError, "missing required property 'security_envelope'"):
            validator.validate(payload)


if __name__ == "__main__":
    unittest.main()
