"""
Test Articles API endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_articles(client: AsyncClient, test_article):
    """Test getting list of articles"""
    response = await client.get("/api/v1/articles")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_articles_with_pagination(client: AsyncClient):
    """Test getting articles with pagination"""
    response = await client.get("/api/v1/articles?page=1&page_size=10")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 10


@pytest.mark.asyncio
async def test_get_articles_with_search(client: AsyncClient, test_article):
    """Test searching articles"""
    response = await client.get(f"/api/v1/articles?search={test_article.title}")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_article_by_id(client: AsyncClient, test_article):
    """Test getting article by ID"""
    response = await client.get(f"/api/v1/articles/{test_article.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_article.id
    assert data["title"] == test_article.title


@pytest.mark.asyncio
async def test_get_article_by_slug(client: AsyncClient, test_article):
    """Test getting article by slug"""
    response = await client.get(f"/api/v1/articles/slug/{test_article.slug}")

    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == test_article.slug


@pytest.mark.asyncio
async def test_get_article_not_found(client: AsyncClient):
    """Test getting non-existent article"""
    response = await client.get("/api/v1/articles/non-existent-id")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_article(client: AsyncClient, user_headers, test_category):
    """Test creating new article"""
    response = await client.post(
        "/api/v1/articles",
        headers=user_headers,
        json={
            "title": "New Test Article",
            "content": "This is the content",
            "excerpt": "Test excerpt",
            "category_id": test_category.id,
            "status": "published",
            "tags": ["test", "new"]
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Test Article"
    assert data["slug"] == "new-test-article"


@pytest.mark.asyncio
async def test_create_article_unauthorized(client: AsyncClient, test_category):
    """Test creating article without authentication"""
    response = await client.post(
        "/api/v1/articles",
        json={
            "title": "New Article",
            "content": "Content",
            "category_id": test_category.id
        }
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_article(client: AsyncClient, user_headers, test_article):
    """Test updating article"""
    response = await client.put(
        f"/api/v1/articles/{test_article.id}",
        headers=user_headers,
        json={
            "title": "Updated Title",
            "content": "Updated content"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_update_article_unauthorized(client: AsyncClient, test_article):
    """Test updating article without authentication"""
    response = await client.put(
        f"/api/v1/articles/{test_article.id}",
        json={
            "title": "Updated Title"
        }
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_article(client: AsyncClient, user_headers, test_article):
    """Test deleting article"""
    response = await client.delete(
        f"/api/v1/articles/{test_article.id}",
        headers=user_headers
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_article_unauthorized(client: AsyncClient, test_article):
    """Test deleting article without authentication"""
    response = await client.delete(f"/api/v1/articles/{test_article.id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_increment_article_view(client: AsyncClient, test_article):
    """Test incrementing article view count"""
    response = await client.post(f"/api/v1/articles/{test_article.id}/view")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_trending_articles(client: AsyncClient):
    """Test getting trending articles"""
    response = await client.get("/api/v1/articles/trending?days=7&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_related_articles(client: AsyncClient, test_article):
    """Test getting related articles"""
    response = await client.get(f"/api/v1/articles/{test_article.id}/related")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_filter_articles_by_category(client: AsyncClient, test_article, test_category):
    """Test filtering articles by category"""
    response = await client.get(f"/api/v1/articles?category_id={test_category.id}")

    assert response.status_code == 200
    data = response.json()
    assert all(a["category_id"] == test_category.id for a in data["items"])


@pytest.mark.asyncio
async def test_filter_articles_by_author(client: AsyncClient, test_article, test_user):
    """Test filtering articles by author"""
    response = await client.get(f"/api/v1/articles?author_id={test_user.id}")

    assert response.status_code == 200
    data = response.json()
    assert all(a["author"]["id"] == test_user.id for a in data["items"])


@pytest.mark.asyncio
async def test_filter_articles_by_tag(client: AsyncClient):
    """Test filtering articles by tag"""
    response = await client.get("/api/v1/articles?tag_id=some-tag-id")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_sort_articles(client: AsyncClient):
    """Test sorting articles"""
    response = await client.get("/api/v1/articles?sort=view_count&order=desc")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_get_articles_by_status(client: AsyncClient, user_headers):
    """Test getting articles by status (auth required)"""
    response = await client.get(
        "/api/v1/articles?status=draft",
        headers=user_headers
    )

    assert response.status_code == 200
