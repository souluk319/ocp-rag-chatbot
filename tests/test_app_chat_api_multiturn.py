from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib import request

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.answering.models import AnswerResult, Citation
from play_book_studio.app.server import _build_handler
from play_book_studio.app.sessions import SessionStore
from play_book_studio.config.settings import load_settings

MANIFEST_PATH = ROOT / "manifests" / "demo_multiturn_scenarios.jsonl"


def _load_scenarios() -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class _FakeLlmClient:
    def runtime_metadata(self) -> dict[str, object]:
        return {
            "preferred_provider": "openai-compatible",
            "fallback_enabled": False,
            "last_provider": "openai-compatible",
            "last_fallback_used": False,
            "last_attempted_providers": ["openai-compatible"],
        }


class _FakeAnswerer:
    def __init__(self, *, root_dir: Path, responses: dict[str, list[dict[str, object]]]) -> None:
        self.settings = load_settings(root_dir)
        self.llm_client = _FakeLlmClient()
        self._responses = responses

    def answer(
        self,
        query: str,
        *,
        mode: str,
        context,
        top_k: int,
        candidate_k: int,
        max_context_chunks: int,
        trace_callback=None,
    ) -> AnswerResult:
        del top_k, candidate_k, max_context_chunks
        candidates = self._responses[query]
        spec = candidates[0]
        current_topic = (getattr(context, "current_topic", "") or "").strip()
        if len(candidates) > 1 and current_topic:
            for candidate in candidates:
                if str(candidate["topic"]) == current_topic:
                    spec = candidate
                    break
        citation = Citation(
            index=1,
            chunk_id=f"chunk-{spec['id']}",
            book_slug=str(spec["book_slug"]),
            section=str(spec["topic"]),
            anchor=f"{spec['id']}-anchor",
            source_url=f"https://example.com/{spec['book_slug']}",
            viewer_path=f"/docs/ocp/4.20/ko/{spec['book_slug']}/index.html#{spec['id']}-anchor",
            excerpt=str(spec["topic"]),
        )
        if callable(trace_callback):
            trace_callback(
                {
                    "type": "trace",
                    "step": "retrieval_complete",
                    "label": "검색 완료",
                    "status": "done",
                    "detail": str(spec["book_slug"]),
                }
            )
        return AnswerResult(
            query=query,
            mode=mode,
            answer=f"답변: {spec['topic']} [1]",
            rewritten_query=f"OCP 4.20 | {query}",
            citations=[citation],
            cited_indices=[1],
            retrieval_trace={
                "metrics": {"hybrid": {"count": 1}},
                "top_book_slugs": [spec["book_slug"]],
            },
            pipeline_trace={"timings_ms": {"total": 1}},
        )

    def append_log(self, result: AnswerResult) -> None:
        del result


class TestAppChatApiMultiturn(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenarios = _load_scenarios()
        cls._tempdir = tempfile.TemporaryDirectory()
        cls.root_dir = Path(cls._tempdir.name)
        cls.responses: dict[str, list[dict[str, object]]] = {}
        for scenario in cls.scenarios:
            for turn in scenario["turns"]:
                cls.responses.setdefault(str(turn["query"]), []).append({
                    "id": f"{scenario['id']}-t{turn['turn']}",
                    "topic": str(turn["expected_topic"]),
                    "book_slug": str((turn["expected_book_slugs"] or ["overview"])[0]),
                })

        answerer = _FakeAnswerer(root_dir=cls.root_dir, responses=cls.responses)
        store = SessionStore()
        handler = _build_handler(answerer=answerer, store=store, root_dir=cls.root_dir)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        cls._tempdir.cleanup()

    def _post_chat(self, *, session_id: str, query: str) -> dict[str, object]:
        req = request.Request(
            f"http://127.0.0.1:{self.port}/api/chat",
            data=json.dumps({"session_id": session_id, "query": query}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def test_multiturn_manifest_runs_end_to_end_via_api_chat(self) -> None:
        self.assertEqual(5, len(self.scenarios))

        for scenario in self.scenarios:
            session_id = str(scenario["id"])
            turns = scenario["turns"]
            self.assertEqual(6, len(turns), scenario["id"])
            observed_topics: list[str] = []

            for turn in turns:
                payload = self._post_chat(session_id=session_id, query=str(turn["query"]))
                observed_topics.append(str(payload["context"]["current_topic"]))

                self.assertEqual(session_id, payload["session_id"], scenario["id"])
                self.assertEqual("rag", payload["response_kind"], scenario["id"])
                self.assertEqual(turn["expected_topic"], payload["context"]["current_topic"], scenario["id"])
                self.assertEqual(int(turn["turn"]), payload["history_size"], scenario["id"])
                self.assertTrue(payload["citations"], scenario["id"])
                self.assertEqual(
                    str((turn["expected_book_slugs"] or ["overview"])[0]),
                    payload["citations"][0]["book_slug"],
                    scenario["id"],
                )
                self.assertFalse(payload["warnings"], scenario["id"])

            if str(scenario["track"]) == "topic-retention":
                self.assertEqual(
                    {str(turns[0]["expected_topic"])},
                    set(observed_topics),
                    scenario["id"],
                )
            else:
                self.assertEqual("OpenShift 아키텍처", observed_topics[0], scenario["id"])
                self.assertEqual("Route와 Ingress 비교", observed_topics[2], scenario["id"])
                self.assertEqual("2.1.5.2. 클러스터의 모든 심각한 경고 해결", observed_topics[4], scenario["id"])
                self.assertGreater(len(set(observed_topics)), 1, scenario["id"])


if __name__ == "__main__":
    unittest.main()
