"""
Redis Cache Module
"""
import json
import logging
from typing import Optional, Any, Callable
from functools import wraps
from datetime import timedelta

import redis
from redis import Redis
from redis.asyncio import Redis as AsyncRedis

from app.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache manager"""

    def __init__(self):
        self._redis: Optional[Redis] = None
        self._async_redis: Optional[AsyncRedis] = None

    def connect(self) -> Redis:
        """Get synchronous Redis connection"""
        if self._redis is None:
            self._redis = Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                max_connections=50,
            )
        return self._redis

    async def aconnect(self) -> AsyncRedis:
        """Get asynchronous Redis connection"""
        if self._async_redis is None:
            self._async_redis = AsyncRedis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                max_connections=50,
            )
        return self._async_redis

    async def disconnect(self):
        """Close Redis connections"""
        if self._async_redis:
            await self._async_redis.close()
        if self._redis:
            self._redis.close()


# Global cache instance
cache = RedisCache()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
    return ":".join(key_parts)


def cached(
    ttl: int = 300,
    key_prefix: str = "",
    key_func: Optional[Callable] = None,
):
    """
    Cache decorator for async functions

    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Prefix for cache keys
        key_func: Custom function to generate cache key
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key_value = key_func(*args, **kwargs)
            else:
                cache_key_value = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"

            # Try to get from cache
            try:
                redis_client = await cache.aconnect()
                cached_value = await redis_client.get(cache_key_value)

                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key_value}")
                    return json.loads(cached_value)
            except Exception as e:
                logger.warning(f"Cache get error: {e}")

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            try:
                redis_client = await cache.aconnect()
                await redis_client.setex(
                    cache_key_value,
                    ttl,
                    json.dumps(result, default=str),
                )
                logger.debug(f"Cache set: {cache_key_value}, TTL: {ttl}s")
            except Exception as e:
                logger.warning(f"Cache set error: {e}")

            return result

        return wrapper

    return decorator


def invalidate_cache(pattern: str):
    """
    Invalidate cache keys matching pattern

    Args:
        pattern: Redis key pattern (e.g., "user:*")
    """

    async def _invalidate():
        try:
            redis_client = await cache.aconnect()
            keys = await redis_client.keys(pattern)

            if keys:
                await redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache keys matching: {pattern}")
        except Exception as e:
            logger.warning(f"Cache invalidation error: {e}")

    return _invalidate


def cache_set(key: str, value: Any, ttl: int = 300):
    """Set value in cache"""

    async def _set():
        try:
            redis_client = await cache.aconnect()
            await redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str),
            )
        except Exception as e:
            logger.warning(f"Cache set error: {e}")

    return _set()


async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        redis_client = await cache.aconnect()
        value = await redis_client.get(key)

        if value is not None:
            return json.loads(value)

        return None
    except Exception as e:
        logger.warning(f"Cache get error: {e}")
        return None


async def cache_delete(key: str):
    """Delete key from cache"""
    try:
        redis_client = await cache.aconnect()
        await redis_client.delete(key)
        logger.debug(f"Cache delete: {key}")
    except Exception as e:
        logger.warning(f"Cache delete error: {e}")


async def cache_delete_pattern(pattern: str):
    """Delete all keys matching pattern"""
    try:
        redis_client = await cache.aconnect()
        keys = await redis_client.keys(pattern)

        if keys:
            await redis_client.delete(*keys)
            logger.info(f"Deleted {len(keys)} cache keys matching: {pattern}")
    except Exception as e:
        logger.warning(f"Cache pattern delete error: {e}")


class CacheManager:
    """High-level cache manager"""

    @staticmethod
    async def get_user(user_id: str) -> Optional[dict]:
        """Get cached user data"""
        return await cache_get(f"user:{user_id}")

    @staticmethod
    async def set_user(user_id: str, user_data: dict, ttl: int = 3600):
        """Cache user data"""
        await cache_set(f"user:{user_id}", user_data, ttl)

    @staticmethod
    async def invalidate_user(user_id: str):
        """Invalidate user cache"""
        await cache_delete(f"user:{user_id}")

    @staticmethod
    async def get_article(article_id: str) -> Optional[dict]:
        """Get cached article data"""
        return await cache_get(f"article:{article_id}")

    @staticmethod
    async def set_article(article_id: str, article_data: dict, ttl: int = 1800):
        """Cache article data"""
        await cache_set(f"article:{article_id}", article_data, ttl)

    @staticmethod
    async def invalidate_article(article_id: str):
        """Invalidate article cache"""
        await cache_delete(f"article:{article_id}")
        # Also invalidate article list cache
        await cache_delete_pattern("articles:*")

    @staticmethod
    async def get_articles_list(page: int, page_size: int, **filters) -> Optional[list]:
        """Get cached articles list"""
        cache_key = f"articles:{page}:{page_size}:{cache_key(**filters)}"
        return await cache_get(cache_key)

    @staticmethod
    async def set_articles_list(
        page: int, page_size: int, articles: list, ttl: int = 300, **filters
    ):
        """Cache articles list"""
        cache_key = f"articles:{page}:{page_size}:{cache_key(**filters)}"
        await cache_set(cache_key, articles, ttl)

    @staticmethod
    async def invalidate_articles_list():
        """Invalidate all articles list cache"""
        await cache_delete_pattern("articles:*")

    @staticmethod
    async def get_tag(tag_id: str) -> Optional[dict]:
        """Get cached tag data"""
        return await cache_get(f"tag:{tag_id}")

    @staticmethod
    async def set_tag(tag_id: str, tag_data: dict, ttl: int = 3600):
        """Cache tag data"""
        await cache_set(f"tag:{tag_id}", tag_data, ttl)

    @staticmethod
    async def invalidate_tags():
        """Invalidate all tags cache"""
        await cache_delete_pattern("tags:*")
        await cache_delete_pattern("tag:*")

    @staticmethod
    async def get_category(category_id: str) -> Optional[dict]:
        """Get cached category data"""
        return await cache_get(f"category:{category_id}")

    @staticmethod
    async def set_category(category_id: str, category_data: dict, ttl: int = 3600):
        """Cache category data"""
        await cache_set(f"category:{category_id}", category_data, ttl)

    @staticmethod
    async def invalidate_categories():
        """Invalidate all categories cache"""
        await cache_delete_pattern("categories:*")
        await cache_delete_pattern("category:*")


# Export cache manager
cache_manager = CacheManager()
