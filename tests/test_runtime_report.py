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

from play_book_studio.app.presenters import _build_health_payload
from play_book_studio.app.runtime_report import build_runtime_report, write_runtime_report
from play_book_studio.config.settings import Settings

TEST_RUNTIME_REPORT_LLM_ENDPOINT = "http://test-runtime-llm.example/v1"


class _FakeResponse:
    def __init__(self, status_code: int, payload) -> None:  # noqa: ANN001
        self.status_code = status_code
        self._payload = payload
        self.ok = 200 <= status_code < 300
        self.text = json.dumps(payload, ensure_ascii=False)

    def json(self):  # noqa: ANN201
        return self._payload


class _FakeEmbeddingClient:
    def __init__(self, settings) -> None:  # noqa: ANN001
        self.settings = settings

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class _BombEmbeddingClient:
    def __init__(self, settings) -> None:  # noqa: ANN001
        raise AssertionError("embedding probing should not instantiate a local client")


class _FakeLlmClient:
    def __init__(self, settings) -> None:  # noqa: ANN001
        self.settings = settings

    def generate(self, messages) -> str:  # noqa: ANN001
        return "ok"

    def runtime_metadata(self) -> dict[str, object]:
        return {}


class _FakeAnswerer:
    def __init__(self, settings) -> None:  # noqa: ANN001
        self.settings = settings
        self.llm_client = _FakeLlmClient(settings)


