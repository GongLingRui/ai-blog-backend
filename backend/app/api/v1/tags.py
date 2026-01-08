"""
Tags API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middlewares.auth import get_current_user, get_current_admin
from app.models.user import User
from app.crud.tag import (
    get_tag,
    get_tag_by_name,
    get_tag_by_slug,
    get_tags,
    count_tags,
    search_tags,
    create_tag,
    update_tag,
)
from app.crud.article import get_articles, count_articles as count_articles_crud
from app.schemas.tag import TagResponse, TagCreate, TagUpdate
from app.schemas.common import PaginationMeta
from app.schemas.article import ArticleListItem

router = APIRouter()


@router.get("")
async def get_tags_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    sort: str = "usage_count",
    order: str = "desc",
    db: AsyncSession = Depends(get_db),
):
    """
    Get all tags
    """
    tags = await get_tags(db, skip=skip, limit=limit, sort=sort, order=order)
    total = await count_tags(db)

    tag_list = [TagResponse.model_validate(t) for t in tags]

    return {
        "success": True,
        "data": tag_list,
        "pagination": PaginationMeta.create(total, (skip // limit) + 1, limit).model_dump(),
    }


@router.get("/search")
async def search_tags_endpoint(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Search tags by name
    """
    tags = await search_tags(db, query=q, limit=limit)

    return {
        "success": True,
        "data": [TagResponse.model_validate(t) for t in tags],
    }


@router.get("/{tag_id}")
async def get_tag_by_id_endpoint(
    tag_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get tag by ID
    """
    tag = await get_tag(db, tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    return {"success": True, "data": TagResponse.model_validate(tag)}


@router.get("/{tag_id}/articles")
async def get_tag_articles_endpoint(
    tag_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Get articles with this tag
    """
    tag = await get_tag(db, tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    skip = (page - 1) * page_size
    articles = await get_articles(
        db,
        skip=skip,
        limit=page_size,
        status="published",
        tag_id=tag_id,
    )

    total = await count_articles_crud(
        db,
        status="published",
        tag_id=tag_id,
    )

    return {
        "success": True,
        "data": {
            "tag": TagResponse.model_validate(tag),
            "articles": [ArticleListItem.model_validate(a) for a in articles],
            "pagination": PaginationMeta.create(total, page, page_size).model_dump(),
        },
    }


@router.post("")
async def create_tag_endpoint(
    data: TagCreate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new tag (Admin only)
    """
    # Check if tag already exists
    existing = await get_tag_by_name(db, data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag already exists",
        )

    tag = await create_tag(db, data)

    return {
        "success": True,
        "data": TagResponse.model_validate(tag),
    }


@router.put("/{tag_id}")
async def update_tag_endpoint(
    tag_id: str,
    data: TagUpdate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a tag (Admin only)
    """
    tag = await get_tag(db, tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    updated_tag = await update_tag(db, tag, data)

    return {
        "success": True,
        "data": TagResponse.model_validate(updated_tag),
    }
