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

from play_book_studio.app.runtime_report import build_runtime_report, write_runtime_report


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


class _FakeLlmClient:
    def __init__(self, settings) -> None:  # noqa: ANN001
        self.settings = settings

    def generate(self, messages) -> str:  # noqa: ANN001
        return "ok"


class RuntimeReportTests(unittest.TestCase):
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

            def fake_get(url: str, **kwargs):  # noqa: ANN001
                del kwargs
                if url.endswith("/api/health"):
                    return _FakeResponse(200, {"ok": True})
                if url.endswith("/v1/models"):
                    return _FakeResponse(200, {"data": [{"id": "Qwen/Qwen3.5-9B"}]})
                if url.endswith("/v1/models") and "tei" in url:
                    return _FakeResponse(404, {"error": "not found"})
                if url.endswith("/collections"):
                    return _FakeResponse(
                        200,
                        {"result": {"collections": [{"name": "openshift_docs"}]}},
                    )
                if "tei.cywell.co.kr" in url:
                    return _FakeResponse(404, {"error": "not found"})
                raise AssertionError(url)

            with (
                patch("play_book_studio.app.runtime_report.requests.get", side_effect=fake_get),
                patch("play_book_studio.app.runtime_report.EmbeddingClient", _FakeEmbeddingClient),
                patch("play_book_studio.app.runtime_report.LLMClient", _FakeLlmClient),
            ):
                report = build_runtime_report(root, recent_turns=1)

        self.assertEqual("Play Book Studio", report["app"]["app_label"])
        self.assertEqual("OpenShift 4.20", report["app"]["active_pack_label"])
        self.assertEqual("http://cllm.cywell.co.kr/v1", report["runtime"]["llm_endpoint"])
        self.assertTrue(report["probes"]["local_ui"]["health_payload"]["ok"])
        self.assertTrue(report["probes"]["qdrant"]["collection_present"])
        self.assertEqual(1, len(report["reproducibility"]["recent_turns"]))
        self.assertEqual("session-1", report["reproducibility"]["recent_turns"][0]["session_id"])

    def test_write_runtime_report_writes_default_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "LLM_ENDPOINT=http://example.internal/v1\n"
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


if __name__ == "__main__":
    unittest.main()
