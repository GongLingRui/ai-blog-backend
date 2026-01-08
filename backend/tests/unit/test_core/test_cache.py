"""
Test Redis cache functions
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.cache import (
    cache_key,
    cache_get,
    cache_set,
    cache_delete,
    cache_delete_pattern,
    CacheManager,
    cache
)


@pytest.mark.asyncio
async def test_cache_key_generation():
    """Test cache key generation from arguments"""
    key = cache_key("user", "123", active=True)
    assert key == "user:123:active=True"


@pytest.mark.asyncio
async def test_cache_key_with_kwargs():
    """Test cache key with keyword arguments"""
    key = cache_key("articles", page=1, limit=10)
    assert "articles" in key
    assert "page=1" in key
    assert "limit=10" in key


@pytest.mark.asyncio
async def test_cache_set():
    """Test setting value in cache"""
    with patch.object(cache, 'aconnect') as mock_connect:
        mock_redis = AsyncMock()
        mock_connect.return_value = mock_redis

        await cache_set("test_key", {"data": "value"}, ttl=60)

        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "test_key"
        assert call_args[0][1] == 60


@pytest.mark.asyncio
async def test_cache_get_hit():
    """Test getting value from cache (cache hit)"""
    with patch.object(cache, 'aconnect') as mock_connect:
        mock_redis = AsyncMock()
        mock_redis.get.return_value = '{"data": "value"}'
        mock_connect.return_value = mock_redis

        result = await cache_get("test_key")

        assert result == {"data": "value"}
        mock_redis.get.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_cache_get_miss():
    """Test getting value from cache (cache miss)"""
    with patch.object(cache, 'aconnect') as mock_connect:
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None
        mock_connect.return_value = mock_redis

        result = await cache_get("test_key")

        assert result is None


@pytest.mark.asyncio
async def test_cache_delete():
    """Test deleting key from cache"""
    with patch.object(cache, 'aconnect') as mock_connect:
        mock_redis = AsyncMock()
        mock_connect.return_value = mock_redis

        await cache_delete("test_key")

        mock_redis.delete.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_cache_delete_pattern():
    """Test deleting keys matching pattern"""
    with patch.object(cache, 'aconnect') as mock_connect:
        mock_redis = AsyncMock()
        mock_redis.keys.return_value = ["key1", "key2", "key3"]
        mock_connect.return_value = mock_redis

        await cache_delete_pattern("test:*")

        mock_redis.keys.assert_called_once_with("test:*")
        mock_redis.delete.assert_called_once_with("key1", "key2", "key3")


@pytest.mark.asyncio
async def test_cache_manager_set_user():
    """Test CacheManager set user"""
    with patch('app.core.cache.cache_set') as mock_set:
        await CacheManager.set_user("user123", {"username": "test"})

        mock_set.assert_called_once()
        call_args = mock_set.call_args
        assert "user123" in str(call_args)


@pytest.mark.asyncio
async def test_cache_manager_get_user():
    """Test CacheManager get user"""
    with patch('app.core.cache.cache_get') as mock_get:
        mock_get.return_value = {"username": "test"}

        result = await CacheManager.get_user("user123")

        assert result == {"username": "test"}
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_cache_manager_invalidate_user():
    """Test CacheManager invalidate user"""
    with patch('app.core.cache.cache_delete') as mock_delete:
        await CacheManager.invalidate_user("user123")

        mock_delete.assert_called_once()


@pytest.mark.asyncio
async def test_cache_manager_set_article():
    """Test CacheManager set article"""
    with patch('app.core.cache.cache_set') as mock_set:
        await CacheManager.set_article("article123", {"title": "Test"})

        mock_set.assert_called_once()


@pytest.mark.asyncio
async def test_cache_manager_get_article():
    """Test CacheManager get article"""
    with patch('app.core.cache.cache_get') as mock_get:
        mock_get.return_value = {"title": "Test"}

        result = await CacheManager.get_article("article123")

        assert result == {"title": "Test"}
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_cache_manager_invalidate_article():
    """Test CacheManager invalidate article"""
    with patch('app.core.cache.cache_delete') as mock_delete, \
         patch('app.core.cache.cache_delete_pattern') as mock_delete_pattern:
        await CacheManager.invalidate_article("article123")

        # Should delete article and articles list
        assert mock_delete.called or mock_delete_pattern.called


@pytest.mark.asyncio
async def test_cache_manager_set_articles_list():
    """Test CacheManager set articles list"""
    with patch('app.core.cache.cache_set') as mock_set:
        articles = [{"id": "1"}, {"id": "2"}]
        await CacheManager.set_articles_list(1, 10, articles)

        mock_set.assert_called_once()


@pytest.mark.asyncio
async def test_cache_manager_invalidate_articles_list():
    """Test CacheManager invalidate articles list"""
    with patch('app.core.cache.cache_delete_pattern') as mock_delete:
        await CacheManager.invalidate_articles_list()

        mock_delete.assert_called_once_with("articles:*")


@pytest.mark.asyncio
async def test_cache_manager_set_tag():
    """Test CacheManager set tag"""
    with patch('app.core.cache.cache_set') as mock_set:
        await CacheManager.set_tag("tag123", {"name": "tech"})

        mock_set.assert_called_once()


@pytest.mark.asyncio
async def test_cache_manager_invalidate_tags():
    """Test CacheManager invalidate tags"""
    with patch('app.core.cache.cache_delete_pattern') as mock_delete:
        await CacheManager.invalidate_tags()

        # Should be called twice for different patterns
        assert mock_delete.call_count >= 1


@pytest.mark.asyncio
async def test_cache_manager_set_category():
    """Test CacheManager set category"""
    with patch('app.core.cache.cache_set') as mock_set:
        await CacheManager.set_category("cat123", {"name": "Tech"})

        mock_set.assert_called_once()


@pytest.mark.asyncio
async def test_cache_manager_invalidate_categories():
    """Test CacheManager invalidate categories"""
    with patch('app.core.cache.cache_delete_pattern') as mock_delete:
        await CacheManager.invalidate_categories()

        # Should be called twice for different patterns
        assert mock_delete.call_count >= 1


@pytest.mark.asyncio
async def test_cache_set_with_complex_data():
    """Test caching complex data structures"""
    with patch.object(cache, 'aconnect') as mock_connect:
        mock_redis = AsyncMock()
        mock_connect.return_value = mock_redis

        complex_data = {
            "user": {"id": "123", "name": "Test"},
            "articles": [
                {"id": "1", "title": "Article 1"},
                {"id": "2", "title": "Article 2"}
            ]
        }

        await cache_set("complex_key", complex_data, ttl=300)

        mock_redis.setex.assert_called_once()


@pytest.mark.asyncio
async def test_cache_error_handling():
    """Test cache error handling"""
    with patch.object(cache, 'aconnect') as mock_connect:
        mock_redis = AsyncMock()
        mock_redis.get.side_effect = Exception("Redis connection error")
        mock_connect.return_value = mock_redis

        # Should not raise exception, return None
        result = await cache_get("test_key")
        assert result is None


@pytest.mark.asyncio
async def test_cache_with_special_characters():
    """Test caching with special characters in data"""
    with.patch.object(cache, 'aconnect') as mock_connect:
        mock_redis = AsyncMock()
        mock_connect.return_value = mock_redis

        data = {"text": "Special chars: @#$%^&*()_+-={}[]|\\:\";:'<>?,./"}
        await cache_set("special_key", data, ttl=60)

        mock_redis.setex.assert_called_once()
