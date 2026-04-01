from __future__ import annotations

import time
from collections import OrderedDict
from threading import Lock
from typing import Generic, TypeVar


T = TypeVar("T")


class TtlLruCache(Generic[T]):
    def __init__(self, *, max_items: int, ttl_seconds: int) -> None:
        self.max_items = int(max_items)
        self.ttl_seconds = int(ttl_seconds)
        self.disabled = self.max_items <= 0 or self.ttl_seconds <= 0
        self._store: OrderedDict[str, tuple[float, T]] = OrderedDict()
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
        self._writes = 0
        self._evictions = 0

    def _prune_expired(self) -> None:
        if self.disabled:
            self._store.clear()
            return
        now = time.time()
        expired_keys = [
            key for key, (expires_at, _) in self._store.items() if expires_at <= now
        ]
        for key in expired_keys:
            self._store.pop(key, None)

    def get(self, key: str) -> T | None:
        with self._lock:
            if self.disabled:
                self._misses += 1
                return None
            self._prune_expired()
            entry = self._store.get(key)
            if entry is None:
                self._misses += 1
                return None
            expires_at, value = entry
            if expires_at <= time.time():
                self._store.pop(key, None)
                self._misses += 1
                return None
            self._store.move_to_end(key)
            self._hits += 1
            return value

    def set(self, key: str, value: T) -> None:
        with self._lock:
            if self.disabled:
                return
            self._prune_expired()
            expires_at = time.time() + self.ttl_seconds
            if key in self._store:
                self._store.pop(key, None)
            self._store[key] = (expires_at, value)
            self._store.move_to_end(key)
            self._writes += 1
            while len(self._store) > self.max_items:
                self._store.popitem(last=False)
                self._evictions += 1

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def stats(self) -> dict[str, int]:
        with self._lock:
            self._prune_expired()
            return {
                "max_items": self.max_items,
                "ttl_seconds": self.ttl_seconds,
                "disabled": int(self.disabled),
                "entries": len(self._store),
                "hits": self._hits,
                "misses": self._misses,
                "writes": self._writes,
                "evictions": self._evictions,
            }
