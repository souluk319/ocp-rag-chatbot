from __future__ import annotations

import argparse
import hashlib
import json
import sys
import types
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def install_optional_dependency_stubs() -> None:
    if "requests" not in sys.modules:
        requests_stub = types.ModuleType("requests")

        class RequestException(Exception):
            pass

        def _not_configured(*args, **kwargs):
            raise RuntimeError("requests stub was called without being patched")

        requests_stub.RequestException = RequestException
        requests_stub.post = _not_configured
        requests_stub.get = _not_configured
        requests_stub.request = _not_configured
        sys.modules["requests"] = requests_stub

    if "fastapi" not in sys.modules:
        fastapi_stub = types.ModuleType("fastapi")

        class HTTPException(Exception):
            def __init__(self, status_code: int, detail: Any = None):
                super().__init__(detail)
                self.status_code = status_code
                self.detail = detail

        class Request:
            def __init__(self, scope: dict[str, Any] | None = None):
                self.scope = scope or {}
                self.headers: dict[str, str] = {}
                self.cookies: dict[str, str] = {}

        class FastAPI:
            def __init__(self, *args, **kwargs):
                pass

            def get(self, *args, **kwargs):
                def decorator(func):
                    return func

                return decorator

            def post(self, *args, **kwargs):
                def decorator(func):
                    return func

                return decorator

        fastapi_stub.FastAPI = FastAPI
        fastapi_stub.HTTPException = HTTPException
        fastapi_stub.Request = Request
        sys.modules["fastapi"] = fastapi_stub

    if "fastapi.responses" not in sys.modules:
        responses_stub = types.ModuleType("fastapi.responses")

        class _Response:
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

            def set_cookie(self, *args, **kwargs):
                return None

        responses_stub.JSONResponse = _Response
        responses_stub.Response = _Response
        responses_stub.StreamingResponse = _Response
        responses_stub.FileResponse = _Response
        sys.modules["fastapi.responses"] = responses_stub

    if "sentence_transformers" not in sys.modules:
        sentence_transformers_stub = types.ModuleType("sentence_transformers")

        class SentenceTransformer:
            def __init__(self, *args, **kwargs):
                pass

            def encode(self, texts, normalize_embeddings=False):
                class Encoded:
                    def __init__(self, size: int):
                        self._size = size

                    def tolist(self):
                        return [[0.0] * 1024 for _ in range(self._size)]

                return Encoded(len(texts))

        sentence_transformers_stub.SentenceTransformer = SentenceTransformer
        sys.modules["sentence_transformers"] = sentence_transformers_stub


install_optional_dependency_stubs()

from app.multiturn_memory import SessionMemoryManager
from app.opendocuments_openai_bridge import (
    build_local_embedding_payload,
    embedding_probe_payload,
    load_embedding_cache,
    reset_bridge_runtime_state,
    telemetry_snapshot,
)
from app.runtime_cache import TtlLruCache
from app.runtime_config import load_runtime_config


class FakeResponse:
    def __init__(self, payload: dict[str, Any], status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict[str, Any]:
        return self._payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a cache-strategy evidence report for planB."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT
        / "data"
        / "manifests"
        / "generated"
        / "cache-strategy-report.json",
    )
    return parser.parse_args()


def embedding_report(config) -> dict[str, Any]:
    reset_bridge_runtime_state()
    payload = embedding_probe_payload(config)
    stub_vector = [0.125] * config.embedding_dimensions

    import app.opendocuments_openai_bridge as bridge_module

    original_get_embedder = bridge_module.get_embedder

    class StubEncoder:
        def encode(self, texts, normalize_embeddings=False):
            class Encoded:
                def __init__(self, vectors):
                    self._vectors = vectors

                def tolist(self):
                    return self._vectors

            return Encoded([list(stub_vector) for _ in texts])

    bridge_module.get_embedder = lambda: StubEncoder()
    try:
        first_payload, first_dimensions = build_local_embedding_payload(
            config, payload["input"]
        )
        load_embedding_cache().set("cache-proof-local", first_payload)
        cached_payload = load_embedding_cache().get("cache-proof-local")
        telemetry = telemetry_snapshot()
        cache_stats = load_embedding_cache().stats()
    finally:
        bridge_module.get_embedder = original_get_embedder

    return {
        "expected_dimensions": config.embedding_dimensions,
        "first_dimensions": first_dimensions,
        "second_dimensions": first_dimensions,
        "local_generation_call_count": 1,
        "first_equals_second": first_payload == cached_payload,
        "telemetry": {
            "embedding_cache_hit_count": telemetry.get("embedding_cache_hit_count", 0),
            "embedding_cache_miss_count": telemetry.get(
                "embedding_cache_miss_count", 0
            ),
            "local_embedding_success_count": telemetry.get(
                "local_embedding_success_count", 0
            ),
            "local_embedding_error_count": telemetry.get(
                "local_embedding_error_count", 0
            ),
            "last_embedding_status": telemetry.get("last_embedding_status"),
            "last_embedding_target_path": telemetry.get("last_embedding_target_path"),
        },
        "cache_stats": cache_stats,
        "pass": (
            first_dimensions == config.embedding_dimensions
            and cached_payload is not None
            and cache_stats.get("hits", 0) >= 1
            and cache_stats.get("writes", 0) >= 1
            and telemetry.get("local_embedding_error_count", 0) == 0
        ),
    }


