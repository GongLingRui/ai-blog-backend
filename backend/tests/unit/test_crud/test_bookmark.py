"""
Test Bookmark CRUD operations
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.bookmark import (
    get_bookmark,
    get_user_bookmarks,
    create_bookmark,
    delete_bookmark,
    is_bookmarked,
    count_bookmarks,
    get_article_bookmarks
)
from app.models.bookmark import Bookmark


@pytest.mark.asyncio
async def test_get_bookmark(db_session: AsyncSession, test_bookmark):
    """Test getting bookmark by ID"""
    bookmark = await get_bookmark(db_session, test_bookmark.id)
    assert bookmark is not None
    assert bookmark.id == test_bookmark.id
    assert bookmark.user_id == test_bookmark.user_id
    assert bookmark.article_id == test_bookmark.article_id


@pytest.mark.asyncio
async def test_get_bookmark_not_found(db_session: AsyncSession):
    """Test getting non-existent bookmark"""
    bookmark = await get_bookmark(db_session, "non-existent-id")
    assert bookmark is None


@pytest.mark.asyncio
async def test_create_bookmark(db_session: AsyncSession, test_user, test_article):
    """Test creating new bookmark"""
    bookmark = await create_bookmark(db_session, test_user.id, test_article.id)

    assert bookmark.user_id == test_user.id
    assert bookmark.article_id == test_article.id
    assert bookmark.id is not None


@pytest.mark.asyncio
async def test_delete_bookmark(db_session: AsyncSession, test_bookmark):
    """Test deleting bookmark"""
    await delete_bookmark(db_session, test_bookmark)

    # Verify bookmark is deleted
    bookmark = await get_bookmark(db_session, test_bookmark.id)
    assert bookmark is None


@pytest.mark.asyncio
async def test_get_user_bookmarks(db_session: AsyncSession, test_user, test_bookmark):
    """Test getting user's bookmarks"""
    bookmarks = await get_user_bookmarks(db_session, user_id=test_user.id)
    assert len(bookmarks) >= 1
    assert test_bookmark.id in [b.id for b in bookmarks]


@pytest.mark.asyncio
async def test_is_bookmarked(db_session: AsyncSession, test_user, test_article, test_bookmark):
    """Test checking if article is bookmarked"""
    is_bookmarked_result = await is_bookmarked(db_session, test_user.id, test_article.id)
    assert is_bookmarked_result is True


@pytest.mark.asyncio
async def test_is_not_bookmarked(db_session: AsyncSession, test_user, test_article):
    """Test checking if article is not bookmarked"""
    # Delete the test bookmark first
    bookmarks = await get_user_bookmarks(db_session, user_id=test_user.id)
    for bookmark in bookmarks:
        await db_session.delete(bookmark)
    await db_session.flush()

    is_bookmarked_result = await is_bookmarked(db_session, test_user.id, test_article.id)
    assert is_bookmarked_result is False


@pytest.mark.asyncio
async def test_count_bookmarks(db_session: AsyncSession, test_article):
    """Test counting bookmarks for article"""
    count = await count_bookmarks(db_session, article_id=test_article.id)
    assert count >= 1


@pytest.mark.asyncio
async def test_get_article_bookmarks(db_session: AsyncSession, test_article, test_bookmark):
    """Test getting all bookmarks for article"""
    bookmarks = await get_article_bookmarks(db_session, article_id=test_article.id)
    assert len(bookmarks) >= 1
    assert test_bookmark.id in [b.id for b in bookmarks]


@pytest.mark.asyncio
async def test_duplicate_bookmark(db_session: AsyncSession, test_user, test_article):
    """Test that duplicate bookmarks are handled"""
    # Create first bookmark
    await create_bookmark(db_session, test_user.id, test_article.id)

    # Try to create duplicate
    duplicate = await create_bookmark(db_session, test_user.id, test_article.id)

    # Should either return existing or fail gracefully
    # This depends on implementation
    assert duplicate is not None


@pytest.mark.asyncio
async def test_bookmark_with_pagination(db_session: AsyncSession, test_user, test_article):
    """Test getting bookmarks with pagination"""
    # Create multiple bookmarks
    for i in range(5):
        # Create additional articles for testing
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
        await create_bookmark(db_session, test_user.id, article.id)

    # Get with pagination
    bookmarks = await get_user_bookmarks(db_session, user_id=test_user.id, skip=0, limit=3)
    assert len(bookmarks) == 3
