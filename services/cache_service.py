"""
======================================================================

Institutional Quant Platform

Cache Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise cache management.

Responsibilities
----------------
• In-memory cache
• Thread safety
• TTL support
• Statistics
• Serialization
• Health Monitoring
• Runtime Metrics

======================================================================
"""

from __future__ import annotations

import json
import pickle
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock, RLock
from typing import Any

from core.services.base_service import BaseService

# ============================================================
# Exceptions
# ============================================================


class CacheServiceError(Exception):
    """Base cache exception."""


class CacheKeyNotFoundError(CacheServiceError):
    """Cache key does not exist."""


class CacheSerializationError(CacheServiceError):
    """Serialization failure."""


# ============================================================
# Cache Entry
# ============================================================


@dataclass(slots=True)
class CacheEntry:
    key: str

    value: Any

    created_at: float = field(default_factory=time.time)

    accessed_at: float = field(default_factory=time.time)

    ttl: int | None = None

    hits: int = 0

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def expired(self) -> bool:

        if self.ttl is None:
            return False

        return time.time() >= self.created_at + self.ttl

    def touch(self):

        self.hits += 1

        self.accessed_at = time.time()


# ============================================================
# Cache Service
# ============================================================


class CacheService(BaseService):
    """
    Enterprise cache manager.

    Thread-safe singleton.

    Supports

    • Memory cache
    • TTL
    • LRU
    • Statistics
    • Persistence
    """

    _instance = None

    _instance_lock = Lock()

    # --------------------------------------------------------

    def __new__(cls, *args, **kwargs):

        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        return cls._instance

    # --------------------------------------------------------

    def __init__(self, max_entries: int = 10000):

        if getattr(self, "_initialized", False):
            return

        super().__init__()

        self._cache = OrderedDict()

        self._lock = RLock()

        self._max_entries = max_entries

        self._enabled = True

        self._default_ttl = None

        self._hits = 0

        self._misses = 0

        self._evictions = 0

        self._writes = 0

        self._deletes = 0

        self._cleanups = 0

        self._initialized = True

        self._logger.info("CacheService initialized.")

    # =====================================================
    # Lifecycle
    # =====================================================

    def enable(self):

        self._enabled = True

    def disable(self):

        self._enabled = False

    def enabled(self):

        return self._enabled

    # =====================================================
    # Configuration
    # =====================================================

    def set_default_ttl(self, seconds: int | None):

        self._default_ttl = seconds

    def default_ttl(self):

        return self._default_ttl

    def capacity(self):

        return self._max_entries

    def size(self):

        return len(self._cache)

    def empty(self):

        return len(self._cache) == 0

    # =====================================================
    # Internal Helpers
    # =====================================================

    def _ensure_capacity(self):
        """
        LRU eviction.
        """

        while len(self._cache) > self._max_entries:
            key, entry = self._cache.popitem(last=False)

            self._notify_eviction(key, entry.value)

            self._evictions += 1

    def _cleanup_expired(self):
        """
        Remove expired keys.
        """

        expired = []

        for key, entry in self._cache.items():
            if entry.expired:
                expired.append(key)

        for key in expired:
            del self._cache[key]

        self._cleanups += len(expired)

    # =====================================================
    # BaseService
    # =====================================================

    def run(self):

        return self.statistics()

    # =====================================================
    # Core Cache Operations
    # =====================================================

    def put(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Store an item in cache.
        """

        if not self._enabled:
            return

        if ttl is None:
            ttl = self._default_ttl

        with self._lock:
            self._cleanup_expired()

            entry = CacheEntry(key=key, value=value, ttl=ttl, metadata=metadata or {})

            self._cache[key] = entry

            self._cache.move_to_end(key, last=True)

            self._writes += 1

            self._ensure_capacity()

    # -----------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve an item from cache.
        """

        if not self._enabled:
            return default

        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._misses += 1

                return default

            if entry.expired:
                del self._cache[key]

                self._misses += 1

                return default

            entry.touch()

            self._cache.move_to_end(key, last=True)

            self._hits += 1

            return entry.value

    # -----------------------------------------------------

    def require(self, key: str) -> Any:
        """
        Retrieve a required cache value.
        """

        value = self.get(key, default=None)

        if value is None:
            raise CacheKeyNotFoundError(f"'{key}' not found.")

        return value

    # -----------------------------------------------------

    def delete(self, key: str) -> bool:
        """
        Delete cache key.
        """

        with self._lock:
            if key not in self._cache:
                return False

            del self._cache[key]

            self._deletes += 1

            return True

    # -----------------------------------------------------

    def clear(self) -> None:
        """
        Clear cache.
        """

        with self._lock:
            self._cache.clear()

    # -----------------------------------------------------

    def contains(self, key: str) -> bool:

        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                return False

            if entry.expired:
                del self._cache[key]

                return False

            return True

    # -----------------------------------------------------

    def pop(self, key: str, default: Any = None) -> Any:
        """
        Remove and return cache value.
        """

        with self._lock:
            entry = self._cache.pop(key, None)

            if entry is None:
                return default

            return entry.value

    # -----------------------------------------------------

    def touch(self, key: str) -> bool:
        """
        Refresh access timestamp.
        """

        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                return False

            if entry.expired:
                del self._cache[key]

                return False

            entry.touch()

            self._cache.move_to_end(key, last=True)

            return True

    # -----------------------------------------------------

    def update(self, key: str, value: Any) -> bool:
        """
        Update existing cache entry.
        """

        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                return False

            if entry.expired:
                del self._cache[key]

                return False

            entry.value = value

            entry.touch()

            self._cache.move_to_end(key, last=True)

            return True

    # -----------------------------------------------------

    def get_or_create(
        self, key: str, factory: Callable[[], Any], ttl: int | None = None
    ) -> Any:
        """
        Return cached value or create it.
        """

        value = self.get(key, default=None)

        if value is not None:
            return value

        value = factory()

        self.put(key, value, ttl=ttl)

        return value

    # -----------------------------------------------------

    def keys(self) -> list[str]:

        with self._lock:
            self._cleanup_expired()

            return list(self._cache.keys())

    # -----------------------------------------------------

    def values(self) -> list[Any]:

        with self._lock:
            self._cleanup_expired()

            return [entry.value for entry in self._cache.values()]

    # -----------------------------------------------------

    def items(self) -> dict[str, Any]:

        with self._lock:
            self._cleanup_expired()

            return {key: entry.value for key, entry in self._cache.items()}

    # -----------------------------------------------------

    def __contains__(self, key: str) -> bool:

        return self.contains(key)

    def __getitem__(self, key: str) -> Any:

        return self.require(key)

    def __setitem__(self, key: str, value: Any) -> None:

        self.put(key, value)

    def __delitem__(self, key: str) -> None:

        self.delete(key)

    def __len__(self) -> int:

        return self.size()

    # =====================================================
    # Statistics
    # =====================================================

    @property
    def hits(self) -> int:

        return self._hits

    @property
    def misses(self) -> int:

        return self._misses

    @property
    def writes(self) -> int:

        return self._writes

    @property
    def deletes(self) -> int:

        return self._deletes

    @property
    def evictions(self) -> int:

        return self._evictions

    @property
    def cleanups(self) -> int:

        return self._cleanups

    @property
    def requests(self) -> int:

        return self._hits + self._misses

    @property
    def hit_ratio(self) -> float:

        requests = self.requests

        if requests == 0:
            return 0.0

        return self._hits / requests

    @property
    def miss_ratio(self) -> float:

        requests = self.requests

        if requests == 0:
            return 0.0

        return self._misses / requests

    # =====================================================
    # Statistics API
    # =====================================================

    def statistics(self) -> dict[str, Any]:
        """
        Cache statistics.
        """

        return {
            "enabled": self._enabled,
            "entries": len(self._cache),
            "capacity": self._max_entries,
            "utilization": (
                len(self._cache) / self._max_entries if self._max_entries else 0.0
            ),
            "hits": self._hits,
            "misses": self._misses,
            "requests": self.requests,
            "writes": self._writes,
            "deletes": self._deletes,
            "evictions": self._evictions,
            "cleanups": self._cleanups,
            "hit_ratio": round(self.hit_ratio, 4),
            "miss_ratio": round(self.miss_ratio, 4),
        }

    # =====================================================
    # Export
    # =====================================================

    def export_json(self, file: Path) -> Path:
        """
        Export cache contents as JSON.
        """

        payload = {}

        with self._lock:
            self._cleanup_expired()

            for key, entry in self._cache.items():
                payload[key] = {
                    "value": entry.value,
                    "created_at": entry.created_at,
                    "accessed_at": entry.accessed_at,
                    "ttl": entry.ttl,
                    "hits": entry.hits,
                    "metadata": entry.metadata,
                }

        file.parent.mkdir(parents=True, exist_ok=True)

        with file.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=4, default=str)

        return file

    # =====================================================
    # Pickle Export
    # =====================================================

    def save(self, file: Path) -> Path:
        """
        Persist cache.
        """

        file.parent.mkdir(parents=True, exist_ok=True)

        with file.open("wb") as handle:
            pickle.dump(self._cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        return file

    def load(self, file: Path) -> None:
        """
        Restore cache.
        """

        if not file.exists():
            raise FileNotFoundError(file)

        with file.open("rb") as handle:
            cache = pickle.load(handle)

        if not isinstance(cache, OrderedDict):
            raise CacheSerializationError("Invalid cache file.")

        with self._lock:
            self._cache = cache

    # =====================================================
    # Snapshot
    # =====================================================

    def snapshot(self) -> dict[str, Any]:
        """
        Return complete cache snapshot.
        """

        with self._lock:
            self._cleanup_expired()

            snapshot = {}

            for key, entry in self._cache.items():
                snapshot[key] = {
                    "value": entry.value,
                    "ttl": entry.ttl,
                    "hits": entry.hits,
                    "metadata": dict(entry.metadata),
                }

            return snapshot

    # =====================================================
    # Diagnostics
    # =====================================================

    def health(self) -> dict[str, Any]:
        """
        Cache health report.
        """

        utilization = len(self._cache) / self._max_entries

        status = "HEALTHY"

        if utilization >= 0.95:
            status = "CRITICAL"

        elif utilization >= 0.80:
            status = "WARNING"

        return {
            "status": status,
            "enabled": self._enabled,
            "entries": len(self._cache),
            "capacity": self._max_entries,
            "utilization": round(utilization, 4),
            "hit_ratio": round(self.hit_ratio, 4),
        }

    # =====================================================
    # Maintenance
    # =====================================================

    def compact(self) -> int:
        """
        Remove expired entries.
        """

        before = len(self._cache)

        with self._lock:
            self._cleanup_expired()

        return before - len(self._cache)

    def reset_statistics(self) -> None:
        """
        Reset counters.
        """

        self._hits = 0

        self._misses = 0

        self._writes = 0

        self._deletes = 0

        self._evictions = 0

        self._cleanups = 0

    # =====================================================
    # Batch Operations
    # =====================================================

    def put_many(self, entries: dict[str, Any], ttl: int | None = None) -> None:
        """
        Store multiple entries.
        """

        for key, value in entries.items():
            self.put(key, value, ttl=ttl)

    # -----------------------------------------------------

    def get_many(self, keys: list[str]) -> dict[str, Any]:
        """
        Retrieve multiple cache entries.
        """

        results: dict[str, Any] = {}

        for key in keys:
            value = self.get(key, default=None)

            if value is not None:
                results[key] = value

        return results

    # -----------------------------------------------------

    def delete_many(self, keys: list[str]) -> int:
        """
        Delete multiple cache entries.
        """

        deleted = 0

        for key in keys:
            if self.delete(key):
                deleted += 1

        return deleted

    # =====================================================
    # Namespace Support
    # =====================================================

    @staticmethod
    def namespace_key(namespace: str, key: str) -> str:

        return f"{namespace}:{key}"

    def put_namespace(
        self, namespace: str, key: str, value: Any, ttl: int | None = None
    ) -> None:

        self.put(self.namespace_key(namespace, key), value, ttl)

    def get_namespace(self, namespace: str, key: str, default: Any = None) -> Any:

        return self.get(self.namespace_key(namespace, key), default)

    def clear_namespace(self, namespace: str) -> int:
        """
        Remove an entire namespace.
        """

        prefix = f"{namespace}:"

        deleted = 0

        with self._lock:
            keys = [key for key in self._cache if key.startswith(prefix)]

            for key in keys:
                del self._cache[key]

                deleted += 1

        return deleted

    # =====================================================
    # Decorator
    # =====================================================

    def cached(self, ttl: int | None = None, namespace: str = "default"):
        """
        Cache decorator.
        """

        def decorator(function):

            def wrapper(*args, **kwargs):

                cache_key = (
                    f"{namespace}:"
                    f"{function.__module__}."
                    f"{function.__name__}:"
                    f"{args!r}:"
                    f"{kwargs!r}"
                )

                value = self.get(cache_key, default=None)

                if value is not None:
                    return value

                value = function(*args, **kwargs)

                self.put(cache_key, value, ttl)

                return value

            return wrapper

        return decorator

    # =====================================================
    # Warm Cache
    # =====================================================

    def warm(self, loader: Callable[[], dict[str, Any]], ttl: int | None = None) -> int:
        """
        Preload cache.
        """

        entries = loader()

        self.put_many(entries, ttl)

        return len(entries)

    # =====================================================
    # Memory Usage
    # =====================================================

    def estimated_memory_bytes(self) -> int:
        """
        Estimate cache memory footprint.
        """

        total = 0

        for entry in self._cache.values():
            try:
                total += len(pickle.dumps(entry, protocol=pickle.HIGHEST_PROTOCOL))

            except Exception:
                continue

        return total

    # =====================================================
    # Eviction Callback
    # =====================================================

    def register_eviction_callback(self, callback: Callable[[str, Any], None]) -> None:

        self._eviction_callback = callback

    def _notify_eviction(self, key: str, value: Any) -> None:

        callback = getattr(self, "_eviction_callback", None)

        if callback is not None:
            try:
                callback(key, value)

            except Exception:
                self._logger.exception("Eviction callback failed.")

    # =====================================================
    # Cache Event Hooks
    # =====================================================

    def register_put_hook(self, callback: Callable[[str, Any], None]) -> None:

        self._put_hook = callback

    def register_get_hook(self, callback: Callable[[str], None]) -> None:

        self._get_hook = callback

    def _fire_put_hook(self, key: str, value: Any) -> None:

        callback = getattr(self, "_put_hook", None)

        if callback:
            callback(key, value)

    def _fire_get_hook(self, key: str) -> None:

        callback = getattr(self, "_get_hook", None)

        if callback:
            callback(key)

    # =====================================================
    # Async API
    # =====================================================

    async def async_get(self, key: str, default: Any = None) -> Any:

        return self.get(key, default)

    async def async_put(self, key: str, value: Any, ttl: int | None = None) -> None:

        self.put(key, value, ttl)

    async def async_delete(self, key: str) -> bool:

        return self.delete(key)

    async def async_clear(self) -> None:

        self.clear()

    # =====================================================
    # Maintenance
    # =====================================================

    def cleanup(self) -> int:
        """
        Cleanup expired cache entries.
        """

        before = len(self._cache)

        with self._lock:
            self._cleanup_expired()

        removed = before - len(self._cache)

        self._logger.info("Removed %d expired cache entries.", removed)

        return removed

    def optimize(self) -> dict[str, Any]:
        """
        Perform cache optimization.
        """

        removed = self.cleanup()

        return {
            "removed": removed,
            "entries": len(self._cache),
            "memory_bytes": self.estimated_memory_bytes(),
            "utilization": len(self._cache) / self._max_entries,
        }

    # =====================================================
    # Validation
    # =====================================================

    def validate(self) -> bool:
        """
        Validate cache integrity.
        """

        with self._lock:
            for key, entry in self._cache.items():
                if key != entry.key:
                    return False

        return True

    # =====================================================
    # Lifecycle
    # =====================================================

    def startup(self) -> None:

        self.enable()

        self.cleanup()

        self._logger.info("Cache service started.")

    def shutdown(self) -> None:

        self.cleanup()

        self._logger.info("Cache service shutdown.")

    # =====================================================
    # Diagnostics
    # =====================================================

    def diagnostics(self) -> dict[str, Any]:
        """
        Full diagnostic report.
        """

        return {
            "statistics": self.statistics(),
            "health": self.health(),
            "memory_bytes": self.estimated_memory_bytes(),
            "integrity": self.validate(),
            "default_ttl": self._default_ttl,
            "enabled": self._enabled,
        }

    # =====================================================
    # String Representation
    # =====================================================

    def __iter__(self):

        with self._lock:
            self._cleanup_expired()

            return iter(self._cache.items())

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(entries={len(self)}, "
            f"capacity={self._max_entries}, "
            f"hit_ratio={self.hit_ratio:.2%})"
        )

    def __bool__(self) -> bool:

        return self._enabled


# ============================================================
# Global Singleton
# ============================================================

cache_service = CacheService()
