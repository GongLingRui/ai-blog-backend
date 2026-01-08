"""
Test Bookmarks API endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_user_bookmarks(client: AsyncClient, user_headers, test_bookmark):
    """Test getting user's bookmarks"""
    response = await client.get(
        "/api/v1/bookmarks",
        headers=user_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_create_bookmark(client: AsyncClient, user_headers, test_article):
    """Test creating new bookmark"""
    response = await client.post(
        f"/api/v1/articles/{test_article.id}/bookmark",
        headers=user_headers
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_duplicate_bookmark(client: AsyncClient, user_headers, test_bookmark):
    """Test creating duplicate bookmark"""
    response = await client.post(
        f"/api/v1/articles/{test_bookmark.article_id}/bookmark",
        headers=user_headers
    )

    # Should either return 200 (already bookmarked) or 409 (conflict)
    assert response.status_code in [200, 201, 409]


@pytest.mark.asyncio
async def test_create_bookmark_unauthorized(client: AsyncClient, test_article):
    """Test creating bookmark without authentication"""
    response = await client.post(
        f"/api/v1/articles/{test_article.id}/bookmark"
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_bookmark(client: AsyncClient, user_headers, test_bookmark):
    """Test deleting bookmark"""
    response = await client.delete(
        f"/api/v1/articles/{test_bookmark.article_id}/bookmark",
        headers=user_headers
    )

    assert response.status_code == 204 or response.status_code == 200


@pytest.mark.asyncio
async def test_check_is_bookmarked(client: AsyncClient, user_headers, test_article, test_bookmark):
    """Test checking if article is bookmarked"""
    response = await client.get(
        f"/api/v1/articles/{test_article.id}/bookmark",
        headers=user_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "is_bookmarked" in data


@pytest.mark.asyncio
async def test_get_bookmarks_with_pagination(client: AsyncClient, user_headers):
    """Test getting bookmarks with pagination"""
    response = await client.get(
        "/api/v1/bookmarks?page=1&page_size=10",
        headers=user_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) <= 10


@pytest.mark.asyncio
async def test_toggle_bookmark(client: AsyncClient, user_headers, test_article):
    """Test toggling bookmark"""
    # First toggle - should create
    response = await client.post(
        f"/api/v1/articles/{test_article.id}/bookmark/toggle",
        headers=user_headers
    )

    assert response.status_code == 200

    # Second toggle - should remove
    response = await client.post(
        f"/api/v1/articles/{test_article.id}/bookmark/toggle",
        headers=user_headers
    )

    assert response.status_code == 200
