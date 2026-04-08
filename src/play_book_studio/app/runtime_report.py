"""시연, 운영 점검, 재현성 확인을 위한 runtime readiness 리포트.

누군가 "지금 이 프로세스가 실제로 어디에 연결돼 있나?"라고 물었을 때
가장 표준적으로 답하는 모듈이다.
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from play_book_studio.answering.llm import LLMClient
from play_book_studio.config.settings import Settings, load_settings
from play_book_studio.ingestion.embedding import EmbeddingClient


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


def _iso_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _path_status(path: Path) -> dict[str, Any]:
    exists = path.exists()
    payload: dict[str, Any] = {
        "path": str(path),
        "exists": exists,
    }
    if exists and path.is_file():
        stat = path.stat()
        payload["size_bytes"] = stat.st_size
        payload["mtime"] = datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec="seconds")
    return payload


def _read_recent_chat_turns(settings: Settings, *, limit: int) -> list[dict[str, Any]]:
    log_path = settings.chat_log_path
    if not log_path.exists():
        return []
    lines = [line for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = [json.loads(line) for line in lines[-limit:]]
    summary: list[dict[str, Any]] = []
    for row in rows:
        answer_text = str(row.get("answer") or "")
        runtime = row.get("runtime") or {}
        summary.append(
            {
                "session_id": str(row.get("session_id") or ""),
                "query": str(row.get("query") or ""),
                "answer_preview": answer_text[:160],
                "response_kind": str(row.get("response_kind") or ""),
                "config_fingerprint": str(runtime.get("config_fingerprint") or ""),
                "llm_endpoint": str(runtime.get("llm_endpoint") or ""),
                "embedding_base_url": str(runtime.get("embedding_base_url") or ""),
                "qdrant_collection": str(runtime.get("qdrant_collection") or ""),
            }
        )
    return summary


def _probe_embedding(settings: Settings, *, sample: bool) -> dict[str, Any]:
    report: dict[str, Any] = {
        "mode": "remote" if settings.embedding_base_url else "local",
        "base_url": settings.embedding_base_url,
        "model": settings.embedding_model,
        "device": settings.embedding_device,
    }
    try:
        if settings.embedding_base_url:
            response = requests.get(
                f"{settings.embedding_base_url}/models",
                headers=_auth_headers(settings.embedding_api_key),
                timeout=20,
            )
            report["models_status"] = response.status_code
            report["models_payload"] = _safe_json(response)
        if sample:
            started_at = time.perf_counter()
            vectors = EmbeddingClient(settings).embed_texts(["OpenShift 아키텍처 설명"])
            report["sample_embedding_ok"] = True
            report["sample_vector_dim"] = len(vectors[0]) if vectors else 0
            report["sample_latency_seconds"] = round(time.perf_counter() - started_at, 4)
    except Exception as exc:  # noqa: BLE001
        report["sample_embedding_ok"] = False
        report["error"] = str(exc)
    return report


def _probe_llm(settings: Settings, *, sample: bool) -> dict[str, Any]:
    report: dict[str, Any] = {
        "endpoint": settings.llm_endpoint,
        "model": settings.llm_model,
        "has_api_key": bool(settings.llm_api_key),
    }
    try:
        response = requests.get(
            f"{settings.llm_endpoint}/models",
            headers=_auth_headers(settings.llm_api_key),
            timeout=20,
        )
        report["models_status"] = response.status_code
        report["models_payload"] = _safe_json(response)
        if sample and response.ok:
            started_at = time.perf_counter()
            completion = LLMClient(settings).generate(
                [{"role": "user", "content": "응답은 ok 한 단어만"}]
            )
            report["sample_completion_ok"] = True
            report["sample_completion_latency_seconds"] = round(time.perf_counter() - started_at, 4)
            report["sample_completion_payload"] = completion
    except Exception as exc:  # noqa: BLE001
        report["sample_completion_ok"] = False
        report["error"] = str(exc)
    return report


def _probe_qdrant(settings: Settings) -> dict[str, Any]:
    report: dict[str, Any] = {
        "url": settings.qdrant_url,
        "collection": settings.qdrant_collection,
    }
    try:
        response = requests.get(
            f"{settings.qdrant_url}/collections",
            timeout=20,
        )
        report["collections_status"] = response.status_code
        payload = _safe_json(response)
        report["collections_payload"] = payload
        if isinstance(payload, dict):
            collections = payload.get("result", {}).get("collections", [])
            report["collection_present"] = any(
                str(item.get("name") or "") == settings.qdrant_collection
                for item in collections
                if isinstance(item, dict)
            )
    except Exception as exc:  # noqa: BLE001
        report["error"] = str(exc)
    return report


def _probe_local_ui(ui_base_url: str | None) -> dict[str, Any]:
    if not ui_base_url:
        return {"enabled": False}
    report: dict[str, Any] = {
        "enabled": True,
        "base_url": ui_base_url.rstrip("/"),
    }
    try:
        response = requests.get(f"{report['base_url']}/api/health", timeout=10)
        report["health_status"] = response.status_code
        report["health_payload"] = _safe_json(response)
    except Exception as exc:  # noqa: BLE001
        report["error"] = str(exc)
    return report


def build_runtime_report(
    root_dir: str | Path,
    *,
    ui_base_url: str | None = "http://127.0.0.1:8765",
    recent_turns: int = 3,
    sample: bool = True,
) -> dict[str, Any]:
    # 이 리포트는 config, artifact 상태, live probe를 함께 담아
    # 배선 설정과 실제 서비스 reachability를 한 번에 확인하게 한다.
    settings = load_settings(root_dir)
    return {
        "generated_at": _iso_timestamp(),
        "app": {
            "app_id": settings.app_id,
            "app_label": settings.app_label,
            "active_pack_id": settings.active_pack_id,
            "active_pack_label": settings.active_pack_label,
            "product_label": settings.active_pack.product_label,
            "docs_language": settings.docs_language,
            "ocp_version": settings.ocp_version,
        },
        "runtime": {
            "llm_endpoint": settings.llm_endpoint,
            "llm_model": settings.llm_model,
            "embedding_base_url": settings.embedding_base_url,
            "embedding_model": settings.embedding_model,
            "qdrant_url": settings.qdrant_url,
            "qdrant_collection": settings.qdrant_collection,
            "reranker_enabled": bool(settings.reranker_enabled),
            "reranker_model": settings.reranker_model,
            "reranker_top_n": settings.reranker_top_n,
        },
        "artifacts": {
            "source_manifest": _path_status(settings.source_manifest_path),
            "source_catalog": _path_status(settings.source_catalog_path),
            "normalized_docs": _path_status(settings.normalized_docs_path),
            "chunks": _path_status(settings.chunks_path),
            "bm25_corpus": _path_status(settings.bm25_corpus_path),
            "chat_turns": _path_status(settings.chat_log_path),
            "answer_eval_report": _path_status(settings.answer_eval_report_path),
            "ragas_eval_report": _path_status(settings.ragas_eval_report_path),
            "retrieval_eval_report": _path_status(settings.retrieval_eval_report_path),
        },
        "probes": {
            "local_ui": _probe_local_ui(ui_base_url),
            "llm": _probe_llm(settings, sample=sample),
            "embedding": _probe_embedding(settings, sample=sample),
            "qdrant": _probe_qdrant(settings),
        },
        "reproducibility": {
            "session_strategy": "memory_only",
            "reproduction_strategy": "use chat_turns.jsonl with per-turn runtime snapshot",
            "canonical_entrypoints": [
                "play_book.cmd ui",
                "play_book.cmd ask",
                "play_book.cmd eval",
                "play_book.cmd ragas",
                "play_book.cmd runtime",
            ],
            "legacy_freeze": {
                "allow_new_run_part_scripts": False,
                "allow_new_top_level_shims": False,
                "legacy_entrypoints_removed": True,
                "functional_scripts_only": True,
            },
            "recent_turns": _read_recent_chat_turns(settings, limit=max(1, recent_turns)),
        },
    }


def write_runtime_report(
    root_dir: str | Path,
    *,
    output_path: str | Path | None = None,
    ui_base_url: str | None = "http://127.0.0.1:8765",
    recent_turns: int = 3,
    sample: bool = True,
) -> tuple[Path, dict[str, Any]]:
    settings = load_settings(root_dir)
    report = build_runtime_report(
        root_dir,
        ui_base_url=ui_base_url,
        recent_turns=recent_turns,
        sample=sample,
    )
    target = Path(output_path).resolve() if output_path else settings.runtime_report_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return target, report
