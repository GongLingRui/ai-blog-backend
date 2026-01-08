"""
Article CRUD Operations
"""
from typing import Optional, List
from sqlalchemy import select, and_, or_, desc, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.article import Article, ArticleTag, ArticleStatus
from app.models.tag import Tag
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.core.utils import generate_slug, calculate_reading_time, generate_unique_slug


async def get_article(db: AsyncSession, article_id: str) -> Optional[Article]:
    """Get article by ID"""
    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.category),
            selectinload(Article.tags),
        )
        .where(Article.id == article_id)
    )
    return result.scalar_one_or_none()


async def get_article_by_slug(db: AsyncSession, slug: str) -> Optional[Article]:
    """Get article by slug"""
    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.category),
            selectinload(Article.tags),
        )
        .where(Article.slug == slug)
    )
    return result.scalar_one_or_none()


async def get_articles(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    status: str = ArticleStatus.PUBLISHED,
    category_id: Optional[str] = None,
    tag_id: Optional[str] = None,
    author_id: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = "published_at",
    order: str = "desc",
) -> List[Article]:
    """Get list of articles with filters"""
    query = (
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.category),
            selectinload(Article.tags),
        )
        .where(Article.status == status)
    )

    if category_id:
        query = query.where(Article.category_id == category_id)

    if author_id:
        query = query.where(Article.author_id == author_id)

    if tag_id:
        query = query.join(Article.tags).where(Tag.id == tag_id)

    if search:
        query = query.where(
            or_(
                Article.title.ilike(f"%{search}%"),
                Article.content.ilike(f"%{search}%"),
                Article.excerpt.ilike(f"%{search}%"),
            )
        )

    # Sorting
    sort_column = getattr(Article, sort, Article.published_at)
    if order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def count_articles(
    db: AsyncSession,
    status: str = ArticleStatus.PUBLISHED,
    category_id: Optional[str] = None,
    tag_id: Optional[str] = None,
    author_id: Optional[str] = None,
    search: Optional[str] = None,
) -> int:
    """Count articles with filters"""
    from sqlalchemy import func

    query = select(func.count(Article.id)).where(Article.status == status)

    if category_id:
        query = query.where(Article.category_id == category_id)

    if author_id:
        query = query.where(Article.author_id == author_id)

    if tag_id:
        query = query.join(Article.tags).where(Tag.id == tag_id)

    if search:
        query = query.where(
            or_(
                Article.title.ilike(f"%{search}%"),
                Article.content.ilike(f"%{search}%"),
            )
        )

    result = await db.execute(query)
    return result.scalar() or 0


async def create_article(
    db: AsyncSession,
    article_in: ArticleCreate,
    author_id: str,
) -> Article:
    """Create new article"""
    import uuid

    # Generate unique slug
    existing_articles = await db.execute(
        select(Article.slug).where(Article.slug.ilike(f"{generate_slug(article_in.title)}%"))
    )
    existing_slugs = [row[0] for row in existing_articles.fetchall()]
    slug = generate_unique_slug(article_in.title, existing_slugs)

    article = Article(
        id=str(uuid.uuid4()),
        title=article_in.title,
        slug=slug,
        content=article_in.content,
        excerpt=article_in.excerpt,
        cover_image_url=article_in.cover_image_url,
        author_id=author_id,
        category_id=article_in.category_id,
        status=article_in.status,
        reading_time=calculate_reading_time(article_in.content),
    )

    db.add(article)
    await db.flush()

    # Add tags
    if article_in.tags:
        await _add_tags_to_article(db, article, article_in.tags)

    await db.refresh(article)
    return await get_article(db, article.id)


async def update_article(
    db: AsyncSession,
    article: Article,
    article_in: ArticleUpdate,
) -> Article:
    """Update article"""
    update_data = article_in.model_dump(exclude_unset=True, exclude={"tags"})

    for field, value in update_data.items():
        setattr(article, field, value)

    # Recalculate reading time if content changed
    if "content" in update_data:
        article.reading_time = calculate_reading_time(article.content)

    # Update tags if provided
    if article_in.tags is not None:
        await _update_article_tags(db, article, article_in.tags)

    await db.flush()
    await db.refresh(article)
    return await get_article(db, article.id)


async def delete_article(db: AsyncSession, article: Article) -> None:
    """Delete article"""
    await db.delete(article)
    await db.flush()


async def increment_view_count(db: AsyncSession, article_id: str) -> int:
    """Increment article view count"""
    from sqlalchemy import update

    await db.execute(
        update(Article)
        .where(Article.id == article_id)
        .values(view_count=Article.view_count + 1)
    )
    await db.flush()

    # Get updated count
    article = await get_article(db, article_id)
    return article.view_count if article else 0


async def get_trending_articles(
    db: AsyncSession,
    days: int = 7,
    limit: int = 10,
) -> List[Article]:
    """Get trending articles (most viewed in last N days)"""
    from datetime import datetime, timedelta
    from sqlalchemy import desc

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.category),
            selectinload(Article.tags),
        )
        .where(Article.status == ArticleStatus.PUBLISHED)
        .where(Article.published_at >= cutoff_date)
        .order_by(desc(Article.view_count))
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_related_articles(
    db: AsyncSession,
    article_id: str,
    limit: int = 5,
) -> List[Article]:
    """Get related articles based on tags and category"""
    article = await get_article(db, article_id)
    if not article:
        return []

    # Get articles with same category or tags
    query = (
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.category),
            selectinload(Article.tags),
        )
        .where(Article.id != article_id)
        .where(Article.status == ArticleStatus.PUBLISHED)
    )

    # Filter by category or tags
    conditions = []
    if article.category_id:
        conditions.append(Article.category_id == article.category_id)
    if article.tags:
        tag_ids = [tag.id for tag in article.tags]
        conditions.append(Article.tags.any(Tag.id.in_(tag_ids)))

    if conditions:
        query = query.where(or_(*conditions))

    result = await db.execute(query.order_by(desc(Article.view_count)).limit(limit))
    return list(result.scalars().all())


async def _add_tags_to_article(db: AsyncSession, article: Article, tag_names: List[str]) -> None:
    """Add tags to article"""
    import uuid

    for tag_name in tag_names:
        # Get or create tag
        tag = await db.execute(select(Tag).where(Tag.name == tag_name))
        tag = tag.scalar_one_or_none()

        if not tag:
            slug = generate_slug(tag_name)
            tag = Tag(id=str(uuid.uuid4()), name=tag_name, slug=slug)
            db.add(tag)
            await db.flush()

        # Create article-tag association
        article_tag = ArticleTag(
            id=str(uuid.uuid4()), article_id=article.id, tag_id=tag.id
        )
        db.add(article_tag)

    await db.flush()


async def _update_article_tags(
    db: AsyncSession,
    article: Article,
    tag_names: List[str],
) -> None:
    """Update article tags (replace all)"""
    import uuid

    # Delete existing associations
    await db.execute(
        select(ArticleTag)
        .where(ArticleTag.article_id == article.id)
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(
        delete(ArticleTag).where(ArticleTag.article_id == article.id)
    )
    await db.flush()

    # Add new tags
    await _add_tags_to_article(db, article, tag_names)


