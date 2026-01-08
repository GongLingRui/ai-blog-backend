"""
Bookmarks API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.middlewares.auth import get_current_user
from app.models.user import User
from app.crud.bookmark import (
    get_bookmark,
    check_if_bookmarked,
    create_bookmark,
    delete_bookmark,
    get_user_bookmarks,
    count_user_bookmarks,
    get_user_folders,
    update_bookmark,
)
from app.schemas.bookmark import BookmarkCreate, BookmarkResponse, BookmarkUpdate
from app.schemas.common import PaginationMeta
from app.schemas.article import ArticleListItem
from app.crud.article import get_article

router = APIRouter()


class BatchBookmarkRequest(BaseModel):
    """Batch bookmark operation request"""

    article_ids: List[str]


class BatchBookmarkResponse(BaseModel):
    """Batch bookmark operation response"""

    successful: List[str]
    failed: List[dict]


@router.get("")
async def get_user_bookmarks_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    folder: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's bookmarks
    """
    skip = (page - 1) * page_size

    bookmarks = await get_user_bookmarks(
        db,
        current_user.id,
        skip=skip,
        limit=page_size,
        folder=folder
    )
    total = await count_user_bookmarks(db, current_user.id, folder=folder)

    # Fetch article details
    bookmark_list = []
    for bookmark in bookmarks:
        article = await get_article(db, bookmark.article_id)
        if article:
            bookmark_data = {
                "id": bookmark.id,
                "article": ArticleListItem.model_validate(article).model_dump(),
                "folder": bookmark.folder,
                "notes": bookmark.notes,
                "created_at": bookmark.created_at.isoformat(),
            }
            bookmark_list.append(bookmark_data)

    return {
        "success": True,
        "data": bookmark_list,
        "pagination": PaginationMeta.create(total, page, page_size).model_dump(),
    }


@router.get("/folders")
async def get_user_folders_list(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's bookmark folders
    """
    folders = await get_user_folders(db, current_user.id)

    return {
        "success": True,
        "data": folders,
    }


@router.get("/check/{article_id}")
async def check_bookmark_endpoint(
    article_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check if article is bookmarked
    """
    is_bookmarked = await check_if_bookmarked(db, current_user.id, article_id)

    return {
        "success": True,
        "data": {"is_bookmarked": is_bookmarked},
    }


@router.post("")
async def create_bookmark_endpoint(
    data: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new bookmark
    """
    # Check if already bookmarked
    if await check_if_bookmarked(db, current_user.id, data.article_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already bookmarked",
        )

    bookmark = await create_bookmark(
        db,
        current_user.id,
        data.article_id,
        folder=data.folder,
        notes=data.notes,
    )

    return {
        "success": True,
        "data": BookmarkResponse.model_validate(bookmark),
    }


@router.post("/batch")
async def create_bookmarks_batch_endpoint(
    data: BatchBookmarkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create multiple bookmarks at once
    """
    successful = []
    failed = []

    for article_id in data.article_ids:
        try:
            # Check if already bookmarked
            if not await check_if_bookmarked(db, current_user.id, article_id):
                await create_bookmark(
                    db,
                    current_user.id,
                    article_id,
                    folder="default",
                )
                successful.append(article_id)
            else:
                failed.append({"article_id": article_id, "error": "Already bookmarked"})
        except Exception as e:
            failed.append({"article_id": article_id, "error": str(e)})

    return {
        "success": True,
        "data": {
            "successful": successful,
            "failed": failed,
            "total_requested": len(data.article_ids),
            "total_successful": len(successful),
        },
    }


@router.delete("/{article_id}")
async def delete_bookmark_endpoint(
    article_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a bookmark
    """
    await delete_bookmark(db, current_user.id, article_id)

    return {"success": True, "message": "Bookmark removed successfully"}


@router.delete("/batch")
async def delete_bookmarks_batch_endpoint(
    data: BatchBookmarkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete multiple bookmarks at once
    """
    successful = []
    failed = []

    for article_id in data.article_ids:
        try:
            await delete_bookmark(db, current_user.id, article_id)
            successful.append(article_id)
        except Exception as e:
            failed.append({"article_id": article_id, "error": str(e)})

    return {
        "success": True,
        "data": {
            "successful": successful,
            "failed": failed,
            "total_requested": len(data.article_ids),
            "total_successful": len(successful),
        },
    }


@router.patch("/{article_id}")
async def update_bookmark_endpoint(
    article_id: str,
    data: BookmarkUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a bookmark
    """
    bookmark = await get_bookmark(db, current_user.id, article_id)

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )

    updated = await update_bookmark(
        db,
        bookmark,
        folder=data.folder,
        notes=data.notes,
    )

    return {
        "success": True,
        "data": BookmarkResponse.model_validate(updated),
    }
