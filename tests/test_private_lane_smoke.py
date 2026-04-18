from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import requests
from http.server import ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.answering.models import AnswerResult, Citation
from play_book_studio.app.private_lane_smoke import (
    build_private_lane_smoke,
    summarize_private_lane_boundary,
)
from play_book_studio.app.server import _build_handler
from play_book_studio.app.sessions import SessionStore
from play_book_studio.config.settings import load_settings


class _FakeTokenizer:
    model_max_length = 1024

    def __call__(self, text: str, **kwargs):
        del kwargs
        token_count = max(len(str(text).split()), 1)
        return {"input_ids": list(range(token_count))}


class _FakeVectorRow:
    def __init__(self, values: list[float]) -> None:
        self._values = values

    def tolist(self) -> list[float]:
        return list(self._values)


class _FakeChunkingModel:
    tokenizer = _FakeTokenizer()


class _FakeEmbeddingModel:
    def encode(self, texts, **kwargs):
        del kwargs
        return [_FakeVectorRow([1.0, 0.0, 0.0]) for _ in texts]


class _FakeLlmClient:
    def runtime_metadata(self) -> dict[str, object]:
        return {
            "preferred_provider": "deterministic-test",
            "fallback_enabled": False,
            "last_provider": "deterministic-test",
            "last_fallback_used": False,
            "last_attempted_providers": ["deterministic-test"],
        }


class _FakeAnswerer:
    def __init__(self, settings) -> None:
        self.settings = settings
        self.llm_client = _FakeLlmClient()
        self.retriever = SimpleNamespace(reranker=None)

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    def append_log(self, result: AnswerResult, log_path: Path | None = None) -> Path:
        target = log_path or self.settings.answer_log_path
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")
        return target

    def answer(
        self,
        query: str,
        *,
        mode: str = "chat",
        context=None,
        top_k: int = 8,
        candidate_k: int = 20,
        max_context_chunks: int = 6,
        trace_callback=None,
    ) -> AnswerResult:
        del top_k, candidate_k, max_context_chunks, trace_callback
        selected_draft_ids = [
            str(item).strip()
            for item in getattr(context, "selected_draft_ids", []) or []
            if str(item).strip()
        ]
        if selected_draft_ids and bool(getattr(context, "restrict_uploaded_sources", True)):
            draft_id = selected_draft_ids[0]
            citation = Citation(
                index=1,
                chunk_id=f"{draft_id}:configmap-secret",
                book_slug="private-lane-smoke",
                section="ConfigMap Secret",
                anchor="configmap-secret",
                source_url=f"/api/customer-packs/captured?draft_id={draft_id}",
                viewer_path=f"/playbooks/customer-packs/{draft_id}/index.html#configmap-secret",
                excerpt="ConfigMap Secret values must be synchronized before rollout.",
                source_collection="uploaded",
            )
            return AnswerResult(
                query=query,
                mode=mode,
                answer="답변: 해당 private 문서는 ConfigMap Secret 동기화를 설명합니다 [1].",
                rewritten_query=query,
                citations=[citation],
                response_kind="rag",
                cited_indices=[1],
                warnings=[],
                retrieval_trace={"route": "private_lane_smoke"},
                pipeline_trace={"mode": "private_lane_smoke"},
            )
        return AnswerResult(
            query=query,
            mode=mode,
            answer="답변: 현재 Playbook Library에 해당 자료가 없습니다. 자료 추가가 필요합니다.",
            rewritten_query=query,
            citations=[],
            response_kind="no_answer",
            cited_indices=[],
            warnings=["no context citations assembled"],
            retrieval_trace={"route": "private_lane_smoke"},
            pipeline_trace={"mode": "private_lane_smoke"},
        )


@contextmanager
def _test_server(root: Path):
    settings = load_settings(root)
    answerer = _FakeAnswerer(settings)
    store = SessionStore(root)
    handler = _build_handler(answerer=answerer, store=store, root_dir=root)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


class PrivateLaneSmokeTests(unittest.TestCase):
    def test_summarize_private_lane_boundary_detects_missing_fields(self) -> None:
        summary = summarize_private_lane_boundary(
            {
                "tenant_id": "default-tenant",
                "workspace_id": "default-workspace",
                "pack_id": "pack-a",
                "pack_version": "v1",
                "classification": "private",
                "provider_egress_policy": "local_only",
                "approval_state": "unreviewed",
                "publication_state": "draft",
                "redaction_state": "not_required",
                "boundary_truth": "private_customer_pack_runtime",
                "runtime_truth_label": "Customer Source-First Pack",
                "boundary_badge": "Private Pack Runtime",
            }
        )

        self.assertFalse(summary["ok"])
        self.assertEqual(["access_groups"], summary["missing_security_fields"])
        self.assertIn("tenant_id", summary["placeholder_security_fields"])
        self.assertIn("workspace_id", summary["placeholder_security_fields"])
        self.assertFalse(summary["approval_ready"])
        self.assertIn("approval_not_runtime_ready:unreviewed", summary["fail_reasons"])
        self.assertEqual([], summary["missing_boundary_fields"])

    def test_build_private_lane_smoke_runs_end_to_end_against_temp_server(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            with (
                patch(
                    "play_book_studio.intake.private_corpus.load_sentence_model",
                    return_value=_FakeEmbeddingModel(),
                ),
                patch(
                    "play_book_studio.ingestion.chunking.load_sentence_model",
                    return_value=_FakeChunkingModel(),
                ),
                _test_server(root) as base_url,
            ):
                payload = build_private_lane_smoke(root, ui_base_url=base_url)

            summary = payload["summary"]
            self.assertTrue(summary["ok"])
            self.assertTrue(summary["ingest_ok"])
            self.assertTrue(summary["private_corpus_ready"])
            self.assertTrue(summary["boundary_fields_complete"])
            self.assertTrue(summary["book_ok"])
            self.assertTrue(summary["viewer_ok"])
            self.assertTrue(summary["selected_chat_private_hit"])
            self.assertTrue(summary["selected_chat_private_boundary"])
            self.assertTrue(summary["no_leak_ok"])
            self.assertTrue(summary["cleanup_ok"])
            self.assertTrue(payload["smoke"]["private_corpus"]["runtime_eligible"])
            self.assertEqual([], payload["smoke"]["private_corpus"]["boundary_fail_reasons"])
            self.assertEqual(
                "private_customer_pack_runtime",
                payload["smoke"]["private_corpus"]["boundary_truth"],
            )
            cleanup_payload = payload["probes"]["cleanup"]["payload"]
            self.assertTrue(cleanup_payload["success"])
            self.assertFalse(
                any((root / "artifacts" / "customer_packs" / "drafts").glob("*.json"))
            )


if __name__ == "__main__":
    unittest.main()
