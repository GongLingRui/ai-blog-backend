"""
Test Comments API endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_article_comments(client: AsyncClient, test_article, test_comment):
    """Test getting comments for article"""
    response = await client.get(f"/api/v1/articles/{test_article.id}/comments")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_create_comment(client: AsyncClient, user_headers, test_article):
    """Test creating new comment"""
    response = await client.post(
        f"/api/v1/articles/{test_article.id}/comments",
        headers=user_headers,
        json={
            "content": "New test comment"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "New test comment"


@pytest.mark.asyncio
async def test_create_comment_unauthorized(client: AsyncClient, test_article):
    """Test creating comment without authentication"""
    response = await client.post(
        f"/api/v1/articles/{test_article.id}/comments",
        json={
            "content": "Test comment"
        }
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_comment_empty(client: AsyncClient, user_headers, test_article):
    """Test creating comment with empty content"""
    response = await client.post(
        f"/api/v1/articles/{test_article.id}/comments",
        headers=user_headers,
        json={
            "content": ""
        }
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_comment(client: AsyncClient, user_headers, test_comment):
    """Test updating comment"""
    response = await client.put(
        f"/api/v1/comments/{test_comment.id}",
        headers=user_headers,
        json={
            "content": "Updated comment content"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Updated comment content"


@pytest.mark.asyncio
async def test_delete_comment(client: AsyncClient, user_headers, test_comment):
    """Test deleting comment"""
    response = await client.delete(
        f"/api/v1/comments/{test_comment.id}",
        headers=user_headers
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_comment_replies(client: AsyncClient, test_article, test_comment, test_user):
    """Test getting comment replies"""
    # Create a reply first
    await client.post(
        f"/api/v1/articles/{test_article.id}/comments",
        headers={"Authorization": f"Bearer {user_headers['Authorization'].split(' ')[1]}"},
        json={
            "content": "This is a reply",
            "parent_id": test_comment.id
        }
    )

    response = await client.get(f"/api/v1/comments/{test_comment.id}/replies")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_like_comment(client: AsyncClient, user_headers, test_comment):
    """Test liking a comment"""
    response = await client.post(
        f"/api/v1/comments/{test_comment.id}/like",
        headers=user_headers
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_unlike_comment(client: AsyncClient, user_headers, test_comment):
    """Test unliking a comment"""
    response = await client.delete(
        f"/api/v1/comments/{test_comment.id}/like",
        headers=user_headers
    )

    assert response.status_code == 204 or response.status_code == 200
