"""
유사 질의 응답 캐시. 같은 의미의 질문이 들어오면 LLM 호출 없이 바로 응답.
cosine similarity 기반으로 매칭하되, 주제가 다른 질문끼리 섞이지 않도록
간단한 토큰/엔티티 가드도 같이 본다.

Redis 연동:
- set_redis(client) 호출 시 기존 캐시를 Redis에서 복원한다.
- store() 시 Redis에도 함께 저장한다 (pickle 직렬화).
- clear() 시 Redis 키도 삭제한다.
- Redis 없이도 기존 인메모리 모드로 정상 동작한다.
"""
import asyncio
import hashlib
import pickle
import time
import re
import numpy as np
from collections import OrderedDict
from dataclasses import dataclass
from typing import Optional

from src.config import CACHE_SIMILARITY_THRESHOLD, CACHE_MAX_SIZE

_REDIS_KEY_PREFIX = "ocp-rag:cache:"
_REDIS_CACHE_TTL = 7 * 24 * 3600  # 7일


@dataclass
class CacheEntry:
    """캐시 항목"""
    query: str
    query_embedding: np.ndarray
    response: str
    context: str  # RAG에서 사용된 context
    sources: list[dict]
    endpoint_key: str
    model: str
    created_at: float
    hit_count: int = 0


class SemanticCache:
    """의미 기반 응답 캐시

    처음에 threshold=0.92로 했다가 다른 질문인데 캐시 히트되는 문제가 있어서 0.95로 올림.

    Redis 연동:
    - 인메모리 행렬이 기본 (cosine similarity 계산은 in-process)
    - Redis는 재시작 후 캐시 복원을 위한 영속 계층으로 사용
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
        self._redis = None

    def set_redis(self, redis_client) -> None:
        """Redis 클라이언트 주입 + 기존 캐시 복원"""
        self._redis = redis_client
        self._load_from_redis()

    def _load_from_redis(self):
        """Redis에 저장된 캐시 항목을 인메모리로 복원"""
        if not self._redis:
            return
        try:
            pattern = f"{_REDIS_KEY_PREFIX}*"
            keys = self._redis.keys(pattern)
            loaded = 0
            for key in keys:
                raw = self._redis.get(key)
                if not raw:
                    continue
                entry: CacheEntry = pickle.loads(raw)
                if len(self._cache) < self.max_size:
                    self._cache[entry.query] = entry
                    loaded += 1
            if loaded:
                self._rebuild_matrix()
                import logging
                logging.getLogger(__name__).info("Redis에서 캐시 항목 %d개 복원", loaded)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning("Redis 캐시 복원 실패: %s", e)

    def _query_redis_key(self, query: str) -> str:
        digest = hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]
        return f"{_REDIS_KEY_PREFIX}{digest}"

    def _save_entry_to_redis(self, entry: CacheEntry):
        if not self._redis:
            return
        try:
            key = self._query_redis_key(entry.query)
            self._redis.set(key, pickle.dumps(entry), ex=_REDIS_CACHE_TTL)
        except Exception:
            pass

    def _delete_entry_from_redis(self, query: str):
        if not self._redis:
            return
        try:
            self._redis.delete(self._query_redis_key(query))
        except Exception:
            pass

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

    _NUMBER_RE = re.compile(r"\d+")

    @classmethod
    def _extract_numbers(cls, text: str) -> list[str]:
        return cls._NUMBER_RE.findall(text)

    @classmethod
    def _is_cache_compatible(cls, query: str, cached_query: str) -> bool:
        # 숫자가 다르면 캐시 미스 ("3줄 요약" vs "4줄 요약")
        if cls._extract_numbers(query) != cls._extract_numbers(cached_query):
            return False

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

    async def async_store(
        self,
        query: str,
        query_embedding: np.ndarray,
        response: str,
        context: str,
        sources: list[dict],
        endpoint_key: str,
        model: str,
    ):
        """스레드 안전한 캐시 저장"""
        async with self._lock:
            self.store(query, query_embedding, response, context, sources, endpoint_key, model)

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
        sources: list[dict],
        endpoint_key: str,
        model: str,
    ):
        """응답을 캐시에 저장"""
        # 이미 유사한 항목이 있으면 업데이트
        existing = self.lookup(query, query_embedding)
        if existing:
            existing.response = response
            existing.context = context
            existing.sources = sources
            existing.endpoint_key = endpoint_key
            existing.model = model
            self._save_entry_to_redis(existing)
            return

        entry = CacheEntry(
            query=query,
            query_embedding=query_embedding.flatten().astype(np.float32),
            response=response,
            context=context,
            sources=sources,
            endpoint_key=endpoint_key,
            model=model,
            created_at=time.time(),
        )

        # LRU: 최대 크기 초과 시 가장 오래된 항목 제거
        if len(self._cache) >= self.max_size:
            evicted_query, _ = self._cache.popitem(last=False)
            self._delete_entry_from_redis(evicted_query)

        self._cache[query] = entry
        self._rebuild_matrix()
        self._save_entry_to_redis(entry)

    def clear(self):
        """캐시 초기화"""
        if self._redis:
            try:
                keys = self._redis.keys(f"{_REDIS_KEY_PREFIX}*")
                if keys:
                    self._redis.delete(*keys)
            except Exception:
                pass
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
