"""
Likes API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.middlewares.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.crud.like import (
    check_if_liked,
    create_like,
    delete_like,
    get_article_likes,
    count_article_likes,
    get_user_likes,
)
from app.schemas.like import LikeCreate, LikeResponse
from app.schemas.common import PaginationMeta

router = APIRouter()


class BatchLikeRequest(BaseModel):
    """Batch like operation request"""

    target_ids: List[str]
    target_type: str  # 'article' or 'comment'


@router.post("")
async def create_like_endpoint(
    data: LikeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Like an article or comment
    """
    # Check if already liked
    if await check_if_liked(db, current_user.id, data.target_id, data.target_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already liked",
        )

    like = await create_like(db, current_user.id, data.target_id, data.target_type)

    return {
        "success": True,
        "data": LikeResponse.model_validate(like),
    }


@router.delete("/{target_id}")
async def delete_like_endpoint(
    target_id: str,
    target_type: str = Query(..., regex="^(article|comment)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Unlike an article or comment
    """
    await delete_like(db, current_user.id, target_id, target_type)

    return {"success": True, "message": "Like removed successfully"}


@router.get("/check")
async def check_if_liked_endpoint(
    target_id: str,
    target_type: str = Query(..., regex="^(article|comment)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check if current user has liked target
    """
    is_liked = await check_if_liked(db, current_user.id, target_id, target_type)

    return {
        "success": True,
        "data": {"is_liked": is_liked},
    }


@router.get("/article/{article_id}")
async def get_article_likes_endpoint(
    article_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """
    Get likes for an article
    """
    skip = (page - 1) * page_size

    likes = await get_article_likes(
        db,
        article_id,
        skip=skip,
        limit=page_size,
    )

    total = await count_article_likes(db, article_id)

    return {
        "success": True,
        "data": [LikeResponse.model_validate(l) for l in likes],
        "pagination": PaginationMeta.create(total, page, page_size).model_dump(),
    }


@router.get("/user/my-likes")
async def get_my_likes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's likes
    """
    skip = (page - 1) * page_size

    likes = await get_user_likes(
        db,
        current_user.id,
        skip=skip,
        limit=page_size,
    )

    # Get total count
    from sqlalchemy import func, select
    from app.models.like import Like
    result = await db.execute(
        select(func.count(Like.id)).where(Like.user_id == current_user.id)
    )
    total = result.scalar() or 0

    return {
        "success": True,
        "data": [LikeResponse.model_validate(l) for l in likes],
        "pagination": PaginationMeta.create(total, page, page_size).model_dump(),
    }


@router.get("/stats/{target_id}")
async def get_like_stats(
    target_id: str,
    target_type: str = Query(..., regex="^(article|comment)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """
    Get like statistics for a target
    """
    from sqlalchemy import func, select
    from app.models.like import Like

    # Count total likes
    result = await db.execute(
        select(func.count(Like.id)).where(
            Like.target_id == target_id,
            Like.target_type == target_type
        )
    )
    total_likes = result.scalar() or 0

    # Check if current user has liked
    is_liked = False
    if current_user:
        is_liked = await check_if_liked(db, current_user.id, target_id, target_type)

    return {
        "success": True,
        "data": {
            "target_id": target_id,
            "target_type": target_type,
            "total_likes": total_likes,
            "is_liked": is_liked,
        },
    }
