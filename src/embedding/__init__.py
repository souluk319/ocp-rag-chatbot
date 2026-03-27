"""sentence-transformers로 텍스트→벡터 변환. 같은 텍스트 중복 계산 방지용 LRU 캐시 포함.

Redis 연동:
- set_redis(client) 호출 시 Redis를 L2 캐시로 사용한다.
- 로컬 LRU(L1) → Redis(L2) → 모델 계산 순으로 조회한다.
- Redis 없이도 기존 인메모리 LRU만으로 정상 동작한다.
"""
import hashlib
import numpy as np
from typing import Optional
from collections import OrderedDict

from src.config import EMBEDDING_MODEL, EMBEDDING_DIM

_REDIS_KEY_PREFIX = "ocp-rag:emb:"


class EmbeddingEngine:
    """모델 로딩은 lazy하게 처리 (첫 호출 시점에 로드)"""

    def __init__(self, model_name: str = EMBEDDING_MODEL, cache_size: int = 5000):
        self.model_name = model_name
        self.dim = EMBEDDING_DIM
        self._model = None  # lazy loading
        self._cache: OrderedDict[str, np.ndarray] = OrderedDict()
        self._cache_size = cache_size
        self._redis = None

    def set_redis(self, redis_client) -> None:
        """Redis 클라이언트 주입 (L2 캐시로 사용)"""
        self._redis = redis_client

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

    def _redis_get(self, key: str) -> Optional[np.ndarray]:
        """Redis L2 캐시 조회 (numpy bytes → ndarray)"""
        if not self._redis:
            return None
        try:
            raw = self._redis.get(f"{_REDIS_KEY_PREFIX}{key}")
            if raw:
                return np.frombuffer(raw, dtype=np.float32).copy()
        except Exception:
            pass
        return None

    def _redis_set(self, key: str, vector: np.ndarray):
        """numpy ndarray → Redis L2 캐시 저장"""
        if not self._redis:
            return
        try:
            self._redis.set(f"{_REDIS_KEY_PREFIX}{key}", vector.astype(np.float32).tobytes())
        except Exception:
            pass

    def _l1_put(self, key: str, vector: np.ndarray):
        """로컬 LRU(L1) 저장"""
        self._cache[key] = vector
        if len(self._cache) > self._cache_size:
            self._cache.popitem(last=False)

    def embed(self, text: str) -> np.ndarray:
        """단일 텍스트 임베딩 (L1 → L2 → 모델 계산 순으로 조회)"""
        key = self._text_hash(text)

        # L1 히트
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]

        # L2(Redis) 히트
        vec = self._redis_get(key)
        if vec is not None:
            self._l1_put(key, vec)
            return vec

        # 캐시 미스 → 임베딩 계산
        vector = self.model.encode(text, normalize_embeddings=True)
        vector = np.array(vector, dtype=np.float32)

        self._l1_put(key, vector)
        self._redis_set(key, vector)

        return vector

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """배치 임베딩 — 캐시에 없는 것만 모아서 한번에 인코딩

        처음에 개별 embed() 루프 돌렸는데 100개 넘으면 눈에 띄게 느려서
        배치 처리로 바꿈. sentence-transformers가 내부적으로 배치 최적화 해줌.
        """
        results = [None] * len(texts)
        uncached_indices = []
        uncached_texts = []

        # L1 확인, L2(Redis) 확인
        for i, text in enumerate(texts):
            key = self._text_hash(text)
            if key in self._cache:
                self._cache.move_to_end(key)
                results[i] = self._cache[key]
            else:
                vec = self._redis_get(key)
                if vec is not None:
                    self._l1_put(key, vec)
                    results[i] = vec
                else:
                    uncached_indices.append(i)
                    uncached_texts.append(text)

        # 캐시에 없는 것만 배치 인코딩
        if uncached_texts:
            vectors = self.model.encode(uncached_texts, normalize_embeddings=True)
            vectors = np.array(vectors, dtype=np.float32)
            for idx, text, vec in zip(uncached_indices, uncached_texts, vectors):
                key = self._text_hash(text)
                self._l1_put(key, vec)
                self._redis_set(key, vec)
                results[idx] = vec

        return np.array(results, dtype=np.float32)

    def cache_stats(self) -> dict:
        """캐시 상태 정보"""
        return {
            "cached_items": len(self._cache),
            "max_size": self._cache_size,
        }
