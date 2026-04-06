from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=4)
def load_sentence_model(
    model_name: str,
    device: str = "auto",
) -> SentenceTransformer:
    normalized_device = (device or "auto").strip().lower()
    if normalized_device in {"", "auto"}:
        return SentenceTransformer(model_name)
    return SentenceTransformer(model_name, device=normalized_device)
