"""
Categories API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middlewares.auth import get_current_user, get_current_admin
from app.models.user import User
from app.crud.category import (
    get_category,
    get_category_by_slug,
    get_categories,
    count_categories,
    create_category,
    update_category,
    delete_category as delete_category_crud,
)
from app.crud.article import get_articles, count_articles as count_articles_crud
from app.schemas.category import (
    CategoryResponse,
    CategoryCreate,
    CategoryUpdate,
)
from app.schemas.common import PaginationMeta
from app.schemas.article import ArticleListItem

router = APIRouter()


@router.get("")
async def get_categories_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all categories
    """
    categories = await get_categories(db, skip=skip, limit=limit, active_only=active_only)
    total = await count_categories(db, active_only=active_only)

    category_list = [CategoryResponse.model_validate(c) for c in categories]

    return {
        "success": True,
        "data": category_list,
        "pagination": PaginationMeta.create(total, (skip // limit) + 1, limit).model_dump(),
    }


@router.get("/{category_id}")
async def get_category_by_id_endpoint(
    category_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get category by ID
    """
    category = await get_category(db, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return {"success": True, "data": CategoryResponse.model_validate(category)}


@router.get("/slug/{slug}")
async def get_category_by_slug_endpoint(
    slug: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Get category by slug with articles
    """
    category = await get_category_by_slug(db, slug)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    # Get articles in this category
    skip = (page - 1) * page_size
    articles = await get_articles(
        db,
        skip=skip,
        limit=page_size,
        status="published",
        category_id=category.id,
    )

    total = await count_articles_crud(
        db,
        status="published",
        category_id=category.id,
    )

    category_data = CategoryResponse.model_validate(category)
    category_data.articles_count = total

    return {
        "success": True,
        "data": {
            "category": category_data.model_dump(),
            "articles": [ArticleListItem.model_validate(a) for a in articles],
            "pagination": PaginationMeta.create(total, page, page_size).model_dump(),
        },
    }


@router.post("")
async def create_category_endpoint(
    data: CategoryCreate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new category (Admin only)
    """
    category = await create_category(db, data)

    return {
        "success": True,
        "data": CategoryResponse.model_validate(category),
    }


@router.put("/{category_id}")
async def update_category_endpoint(
    category_id: str,
    data: CategoryUpdate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a category (Admin only)
    """
    category = await get_category(db, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    updated_category = await update_category(db, category, data)

    return {
        "success": True,
        "data": CategoryResponse.model_validate(updated_category),
    }


@router.delete("/{category_id}")
async def delete_category_endpoint(
    category_id: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a category (Admin only)
    """
    category = await get_category(db, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    await delete_category_crud(db, category)

    return {"success": True, "message": "Category deleted successfully"}
