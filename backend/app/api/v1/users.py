"""
Users API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import require_auth
from app.crud.user import get_user, get_users, count_users, update_user as update_user_crud
from app.crud.article import get_articles, count_articles as count_articles_crud
from app.schemas.user import UserProfile, UserUpdate as UserUpdateSchema
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.article import ArticleListItem

router = APIRouter()


@router.get("")
async def get_users_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of users with pagination
    """
    skip = (page - 1) * page_size

    users = await get_users(db, skip=skip, limit=page_size, role=role, search=search)
    total = await count_users(db, role=role, search=search)

    user_list = [UserProfile.model_validate(u) for u in users]

    return {
        "success": True,
        "data": user_list,
        "pagination": PaginationMeta.create(total, page, page_size).model_dump(),
    }


@router.get("/{user_id}")
async def get_user_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get user by ID
    """
    user = await get_user(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {"success": True, "data": UserProfile.model_validate(user)}


@router.patch("/{user_id}")
async def update_user_profile(
    user_id: str,
    user_in: UserUpdateSchema,
    current_user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user profile
    """
    # Check ownership or admin
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )

    user = await get_user(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    updated_user = await update_user_crud(db, user, user_in)

    return {
        "success": True,
        "data": UserProfile.model_validate(updated_user),
    }


@router.get("/{user_id}/articles")
async def get_user_articles_list(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = "published",
    db: AsyncSession = Depends(get_db),
):
    """
    Get user's articles
    """
    skip = (page - 1) * page_size

    articles = await get_articles(
        db,
        skip=skip,
        limit=page_size,
        status=status,
        author_id=user_id,
    )

    total = await count_articles_crud(
        db,
        status=status,
        author_id=user_id,
    )

    article_list = [ArticleListItem.model_validate(a) for a in articles]

    return {
        "success": True,
        "data": article_list,
        "pagination": PaginationMeta.create(total, page, page_size).model_dump(),
    }
