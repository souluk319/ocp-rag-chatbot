"""
유사 질의 응답 캐시. 같은 의미의 질문이 들어오면 LLM 호출 없이 바로 응답.
cosine similarity 기반으로 매칭하되, 주제가 다른 질문끼리 섞이지 않도록
간단한 토큰/엔티티 가드도 같이 본다.
"""
import asyncio
import time
import re
import numpy as np
from collections import OrderedDict
from dataclasses import dataclass
from typing import Optional

from src.config import CACHE_SIMILARITY_THRESHOLD, CACHE_MAX_SIZE


@dataclass
class CacheEntry:
    """캐시 항목"""
    query: str
    query_embedding: np.ndarray
    response: str
    context: str  # RAG에서 사용된 context
    created_at: float
    hit_count: int = 0


class SemanticCache:
    """의미 기반 응답 캐시

    처음에 threshold=0.92로 했다가 다른 질문인데 캐시 히트되는 문제가 있어서 0.95로 올림.
    """
    # 향후 개선: 쿼리 길이에 따른 동적 threshold 조절 (현재 0.95 고정)

    def __init__(
        self,
        threshold: float = CACHE_SIMILARITY_THRESHOLD,
        max_size: int = CACHE_MAX_SIZE,
    ):
        self.threshold = threshold
        self.max_size = max_size
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._embeddings: Optional[np.ndarray] = None  # lookup 때마다 재계산하면 느려서 행렬로 캐싱
        self._keys: list[str] = []
        self._lock = asyncio.Lock()  # 동시 요청 시 캐시 상태 보호

    _GENERIC_TOKENS = {
        "개요", "설명", "간략", "간단", "소개", "기본", "핵심",
        "대해", "대해서", "관해", "알려줘", "설명해봐", "해봐",
    }
    _ENTITY_TERMS = {
        "openshift": {"오픈시프트", "openshift", "ocp"},
        "kubernetes": {"쿠버네티스", "kubernetes", "k8s"},
    }

    @classmethod
    def _tokenize(cls, text: str) -> set[str]:
        parts = re.findall(r"[a-z0-9\-]+|[가-힣]{2,}", text.lower())
        return set(parts)

    @classmethod
    def _detect_entity(cls, tokens: set[str]) -> str | None:
        for entity, terms in cls._ENTITY_TERMS.items():
            if tokens & terms:
                return entity
        return None

    @classmethod
    def _is_cache_compatible(cls, query: str, cached_query: str) -> bool:
        query_tokens = cls._tokenize(query)
        cached_tokens = cls._tokenize(cached_query)

        query_entity = cls._detect_entity(query_tokens)
        cached_entity = cls._detect_entity(cached_tokens)
        if query_entity and cached_entity and query_entity != cached_entity:
            return False

        informative_query = query_tokens - cls._GENERIC_TOKENS
        informative_cached = cached_tokens - cls._GENERIC_TOKENS
        if informative_query and informative_cached:
            if not (informative_query & informative_cached):
                return False

        return True

    def _rebuild_matrix(self):
        """캐시 임베딩 행렬 재구성"""
        if not self._cache:
            self._embeddings = None
            self._keys = []
            return
        self._keys = list(self._cache.keys())
        self._embeddings = np.array(
            [self._cache[k].query_embedding for k in self._keys],
            dtype=np.float32,
        )

    async def async_lookup(self, query: str, query_embedding: np.ndarray) -> Optional[CacheEntry]:
        """스레드 안전한 캐시 조회"""
        async with self._lock:
            return self.lookup(query, query_embedding)

    async def async_store(self, query: str, query_embedding: np.ndarray, response: str, context: str):
        """스레드 안전한 캐시 저장"""
        async with self._lock:
            self.store(query, query_embedding, response, context)

    def lookup(self, query: str, query_embedding: np.ndarray) -> Optional[CacheEntry]:
        """캐시 조회 - 유사한 질의가 있으면 반환"""
        if self._embeddings is None or len(self._embeddings) == 0:
            return None

        # cosine similarity 계산
        query_vector = query_embedding.flatten().astype(np.float32)
        norm_q = np.linalg.norm(query_vector)
        if norm_q == 0:
            return None
        query_normalized = query_vector / norm_q

        norms = np.linalg.norm(self._embeddings, axis=1)
        norms = np.where(norms == 0, 1, norms)
        cache_normalized = self._embeddings / norms[:, np.newaxis]

        similarities = cache_normalized @ query_normalized

        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]

        if best_score >= self.threshold:
            key = self._keys[best_idx]
            entry = self._cache[key]
            if not self._is_cache_compatible(query, entry.query):
                return None
            entry.hit_count += 1
            self._cache.move_to_end(key)
            return entry

        return None

    def store(
        self,
        query: str,
        query_embedding: np.ndarray,
        response: str,
        context: str,
    ):
        """응답을 캐시에 저장"""
        # 이미 유사한 항목이 있으면 업데이트
        existing = self.lookup(query, query_embedding)
        if existing:
            existing.response = response
            existing.context = context
            return

        entry = CacheEntry(
            query=query,
            query_embedding=query_embedding.flatten().astype(np.float32),
            response=response,
            context=context,
            created_at=time.time(),
        )

        # LRU: 최대 크기 초과 시 가장 오래된 항목 제거
        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)

        self._cache[query] = entry
        self._rebuild_matrix()

    def clear(self):
        """캐시 초기화"""
        self._cache.clear()
        self._embeddings = None
        self._keys = []

    def stats(self) -> dict:
        """캐시 상태"""
        total_hits = sum(e.hit_count for e in self._cache.values())
        return {
            "cached_queries": len(self._cache),
            "max_size": self.max_size,
            "total_hits": total_hits,
            "threshold": self.threshold,
        }
