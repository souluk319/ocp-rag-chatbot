from __future__ import annotations

from collections.abc import Callable
from typing import Iterable

import requests

from ocp_rag.shared.settings import Settings

from .sentence_model import load_sentence_model


class EmbeddingClient:
    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.embedding_base_url
        self.model = settings.embedding_model
        self.api_key = settings.embedding_api_key
        self.batch_size = settings.embedding_batch_size
        self.timeout = max(settings.request_timeout_seconds, 120)

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            return {}
        if " " in self.api_key.strip():
            return {"Authorization": self.api_key.strip()}
        return {"Authorization": f"Bearer {self.api_key}"}

    def _candidate_models(self) -> list[str]:
        candidates: list[str] = [self.model]
        for candidate in (
            self.model.rsplit("/", 1)[-1],
            self.model.lower(),
            self.model.lower().rsplit("/", 1)[-1],
        ):
            if candidate and candidate not in candidates:
                candidates.append(candidate)
        return candidates

    def _request_remote_embeddings(self, batch: list[str]) -> list[list[float]]:
        last_error: Exception | None = None
        for model_name in self._candidate_models():
            try:
                response = requests.post(
                    f"{self.base_url}/embeddings",
                    json={"model": model_name, "input": batch},
                    headers=self._headers(),
                    timeout=self.timeout,
                )
                response.raise_for_status()
                payload = response.json()
                data = payload.get("data")
                if not isinstance(data, list):
                    raise ValueError("Embedding response is missing a 'data' list")
                vectors = [item["embedding"] for item in data]
                return [list(map(float, vector)) for vector in vectors]
            except Exception as exc:  # noqa: BLE001
                last_error = exc
        raise RuntimeError(
            f"Failed to fetch embeddings from {self.base_url} using model '{self.model}'"
        ) from last_error

    def _request_local_embeddings(self, batch: list[str]) -> list[list[float]]:
        model = load_sentence_model(self.model)
        vectors = model.encode(
            batch,
            normalize_embeddings=False,
            show_progress_bar=False,
        )
        if hasattr(vectors, "tolist"):
            vectors = vectors.tolist()
        return [list(map(float, vector)) for vector in vectors]

    def _request_embeddings(
        self,
        batch: list[str],
        *,
        prefer_local: bool = False,
    ) -> list[list[float]]:
        if prefer_local:
            try:
                return self._request_local_embeddings(batch)
            except Exception:  # noqa: BLE001
                pass
        if self.base_url:
            try:
                return self._request_remote_embeddings(batch)
            except Exception:  # noqa: BLE001
                pass
        return self._request_local_embeddings(batch)

    def embed_texts(
        self,
        texts: Iterable[str],
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> list[list[float]]:
        items = list(texts)
        vectors: list[list[float]] = []
        total_batches = (len(items) + self.batch_size - 1) // self.batch_size
        prefer_local = len(items) == 1
        for start in range(0, len(items), self.batch_size):
            batch = items[start : start + self.batch_size]
            vectors.extend(self._request_embeddings(batch, prefer_local=prefer_local))
            if progress_callback is not None:
                completed_batches = (start // self.batch_size) + 1
                progress_callback(completed_batches, total_batches)
        return vectors
