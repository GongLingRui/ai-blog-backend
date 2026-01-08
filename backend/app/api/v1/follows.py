"""
Follows API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.middlewares.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.crud.follow import (
    check_if_following,
    create_follow,
    delete_follow,
    get_followers,
    get_following,
    count_followers,
    count_following,
    get_mutual_followers,
)
from app.schemas.follow import FollowResponse, UserFollow
from app.schemas.common import PaginationMeta

router = APIRouter()


class FollowCreate(BaseModel):
    """Follow creation schema"""

    following_id: str


@router.post("")
async def create_follow_endpoint(
    data: FollowCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    Follow a user
    """
    # Cannot follow yourself
    if data.following_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself",
        )

    # Check if already following
    if await check_if_following(db, current_user.id, data.following_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following",
        )

    follow = await create_follow(db, current_user.id, data.following_id)

    # Create notification for the followed user (async)
    # background_tasks.add_task(create_follow_notification, current_user.id, data.following_id)

    return {
        "success": True,
        "data": FollowResponse.model_validate(follow),
    }


@router.delete("/{user_id}")
async def delete_follow_endpoint(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Unfollow a user
    """
    await delete_follow(db, current_user.id, user_id)

    return {"success": True, "message": "Unfollowed successfully"}


@router.get("/{user_id}/followers")
async def get_user_followers_list(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user's followers
    """
    skip = (page - 1) * page_size

    followers = await get_followers(db, user_id, skip=skip, limit=page_size)
    total = await count_followers(db, user_id)

    # Check if current user is following each follower
    follower_list = []
    for follower in followers:
        is_following = False
        if current_user:
            is_following = await check_if_following(db, current_user.id, follower.id)

        from datetime import datetime
        follower_list.append(
            UserFollow(
                id=follower.id,
                username=follower.username,
                full_name=follower.full_name,
                avatar_url=follower.avatar_url,
                bio=follower.bio,
                is_following=is_following,
            )
        )

    return {
        "success": True,
        "data": follower_list,
        "pagination": PaginationMeta.create(total, page, page_size).model_dump(),
    }


@router.get("/{user_id}/following")
async def get_user_following_list(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Get users that user is following
    """
    skip = (page - 1) * page_size

    following = await get_following(db, user_id, skip=skip, limit=page_size)
    total = await count_following(db, user_id)

    # Check if current user is following each user
    following_list = []
    for user in following:
        is_following = False
        if current_user:
            is_following = await check_if_following(db, current_user.id, user.id)

        following_list.append(
            UserFollow(
                id=user.id,
                username=user.username,
                full_name=user.full_name,
                avatar_url=user.avatar_url,
                bio=user.bio,
                is_following=is_following,
            )
        )

    return {
        "success": True,
        "data": following_list,
        "pagination": PaginationMeta.create(total, page, page_size).model_dump(),
    }


@router.get("/{user_id}/stats")
async def get_follow_stats(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """
    Get follow statistics for a user
    """
    followers_count = await count_followers(db, user_id)
    following_count = await count_following(db, user_id)

    is_following = False
    is_followed_by = False

    if current_user:
        is_following = await check_if_following(db, current_user.id, user_id)
        is_followed_by = await check_if_following(db, user_id, current_user.id)

    return {
        "success": True,
        "data": {
            "user_id": user_id,
            "followers_count": followers_count,
            "following_count": following_count,
            "is_following": is_following,
            "is_followed_by": is_followed_by,
        },
    }


@router.get("/check/{user_id}")
async def check_if_following_endpoint(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check if current user is following the target user
    """
    is_following = await check_if_following(db, current_user.id, user_id)

    return {
        "success": True,
        "data": {"is_following": is_following},
    }


@router.get("/{user_id}/mutual")
async def get_mutual_followers_endpoint(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get mutual followers between current user and target user
    """
    skip = (page - 1) * page_size

    mutuals = await get_mutual_followers(
        db,
        current_user.id,
        user_id,
        limit=page_size,
    )

    # For simplicity, return all mutuals ( pagination would require more complex logic)
    return {
        "success": True,
        "data": [
            UserFollow(
                id=user.id,
                username=user.username,
                full_name=user.full_name,
                avatar_url=user.avatar_url,
                bio=user.bio,
                is_following=True,  # Mutual followers are always followed
            )
            for user in mutuals
        ],
    }
