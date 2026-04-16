from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib import request

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.answering.models import AnswerResult, Citation
from play_book_studio.app.server import _build_handler
from play_book_studio.app.sessions import SessionStore
from play_book_studio.config.settings import load_settings
from play_book_studio.retrieval.text_utils import strip_section_prefix

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
        cls.root_dir.joinpath(".env").write_text(
            f"ARTIFACTS_DIR={cls.root_dir / 'artifacts'}\n",
            encoding="utf-8",
        )
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

    def _post_chat_stream(self, *, session_id: str, query: str) -> list[dict[str, object]]:
        req = request.Request(
            f"http://127.0.0.1:{self.port}/api/chat/stream",
            data=json.dumps({"session_id": session_id, "query": query}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=10) as resp:
            lines = [line.strip() for line in resp.read().decode("utf-8").splitlines() if line.strip()]
        return [json.loads(line) for line in lines]

    def _post_json(self, path: str, payload: dict[str, object]) -> tuple[int, dict[str, object]]:
        req = request.Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=10) as resp:
                return int(resp.status), json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8")
            return int(exc.code), json.loads(body or "{}")

    def _get_json(self, path: str) -> tuple[int, dict[str, object]]:
        req = request.Request(
            f"http://127.0.0.1:{self.port}{path}",
            method="GET",
        )
        try:
            with request.urlopen(req, timeout=10) as resp:
                return int(resp.status), json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8")
            return int(exc.code), json.loads(body or "{}")

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
                self.assertEqual(
                    strip_section_prefix(str(turn["expected_topic"])),
                    payload["context"]["current_topic"],
                    scenario["id"],
                )
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
                self.assertEqual("클러스터의 모든 심각한 경고 해결", observed_topics[4], scenario["id"])
                self.assertGreater(len(set(observed_topics)), 1, scenario["id"])

    def test_chat_stream_emits_runtime_trace_then_final_result(self) -> None:
        query = str(self.scenarios[0]["turns"][0]["query"])
        events = self._post_chat_stream(session_id="stream-smoke", query=query)

        self.assertGreaterEqual(len(events), 3)
        self.assertEqual("trace", events[0]["type"])
        self.assertEqual("request_received", events[0]["step"])
        self.assertTrue(any(event.get("type") == "trace" and event.get("step") == "retrieval_complete" for event in events))
        self.assertEqual("result", events[-1]["type"])
        payload = events[-1]["payload"]
        self.assertIn("retrieval_trace", payload)
        self.assertIn("pipeline_trace", payload)
        self.assertIn("rewritten_query", payload)
        self.assertEqual("rag", payload["response_kind"])

    def test_session_delete_endpoint_removes_saved_history(self) -> None:
        session_id = "delete-me"
        query = str(self.scenarios[0]["turns"][0]["query"])
        self._post_chat(session_id=session_id, query=query)

        status, sessions_payload = self._get_json("/api/sessions?limit=20")
        self.assertEqual(200, status)
        self.assertIn(session_id, [item["session_id"] for item in sessions_payload["sessions"]])

        status, delete_payload = self._post_json("/api/sessions/delete", {"session_id": session_id})
        self.assertEqual(200, status)
        self.assertTrue(delete_payload["success"])

        status, sessions_payload = self._get_json("/api/sessions?limit=20")
        self.assertEqual(200, status)
        self.assertNotIn(session_id, [item["session_id"] for item in sessions_payload["sessions"]])

        status, load_payload = self._get_json(f"/api/sessions/load?session_id={session_id}")
        self.assertEqual(404, status)
        self.assertEqual("Session not found", load_payload["error"])

    def test_sessions_delete_all_endpoint_removes_all_saved_history(self) -> None:
        query = str(self.scenarios[0]["turns"][0]["query"])
        self._post_chat(session_id="delete-all-1", query=query)
        self._post_chat(session_id="delete-all-2", query=query)

        status, delete_payload = self._post_json("/api/sessions/delete-all", {})
        self.assertEqual(200, status)
        self.assertTrue(delete_payload["success"])
        self.assertGreaterEqual(int(delete_payload["deleted_count"]), 2)

        status, sessions_payload = self._get_json("/api/sessions?limit=20")
        self.assertEqual(200, status)
        self.assertEqual([], sessions_payload["sessions"])


if __name__ == "__main__":
    unittest.main()
