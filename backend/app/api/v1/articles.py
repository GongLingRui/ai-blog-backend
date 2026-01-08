"""
Articles API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.article import (
    get_article,
    get_article_by_slug,
    get_articles,
    count_articles,
    create_article,
    update_article,
    delete_article as delete_article_crud,
    increment_view_count,
    get_trending_articles,
    get_related_articles,
)
from app.schemas.article import (
    ArticleResponse,
    ArticleListItem,
    ArticleCreate,
    ArticleUpdate,
)
from app.schemas.common import PaginationMeta
from app.middlewares.auth import get_current_user, get_current_author

router = APIRouter()


@router.get("")
async def get_articles_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = "published",
    category_id: str | None = None,
    tag_id: str | None = None,
    author_id: str | None = None,
    search: str | None = None,
    sort: str = "published_at",
    order: str = "desc",
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of articles with filters and pagination
    """
    skip = (page - 1) * page_size

    articles = await get_articles(
        db,
        skip=skip,
        limit=page_size,
        status=status,
        category_id=category_id,
        tag_id=tag_id,
        author_id=author_id,
        search=search,
        sort=sort,
        order=order,
    )

    total = await count_articles(
        db,
        status=status,
        category_id=category_id,
        tag_id=tag_id,
        author_id=author_id,
        search=search,
    )

    article_list = [ArticleListItem.model_validate(a) for a in articles]

    return {
        "success": True,
        "data": article_list,
        "pagination": PaginationMeta.create(total, page, page_size).model_dump(),
    }


@router.get("/trending")
async def get_trending_articles_endpoint(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Get trending articles
    """
    articles = await get_trending_articles(db, days=days, limit=limit)
    return {
        "success": True,
        "data": [ArticleListItem.model_validate(a) for a in articles],
    }


@router.get("/{article_id}")
async def get_article_by_id_endpoint(
    article_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get article by ID
    """
    article = await get_article(db, article_id)

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    return {"success": True, "data": ArticleResponse.model_validate(article)}


@router.get("/slug/{slug}")
async def get_article_by_slug_endpoint(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get article by slug
    """
    article = await get_article_by_slug(db, slug)

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    return {"success": True, "data": ArticleResponse.model_validate(article)}


@router.post("", response_model=ArticleResponse)
async def create_article_endpoint(
    data: ArticleCreate,
    current_user = Depends(get_current_author),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new article
    """
    article = await create_article(db, data, author_id=current_user.id)

    return ArticleResponse.model_validate(article)


@router.put("/{article_id}")
async def update_article_endpoint(
    article_id: str,
    data: ArticleUpdate,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an article
    """
    article = await get_article(db, article_id)

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    # Check ownership or admin
    if article.author_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this article",
        )

    updated_article = await update_article(db, article, data)

    return {
        "success": True,
        "data": ArticleResponse.model_validate(updated_article),
    }


@router.delete("/{article_id}")
async def delete_article_endpoint(
    article_id: str,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an article
    """
    article = await get_article(db, article_id)

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    # Check ownership or admin
    if article.author_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this article",
        )

    await delete_article_crud(db, article)

    return {"success": True, "message": "Article deleted successfully"}


@router.post("/{article_id}/view")
async def increment_view_count_endpoint(
    article_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Increment article view count
    """
    view_count = await increment_view_count(db, article_id)

    return {
        "success": True,
        "data": {"view_count": view_count},
    }


@router.get("/{article_id}/related")
async def get_related_articles_endpoint(
    article_id: str,
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """
    Get related articles
    """
    articles = await get_related_articles(db, article_id, limit=limit)

    return {
        "success": True,
        "data": [ArticleListItem.model_validate(a) for a in articles],
    }
