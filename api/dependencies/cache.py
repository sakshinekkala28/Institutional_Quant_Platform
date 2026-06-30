"""
====================================================================
Institutional Quant Platform

Cache Dependencies

Author : Institutional Quant Platform

Purpose
-------
FastAPI dependency providers for caching services.

Provides

• Cache Manager
• Redis Client
• In-Memory Cache
• TTL Manager
• Cache Statistics
• Cache Invalidation
• Cache Warming
• Cache Health

Used By

• Portfolio Router
• Signal Router
• Risk Router
• Execution Router
• Monitoring Router

====================================================================
"""

from __future__ import annotations

from functools import lru_cache

from cache.cache_manager import (
    CacheManager,
)

from cache.redis_cache import (
    RedisCache,
)

from cache.memory_cache import (
    MemoryCache,
)

from cache.ttl_manager import (
    TTLManager,
)

from cache.cache_statistics import (
    CacheStatistics,
)

from cache.cache_invalidator import (
    CacheInvalidator,
)

from cache.cache_warmer import (
    CacheWarmer,
)


# ==========================================================
# CACHE MANAGER
# ==========================================================


@lru_cache
def get_cache(

) -> CacheManager:
    """
    Primary cache manager.
    """

    return CacheManager()


# ==========================================================
# REDIS
# ==========================================================


@lru_cache
def get_redis(

) -> RedisCache:
    """
    Redis cache.
    """

    return RedisCache()


# ==========================================================
# MEMORY CACHE
# ==========================================================


@lru_cache
def get_memory_cache(

) -> MemoryCache:
    """
    Local memory cache.
    """

    return MemoryCache()


# ==========================================================
# TTL MANAGER
# ==========================================================


@lru_cache
def get_ttl_manager(

) -> TTLManager:
    """
    TTL manager.
    """

    return TTLManager()


# ==========================================================
# CACHE STATISTICS
# ==========================================================


@lru_cache
def get_cache_statistics(

) -> CacheStatistics:
    """
    Cache statistics.
    """

    return CacheStatistics()


# ==========================================================
# CACHE INVALIDATOR
# ==========================================================


@lru_cache
def get_cache_invalidator(

) -> CacheInvalidator:
    """
    Cache invalidator.
    """

    return CacheInvalidator()


# ==========================================================
# CACHE WARMER
# ==========================================================


@lru_cache
def get_cache_warmer(

) -> CacheWarmer:
    """
    Cache warming service.
    """

    return CacheWarmer()


# ==========================================================
# CACHE HEALTH
# ==========================================================


def cache_health(

) -> dict:
    """
    Cache dependency health.
    """

    return {

        "engine": "CacheManager",

        "status": "healthy",

        "singleton": True,

    }


# ==========================================================
# CACHE SUMMARY
# ==========================================================


def cache_summary(

) -> dict:
    """
    Cache services summary.
    """

    return {

        "services": [

            "CacheManager",

            "RedisCache",

            "MemoryCache",

            "TTLManager",

            "CacheStatistics",

            "CacheInvalidator",

            "CacheWarmer",

        ],

        "count": 7,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "get_cache",

    "get_redis",

    "get_memory_cache",

    "get_ttl_manager",

    "get_cache_statistics",

    "get_cache_invalidator",

    "get_cache_warmer",

    "cache_health",

    "cache_summary",

]