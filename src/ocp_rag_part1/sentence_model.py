from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=4)
def load_sentence_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)