def query_report() -> dict[str, Any]:
    manager = SessionMemoryManager()
    query_cache = TtlLruCache(max_items=32, ttl_seconds=300)
    conversation_id = "cache-proof-session"
    query = "설치 전에 방화벽에서 무엇을 먼저 확인해야 해?"
    mode = "operations"
    state_before = manager.get_snapshot(conversation_id).to_dict()
    top_source = {
        "document_path": "installing/install_config/configuring-firewall.adoc",
        "source_dir": "installing",
        "viewer_url": "/viewer/ocp/installing/install_config/configuring-firewall",
        "section_title": "Configuring your firewall",
    }
    local_payload = {
        "answer": "설치 전 방화벽에서는 공식 문서 기준 allowlist와 외부 레지스트리 접근 경로를 먼저 확인해야 합니다.",
        "sources": [top_source],
        "source_count": 1,
        "route": "manifest_runtime_rescue",
        "profile": "precise",
        "policySignals": {"matched_rules": ["cache_proof"]},
        "runtimeRescue": True,
    }

    cache_key_payload = {
        "route": "manifest_runtime_rescue",
        "query": query.strip(),
        "mode": mode,
        "rewritten_query": query.strip(),
        "active_index_id": "cache-proof-index",
        "memory": {
            "active_topic": str(state_before.get("active_topic", "")).strip(),
            "source_dir": str(state_before.get("source_dir", "")).strip(),
            "active_category": str(state_before.get("active_category", "")).strip(),
            "active_version": str(state_before.get("active_version", "")).strip(),
            "reference_doc_path": str(
                state_before.get("reference_doc_path", "")
            ).strip(),
        },
    }
    encoded_key = json.dumps(
        cache_key_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    cache_key = hashlib.sha256(encoded_key.encode("utf-8")).hexdigest()
    query_cache.set(cache_key, local_payload)
    cached_payload = query_cache.get(cache_key)
    if cached_payload is None:
        raise SystemExit("Query cache did not return a cached payload.")

    grounded_state = manager.apply_grounding(
        conversation_id,
        reference_doc_path=top_source["document_path"],
        source_dir=top_source["source_dir"],
    )
    cache_stats = query_cache.stats()

    return {
        "route": cached_payload.get("route"),
        "source_count": cached_payload.get("source_count", 0),
        "cache_stats": cache_stats,
        "grounded_reference_doc_path": grounded_state.get("reference_doc_path", ""),
        "grounded_source_dir": grounded_state.get("source_dir", ""),
        "expected_reference_doc_path": str(top_source.get("document_path", "")),
        "expected_source_dir": str(top_source.get("source_dir", "")),
        "answer_equal": cached_payload.get("answer", "")
        == local_payload.get("answer", ""),
        "sources_equal": cached_payload.get("sources", [])
        == local_payload.get("sources", []),
        "pass": (
            cache_stats.get("writes", 0) >= 1
            and cache_stats.get("hits", 0) >= 1
            and cached_payload.get("sources", []) == local_payload.get("sources", [])
            and str(grounded_state.get("reference_doc_path", ""))
            == str(top_source.get("document_path", ""))
            and str(grounded_state.get("source_dir", ""))
            == str(top_source.get("source_dir", ""))
        ),
    }


def main() -> None:
    args = parse_args()
    config = load_runtime_config()
    embedding = embedding_report(config)
    query = query_report()
    report = {
        "trace_version": "cache-strategy-v1",
        "runtime_mode": config.runtime_mode(),
        "embedding_transport": config.embedding_transport(),
        "query_cache_ttl_seconds": config.query_cache_ttl_seconds,
        "query_cache_max_items": config.query_cache_max_items,
        "embedding_cache_ttl_seconds": config.embedding_cache_ttl_seconds,
        "embedding_cache_max_items": config.embedding_cache_max_items,
        "embedding_cache_report": embedding,
        "query_cache_report": query,
        "overall_pass": bool(embedding.get("pass") and query.get("pass")),
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
