from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.embedding import EmbeddingClient
from ocp_rag_part1.settings import load_settings
from ocp_rag_part3.llm import LLMClient


def _auth_headers(token: str) -> dict[str, str]:
    normalized = (token or "").strip()
    if not normalized:
        return {}
    if " " in normalized:
        return {"Authorization": normalized}
    return {"Authorization": f"Bearer {normalized}"}


def _safe_json(response: requests.Response) -> dict | list | str:
    try:
        return response.json()
    except Exception:  # noqa: BLE001
        return response.text[:1000]


def main() -> int:
    settings = load_settings(ROOT)
    report: dict[str, object] = {
        "embedding": {},
        "llm": {},
    }

    try:
        embedding_models = requests.get(
            f"{settings.embedding_base_url}/models",
            headers=_auth_headers(settings.embedding_api_key),
            timeout=20,
        )
        report["embedding"] = {
            "base_url": settings.embedding_base_url,
            "models_status": embedding_models.status_code,
            "models_payload": _safe_json(embedding_models),
        }
        try:
            embedding_client = EmbeddingClient(settings)
            probe_results: list[dict[str, object]] = []
            vectors = []
            for text in ("테스트", "OpenShift 아키텍처 설명", "etcd 백업 복구"):
                started_at = time.perf_counter()
                vector_batch = embedding_client.embed_texts([text])
                latency_seconds = round(time.perf_counter() - started_at, 4)
                vectors = vector_batch
                probe_results.append(
                    {
                        "text": text,
                        "latency_seconds": latency_seconds,
                        "vector_dim": len(vector_batch[0]) if vector_batch else 0,
                    }
                )
            embedding_info = report["embedding"]
            if isinstance(embedding_info, dict):
                embedding_info["sample_embedding_ok"] = True
                embedding_info["sample_vector_dim"] = len(vectors[0]) if vectors else 0
                embedding_info["probe_results"] = probe_results
        except Exception as exc:  # noqa: BLE001
            embedding_info = report["embedding"]
            if isinstance(embedding_info, dict):
                embedding_info["sample_embedding_ok"] = False
                embedding_info["sample_embedding_error"] = str(exc)
    except Exception as exc:  # noqa: BLE001
        report["embedding"] = {
            "base_url": settings.embedding_base_url,
            "reachable": False,
            "error": str(exc),
        }

    llm_headers = _auth_headers(settings.llm_api_key)
    try:
        llm_models = requests.get(
            f"{settings.llm_endpoint}/models",
            headers=llm_headers,
            timeout=20,
        )
        report["llm"] = {
            "endpoint": settings.llm_endpoint,
            "has_api_key": bool(settings.llm_api_key),
            "models_status": llm_models.status_code,
            "models_payload": _safe_json(llm_models),
        }
        if llm_models.ok:
            try:
                started_at = time.perf_counter()
                content = LLMClient(settings).generate(
                    [{"role": "user", "content": "응답은 ok 한 단어만"}]
                )
                latency_seconds = round(time.perf_counter() - started_at, 4)
                llm_info = report["llm"]
                if isinstance(llm_info, dict):
                    llm_info["sample_completion_status"] = "ok"
                    llm_info["sample_completion_payload"] = content
                    llm_info["sample_completion_latency_seconds"] = latency_seconds
            except Exception as exc:  # noqa: BLE001
                llm_info = report["llm"]
                if isinstance(llm_info, dict):
                    llm_info["sample_completion_status"] = "error"
                    llm_info["sample_completion_payload"] = str(exc)
    except Exception as exc:  # noqa: BLE001
        report["llm"] = {
            "endpoint": settings.llm_endpoint,
            "has_api_key": bool(settings.llm_api_key),
            "reachable": False,
            "error": str(exc),
        }

    output_path = settings.part3_dir / "runtime_endpoint_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote runtime endpoint report: {output_path}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
