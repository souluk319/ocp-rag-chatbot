"""sentence-transformers로 텍스트→벡터 변환. 같은 텍스트 중복 계산 방지용 LRU 캐시 포함."""
import hashlib
import numpy as np
from typing import Optional
from collections import OrderedDict

from src.config import EMBEDDING_MODEL, EMBEDDING_DIM


class EmbeddingEngine:
    """모델 로딩은 lazy하게 처리 (첫 호출 시점에 로드)"""

    def __init__(self, model_name: str = EMBEDDING_MODEL, cache_size: int = 5000):
        self.model_name = model_name
        self.dim = EMBEDDING_DIM
        self._model = None  # lazy loading
        self._cache: OrderedDict[str, np.ndarray] = OrderedDict()
        self._cache_size = cache_size

    @property
    def model(self):
        """모델 lazy loading - 첫 호출 시에만 로드"""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def _text_hash(self, text: str) -> str:
        """텍스트의 해시값 생성 (캐시 키)
        sha256 전체 쓰기엔 과한데 md5는 충돌 위험 있어서 sha256[:16]으로 타협
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    def embed(self, text: str) -> np.ndarray:
        """단일 텍스트 임베딩 (캐시 적용)"""
        key = self._text_hash(text)

        # 캐시 히트
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]

        # 캐시 미스 → 임베딩 계산
        vector = self.model.encode(text, normalize_embeddings=True)
        vector = np.array(vector, dtype=np.float32)

        # 캐시 저장 (LRU)
        self._cache[key] = vector
        if len(self._cache) > self._cache_size:
            self._cache.popitem(last=False)

        return vector

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """배치 임베딩 — 캐시에 없는 것만 모아서 한번에 인코딩

        처음에 개별 embed() 루프 돌렸는데 100개 넘으면 눈에 띄게 느려서
        배치 처리로 바꿈. sentence-transformers가 내부적으로 배치 최적화 해줌.
        """
        results = [None] * len(texts)
        uncached_indices = []
        uncached_texts = []

        # 캐시 확인
        for i, text in enumerate(texts):
            key = self._text_hash(text)
            if key in self._cache:
                self._cache.move_to_end(key)
                results[i] = self._cache[key]
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)

        # 캐시에 없는 것만 배치 인코딩
        if uncached_texts:
            vectors = self.model.encode(uncached_texts, normalize_embeddings=True)
            vectors = np.array(vectors, dtype=np.float32)
            for idx, text, vec in zip(uncached_indices, uncached_texts, vectors):
                key = self._text_hash(text)
                self._cache[key] = vec
                if len(self._cache) > self._cache_size:
                    self._cache.popitem(last=False)
                results[idx] = vec

        return np.array(results, dtype=np.float32)

    def cache_stats(self) -> dict:
        """캐시 상태 정보"""
        return {
            "cached_items": len(self._cache),
            "max_size": self._cache_size,
        }
