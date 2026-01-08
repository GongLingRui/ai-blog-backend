"""
Test Like CRUD operations
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.like import (
    get_like,
    get_user_likes,
    create_like,
    delete_like,
    is_liked,
    count_likes,
    get_article_likes,
    toggle_like
)
from app.models.like import Like


@pytest.mark.asyncio
async def test_get_like(db_session: AsyncSession, test_like):
    """Test getting like by ID"""
    like = await get_like(db_session, test_like.id)
    assert like is not None
    assert like.id == test_like.id
    assert like.user_id == test_like.user_id
    assert like.article_id == test_like.article_id


@pytest.mark.asyncio
async def test_get_like_not_found(db_session: AsyncSession):
    """Test getting non-existent like"""
    like = await get_like(db_session, "non-existent-id")
    assert like is None


@pytest.mark.asyncio
async def test_create_like(db_session: AsyncSession, test_user, test_article):
    """Test creating new like"""
    like = await create_like(db_session, test_user.id, test_article.id)

    assert like.user_id == test_user.id
    assert like.article_id == test_article.id
    assert like.id is not None


@pytest.mark.asyncio
async def test_delete_like(db_session: AsyncSession, test_like):
    """Test deleting like"""
    await delete_like(db_session, test_like)

    # Verify like is deleted
    like = await get_like(db_session, test_like.id)
    assert like is None


@pytest.mark.asyncio
async def test_get_user_likes(db_session: AsyncSession, test_user, test_like):
    """Test getting user's likes"""
    likes = await get_user_likes(db_session, user_id=test_user.id)
    assert len(likes) >= 1
    assert test_like.id in [l.id for l in likes]


@pytest.mark.asyncio
async def test_is_liked(db_session: AsyncSession, test_user, test_article, test_like):
    """Test checking if article is liked"""
    is_liked_result = await is_liked(db_session, test_user.id, test_article.id)
    assert is_liked_result is True


@pytest.mark.asyncio
async def test_is_not_liked(db_session: AsyncSession, test_user, test_article):
    """Test checking if article is not liked"""
    # Delete the test like first
    likes = await get_user_likes(db_session, user_id=test_user.id)
    for like in likes:
        await db_session.delete(like)
    await db_session.flush()

    is_liked_result = await is_liked(db_session, test_user.id, test_article.id)
    assert is_liked_result is False


@pytest.mark.asyncio
async def test_count_likes(db_session: AsyncSession, test_article):
    """Test counting likes for article"""
    count = await count_likes(db_session, article_id=test_article.id)
    assert count >= 1


@pytest.mark.asyncio
async def test_get_article_likes(db_session: AsyncSession, test_article, test_like):
    """Test getting all likes for article"""
    likes = await get_article_likes(db_session, article_id=test_article.id)
    assert len(likes) >= 1
    assert test_like.id in [l.id for l in likes]


@pytest.mark.asyncio
async def test_toggle_like_create(db_session: AsyncSession, test_user, test_article):
    """Test toggling like to create"""
    # Ensure no like exists
    likes = await get_user_likes(db_session, user_id=test_user.id)
    for like in likes:
        if like.article_id == test_article.id:
            await db_session.delete(like)
    await db_session.flush()

    # Toggle to create
    like = await toggle_like(db_session, test_user.id, test_article.id)
    assert like is not None
    assert like.user_id == test_user.id
    assert like.article_id == test_article.id


@pytest.mark.asyncio
async def test_toggle_like_delete(db_session: AsyncSession, test_user, test_article, test_like):
    """Test toggling like to delete"""
    # Toggle to delete
    result = await toggle_like(db_session, test_user.id, test_article.id)

    # Verify like is deleted
    is_liked_result = await is_liked(db_session, test_user.id, test_article.id)
    assert is_liked_result is False


@pytest.mark.asyncio
async def test_duplicate_like(db_session: AsyncSession, test_user, test_article):
    """Test that duplicate likes are handled"""
    # Create first like
    await create_like(db_session, test_user.id, test_article.id)

    # Try to create duplicate
    duplicate = await create_like(db_session, test_user.id, test_article.id)

    # Should either return existing or fail gracefully
    assert duplicate is not None


@pytest.mark.asyncio
async def test_like_with_pagination(db_session: AsyncSession, test_user, test_article):
    """Test getting likes with pagination"""
    # Create multiple articles and likes
    for i in range(5):
        from app.crud.article import create_article
        from app.schemas.article import ArticleCreate
        from app.models.article import ArticleStatus

        article_in = ArticleCreate(
            title=f"Test Article {i}",
            content=f"Content {i}",
            excerpt=f"Excerpt {i}",
            category_id=test_article.category_id,
            status=ArticleStatus.PUBLISHED
        )
        article = await create_article(db_session, article_in, test_user.id)
        await create_like(db_session, test_user.id, article.id)

    # Get with pagination
    likes = await get_user_likes(db_session, user_id=test_user.id, skip=0, limit=3)
    assert len(likes) == 3