class RuntimeReportTests(unittest.TestCase):
    def test_build_runtime_report_skips_embedding_probe_when_unconfigured(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "LLM_ENDPOINT=http://cllm.cywell.co.kr/v1\n"
                "LLM_MODEL=Qwen/Qwen3.5-9B\n"
                "QDRANT_URL=http://localhost:6333\n"
                "QDRANT_COLLECTION=openshift_docs\n",
                encoding="utf-8",
            )

            def fake_get(url: str, **kwargs):  # noqa: ANN001
                del kwargs
                if url.endswith("/v1/models"):
                    return _FakeResponse(200, {"data": [{"id": "Qwen/Qwen3.5-9B"}]})
                if url.endswith("/collections"):
                    return _FakeResponse(
                        200,
                        {"result": {"collections": [{"name": "openshift_docs"}]}} ,
                    )
                raise AssertionError(url)

            with (
                patch("play_book_studio.app.runtime_report.requests.get", side_effect=fake_get),
                patch("play_book_studio.app.runtime_report.requests.post") as post,
                patch("play_book_studio.app.runtime_report.EmbeddingClient", _BombEmbeddingClient),
                patch("play_book_studio.app.runtime_report.LLMClient", _FakeLlmClient),
            ):
                report = build_runtime_report(root, ui_base_url=None, recent_turns=1, sample=False)

        self.assertEqual("unconfigured", report["probes"]["embedding"]["mode"])
        self.assertEqual("", report["probes"]["embedding"]["base_url"])
        self.assertEqual("Remote embedding endpoint is not configured. Local embedding execution is disabled.", report["probes"]["embedding"]["error"])
        self.assertFalse(report["probes"]["embedding"]["sample_embedding_ok"])
        post.assert_not_called()

    def test_build_runtime_report_includes_recent_turns_and_runtime_probes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "LLM_ENDPOINT=http://cllm.cywell.co.kr/v1\n"
                "LLM_MODEL=Qwen/Qwen3.5-9B\n"
                "EMBEDDING_BASE_URL=http://tei.cywell.co.kr/v1\n"
                "EMBEDDING_MODEL=dragonkue/bge-m3-ko\n"
                "QDRANT_URL=http://localhost:6333\n"
                "QDRANT_COLLECTION=openshift_docs\n",
                encoding="utf-8",
            )
            chat_log = root / "artifacts" / "runtime" / "chat_turns.jsonl"
            chat_log.parent.mkdir(parents=True, exist_ok=True)
            chat_log.write_text(
                json.dumps(
                    {
                        "session_id": "session-1",
                        "query": "Pod lifecycle 설명",
                        "answer": "Pod는 실행 단위입니다.",
                        "response_kind": "grounded",
                        "runtime": {
                            "config_fingerprint": "abc123",
                            "llm_endpoint": "http://cllm.cywell.co.kr/v1",
                            "embedding_base_url": "http://tei.cywell.co.kr/v1",
                            "qdrant_collection": "openshift_docs",
                        },
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            session_snapshot = root / "artifacts" / "runtime" / "sessions" / "session-1.json"
            session_snapshot.parent.mkdir(parents=True, exist_ok=True)
            session_snapshot.write_text(
                json.dumps(
                    {
                        "updated_at": "2026-04-12T18:00:00",
                        "session_id": "session-1",
                        "session_name": "세션 session",
                        "mode": "chat",
                        "revision": 1,
                        "context": {
                            "mode": "chat",
                            "user_goal": "replicas 조정",
                            "current_topic": "Deployment",
                            "open_entities": [],
                            "ocp_version": "4.20",
                            "selected_draft_ids": [],
                            "restrict_uploaded_sources": True,
                            "unresolved_question": None,
                        },
                        "turn_count": 1,
                        "latest_turn_id": "turn-1",
                        "turns": [
                            {
                                "turn_id": "turn-1",
                                "parent_turn_id": "",
                                "created_at": "2026-04-12T18:00:00",
                                "query": "Pod lifecycle 설명",
                                "mode": "chat",
                                "answer": "Pod는 실행 단위입니다.",
                                "rewritten_query": "Pod lifecycle 설명",
                                "response_kind": "grounded",
                                "warnings": [],
                                "stages": [],
                                "diagnosis": {"severity": "ok", "summary": "정상", "signals": ["문제 신호 없음"]},
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            def fake_get(url: str, **kwargs):  # noqa: ANN001
                del kwargs
                if url.endswith("/api/health"):
                    return _FakeResponse(200, {"ok": True})
                if url.endswith("/v1/models") and "tei" in url:
                    return _FakeResponse(404, {"error": "not found"})
                if url.endswith("/v1/models"):
                    return _FakeResponse(200, {"data": [{"id": "Qwen/Qwen3.5-9B"}]})
                if url.endswith("/collections"):
                    return _FakeResponse(
                        200,
                        {"result": {"collections": [{"name": "openshift_docs"}]}},
                    )
                raise AssertionError(url)

            def fake_post(url: str, json=None, **kwargs):  # noqa: ANN001
                del kwargs
                if url.endswith("/v1/embeddings"):
                    return _FakeResponse(
                        200,
                        {
                            "object": "list",
                            "data": [{"object": "embedding", "embedding": [0.1, 0.2, 0.3], "index": 0}],
                            "model": "dragonkue/BGE-m3-ko",
                            "usage": {"prompt_tokens": 3, "total_tokens": 3},
                        },
                    )
                raise AssertionError(url)

            with (
                patch("play_book_studio.app.runtime_report.requests.get", side_effect=fake_get),
                patch("play_book_studio.app.runtime_report.requests.post", side_effect=fake_post),
                patch("play_book_studio.app.runtime_report.EmbeddingClient", _FakeEmbeddingClient),
                patch("play_book_studio.app.runtime_report.LLMClient", _FakeLlmClient),
            ):
                report = build_runtime_report(root, recent_turns=1, sample=False)

        self.assertEqual("Play Book Studio", report["app"]["app_label"])
        self.assertEqual("OpenShift 4.20", report["app"]["active_pack_label"])
        self.assertEqual("http://cllm.cywell.co.kr/v1", report["runtime"]["llm_endpoint"])
        self.assertEqual("filesystem_snapshot_store", report["reproducibility"]["session_strategy"])
        self.assertEqual(1, report["reproducibility"]["session_snapshot_count"])
        self.assertTrue(report["probes"]["local_ui"]["health_payload"]["ok"])
        self.assertTrue(report["probes"]["qdrant"]["collection_present"])
        self.assertEqual(404, report["probes"]["embedding"]["models_status"])
        self.assertFalse(report["probes"]["embedding"]["models_endpoint_supported"])
        self.assertEqual(200, report["probes"]["embedding"]["health_status"])
        self.assertTrue(report["probes"]["embedding"]["sample_embedding_ok"])
        self.assertEqual("dragonkue/BGE-m3-ko", report["probes"]["embedding"]["resolved_model"])
        self.assertEqual(1, len(report["reproducibility"]["recent_turns"]))
        self.assertEqual("session-1", report["reproducibility"]["recent_turns"][0]["session_id"])

    def test_write_runtime_report_writes_default_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                f"LLM_ENDPOINT={TEST_RUNTIME_REPORT_LLM_ENDPOINT}\n"
                "EMBEDDING_MODEL=test-model\n",
                encoding="utf-8",
            )
            with (
                patch("play_book_studio.app.runtime_report.requests.get", side_effect=RuntimeError("offline")),
                patch("play_book_studio.app.runtime_report.EmbeddingClient", _FakeEmbeddingClient),
                patch("play_book_studio.app.runtime_report.LLMClient", _FakeLlmClient),
            ):
                output_path, report = write_runtime_report(root, sample=False, ui_base_url=None)
                self.assertTrue(output_path.exists())
                self.assertEqual(output_path.name, "runtime_report.json")
                self.assertEqual("Play Book Studio", report["app"]["app_label"])

    def test_runtime_report_and_health_payload_expose_stale_compact_graph_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                f"LLM_ENDPOINT={TEST_RUNTIME_REPORT_LLM_ENDPOINT}\n"
                "QDRANT_URL=http://localhost:6333\n"
                "QDRANT_COLLECTION=openshift_docs\n",
                encoding="utf-8",
            )
            settings = Settings(root_dir=root)
            settings.graph_sidecar_compact_path.parent.mkdir(parents=True, exist_ok=True)
            settings.graph_sidecar_compact_path.write_text(
                json.dumps(
                    {
                        "schema": "graph_sidecar_compact_v1",
                        "schema_version": "graph_sidecar_compact_v1",
                        "book_count": 1,
                        "relation_count": 0,
                        "books": [{"book_slug": "monitoring", "title": "모니터링"}],
                        "relations": [],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            settings.chunks_path.parent.mkdir(parents=True, exist_ok=True)
            settings.chunks_path.write_text(
                json.dumps({"chunk_id": "monitoring::0", "book_slug": "monitoring"}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            settings.playbook_documents_path.parent.mkdir(parents=True, exist_ok=True)
            settings.playbook_documents_path.write_text(
                json.dumps({"book_slug": "monitoring", "title": "모니터링"}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            def fake_get(url: str, **kwargs):  # noqa: ANN001
                del kwargs
                if url.endswith("/v1/models"):
                    return _FakeResponse(200, {"data": [{"id": "test"}]})
                if url.endswith("/collections"):
                    return _FakeResponse(
                        200,
                        {"result": {"collections": [{"name": "openshift_docs"}]}},
                    )
                raise AssertionError(url)

            with (
                patch("play_book_studio.app.runtime_report.requests.get", side_effect=fake_get),
                patch("play_book_studio.app.runtime_report.requests.post", side_effect=RuntimeError("unused")),
                patch("play_book_studio.app.runtime_report.LLMClient", _FakeLlmClient),
            ):
                report = build_runtime_report(root, sample=False, ui_base_url=None)

            health_payload = _build_health_payload(_FakeAnswerer(settings))
            compact_runtime = report["runtime"]["graph_compact_artifact"]
            compact_health = health_payload["runtime"]["graph_compact_artifact"]

            self.assertEqual("stale", compact_runtime["state"])
            self.assertFalse(compact_runtime["ready"])
            self.assertEqual("playbook_documents_runtime_fallback", compact_runtime["degrade_mode"])
            self.assertEqual("stale", compact_health["state"])
            self.assertFalse(compact_health["ready"])


if __name__ == "__main__":
    unittest.main()
