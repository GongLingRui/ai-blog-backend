"""
Test Article CRUD operations
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.article import (
    get_article,
    get_article_by_slug,
    get_articles,
    count_articles,
    create_article,
    update_article,
    delete_article,
    increment_view_count,
    get_trending_articles,
    get_related_articles
)
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.models.article import ArticleStatus


@pytest.mark.asyncio
async def test_get_article(db_session: AsyncSession, test_article):
    """Test getting article by ID"""
    article = await get_article(db_session, test_article.id)
    assert article is not None
    assert article.id == test_article.id
    assert article.title == test_article.title
    assert article.slug == test_article.slug


@pytest.mark.asyncio
async def test_get_article_with_relations(db_session: AsyncSession, test_article):
    """Test getting article with author, category, and tags"""
    article = await get_article(db_session, test_article.id)
    assert article is not None
    assert article.author is not None
    assert article.category is not None
    assert article.title == test_article.title


@pytest.mark.asyncio
async def test_get_article_by_slug(db_session: AsyncSession, test_article):
    """Test getting article by slug"""
    article = await get_article_by_slug(db_session, test_article.slug)
    assert article is not None
    assert article.slug == test_article.slug


@pytest.mark.asyncio
async def test_get_article_not_found(db_session: AsyncSession):
    """Test getting non-existent article"""
    article = await get_article(db_session, "non-existent-id")
    assert article is None


@pytest.mark.asyncio
async def test_create_article(db_session: AsyncSession, test_user, test_category):
    """Test creating new article"""
    article_in = ArticleCreate(
        title="New Test Article",
        content="This is the content of the new article",
        excerpt="Test excerpt",
        category_id=test_category.id,
        status=ArticleStatus.PUBLISHED,
        tags=["test", "example"]
    )
    article = await create_article(db_session, article_in, test_user.id)

    assert article.title == "New Test Article"
    assert article.slug == "new-test-article"
    assert article.author_id == test_user.id
    assert article.category_id == test_category.id
    assert article.status == ArticleStatus.PUBLISHED
    assert article.reading_time > 0


@pytest.mark.asyncio
async def test_create_article_with_duplicate_slug(db_session: AsyncSession, test_user, test_category, test_article):
    """Test creating article with duplicate title generates unique slug"""
    article_in = ArticleCreate(
        title=test_article.title,  # Same title
        content="Different content",
        excerpt="Different excerpt",
        category_id=test_category.id,
        status=ArticleStatus.PUBLISHED
    )
    article = await create_article(db_session, article_in, test_user.id)

    assert article.slug != test_article.slug
    assert article.slug.startswith("test-article-")


@pytest.mark.asyncio
async def test_update_article(db_session: AsyncSession, test_article):
    """Test updating article"""
    article_in = ArticleUpdate(
        title="Updated Title",
        content="Updated content"
    )
    updated_article = await update_article(db_session, test_article, article_in)

    assert updated_article.title == "Updated Title"
    assert updated_article.content == "Updated content"
    assert updated_article.slug == test_article.slug  # Unchanged


@pytest.mark.asyncio
async def test_delete_article(db_session: AsyncSession, test_article):
    """Test deleting article"""
    await delete_article(db_session, test_article)

    # Verify article is deleted
    article = await get_article(db_session, test_article.id)
    assert article is None


@pytest.mark.asyncio
async def test_increment_view_count(db_session: AsyncSession, test_article):
    """Test incrementing article view count"""
    initial_count = test_article.view_count

    new_count = await increment_view_count(db_session, test_article.id)

    assert new_count == initial_count + 1


@pytest.mark.asyncio
async def test_get_articles(db_session: AsyncSession, test_article):
    """Test getting list of articles"""
    articles = await get_articles(db_session, skip=0, limit=10)
    assert len(articles) >= 1
    assert test_article.id in [a.id for a in articles]


@pytest.mark.asyncio
async def test_get_articles_by_category(db_session: AsyncSession, test_article, test_category):
    """Test filtering articles by category"""
    articles = await get_articles(db_session, category_id=test_category.id)
    assert len(articles) >= 1
    assert all(a.category_id == test_category.id for a in articles)


@pytest.mark.asyncio
async def test_get_articles_by_author(db_session: AsyncSession, test_article, test_user):
    """Test filtering articles by author"""
    articles = await get_articles(db_session, author_id=test_user.id)
    assert len(articles) >= 1
    assert all(a.author_id == test_user.id for a in articles)


@pytest.mark.asyncio
async def test_search_articles(db_session: AsyncSession, test_article):
    """Test searching articles"""
    articles = await get_articles(db_session, search="Test")
    assert len(articles) >= 1
    assert test_article.id in [a.id for a in articles]


@pytest.mark.asyncio
async def test_count_articles(db_session: AsyncSession, test_article):
    """Test counting articles"""
    count = await count_articles(db_session)
    assert count >= 1


@pytest.mark.asyncio
async def test_get_trending_articles(db_session: AsyncSession, test_article):
    """Test getting trending articles"""
    # Increment view count to make it trending
    await increment_view_count(db_session, test_article.id)
    await increment_view_count(db_session, test_article.id)

    trending = await get_trending_articles(db_session, days=7, limit=10)
    assert len(trending) >= 1


@pytest.mark.asyncio
async def test_get_related_articles(db_session: AsyncSession, test_article, test_user, test_category):
    """Test getting related articles"""
    # Create another article in same category
    from app.schemas.article import ArticleCreate
    article_in = ArticleCreate(
        title="Related Article",
        content="Related content",
        excerpt="Related excerpt",
        category_id=test_category.id,
        status=ArticleStatus.PUBLISHED
    )
    related = await create_article(db_session, article_in, test_user.id)

    # Get related articles
    related_articles = await get_related_articles(db_session, test_article.id, limit=5)
    assert len(related_articles) >= 1
    assert related.id in [a.id for a in related_articles]


@pytest.mark.asyncio
async def test_article_status_filtering(db_session: AsyncSession, test_user, test_category):
    """Test filtering articles by status"""
    # Create draft article
    from app.schemas.article import ArticleCreate
    draft_in = ArticleCreate(
        title="Draft Article",
        content="Draft content",
        excerpt="Draft excerpt",
        category_id=test_category.id,
        status=ArticleStatus.DRAFT
    )
    draft = await create_article(db_session, draft_in, test_user.id)

    # Get only published articles
    published = await get_articles(db_session, status=ArticleStatus.PUBLISHED)
    assert draft.id not in [a.id for a in published]

    # Get only draft articles
    drafts = await get_articles(db_session, status=ArticleStatus.DRAFT)
    assert draft.id in [a.id for a in drafts]
