"""
Comments API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middlewares.auth import get_current_user, get_current_admin
from app.models.user import User
from app.crud.comment import (
    get_comment,
    get_comments,
    count_comments,
    get_replies,
    create_comment,
    update_comment,
    delete_comment,
    get_user_comments,
    get_pending_comments,
    count_pending_comments,
    moderate_comment,
    get_all_comments,
    count_all_comments,
)
from app.schemas.comment import (
    CommentResponse,
    CommentWithReplies,
    CommentCreate,
    CommentUpdate,
    CommentModerate,
)
from app.schemas.common import PaginationMeta

router = APIRouter()


@router.get("")
async def get_comments_list(
    article_id: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    parent_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get comments for an article
    """
    skip = (page - 1) * page_size

    comments = await get_comments(
        db,
        article_id=article_id,
        skip=skip,
        limit=page_size,
        parent_id=parent_id,
    )

    total = await count_comments(
        db,
        article_id=article_id,
        parent_id=parent_id,
    )

    # If getting top-level comments, fetch replies
    if parent_id is None:
        comment_list = []
        for comment in comments:
            replies = await get_replies(db, comment.id)
            comment_data = CommentWithReplies.model_validate(comment)
            comment_data.replies = [
                CommentResponse.model_validate(r) for r in replies
            ]
            comment_list.append(comment_data)
    else:
        comment_list = [CommentResponse.model_validate(c) for c in comments]

    return {
        "success": True,
        "data": comment_list,
        "pagination": PaginationMeta.create(total, page, page_size).model_dump(),
    }


@router.get("/{comment_id}")
async def get_comment_by_id(
    comment_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get comment by ID
    """
    comment = await get_comment(db, comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    return {"success": True, "data": CommentResponse.model_validate(comment)}


@router.get("/{comment_id}/replies")
async def get_comment_replies_endpoint(
    comment_id: str,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Get replies to a comment
    """
    replies = await get_replies(db, comment_id, limit=limit)

    return {
        "success": True,
        "data": [CommentResponse.model_validate(r) for r in replies],
    }


@router.post("")
async def create_comment_endpoint(
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new comment
    """
    comment = await create_comment(db, data, author_id=current_user.id)

    return {
        "success": True,
        "data": CommentResponse.model_validate(comment),
    }


@router.put("/{comment_id}")
async def update_comment_endpoint(
    comment_id: str,
    data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a comment
    """
    comment = await get_comment(db, comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # Check ownership
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment",
        )

    updated_comment = await update_comment(db, comment, data)

    return {
        "success": True,
        "data": CommentResponse.model_validate(updated_comment),
    }


@router.delete("/{comment_id}")
async def delete_comment_endpoint(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a comment
    """
    comment = await get_comment(db, comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # Check ownership or admin
    if comment.author_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment",
        )

    await delete_comment(db, comment)

    return {"success": True, "message": "Comment deleted successfully"}


@router.get("/user/my-comments")
async def get_my_comments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's comments
    """
    skip = (page - 1) * page_size

    comments = await get_user_comments(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=page_size,
    )

    # Get total count
    from sqlalchemy import func, select
    from app.models.comment import Comment
    result = await db.execute(
        select(func.count(Comment.id)).where(Comment.author_id == current_user.id)
    )
    total = result.scalar() or 0

    return {
        "success": True,
        "data": [CommentResponse.model_validate(c) for c in comments],
        "pagination": PaginationMeta.create(total, page, page_size).model_dump(),
    }


@router.get("/admin/pending")
async def get_pending_comments_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get pending comments for review (Admin only)
    """
    skip = (page - 1) * page_size

    comments = await get_pending_comments(
        db,
        skip=skip,
        limit=page_size,
    )

    total = await count_pending_comments(db)

    return {
        "success": True,
        "data": [CommentResponse.model_validate(c) for c in comments],
        "pagination": PaginationMeta.create(total, page, page_size).model_dump(),
    }


@router.get("/admin/all")
async def get_all_comments_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all comments with optional status filter (Admin only)
    """
    skip = (page - 1) * page_size

    comments = await get_all_comments(
        db,
        skip=skip,
        limit=page_size,
        status=status,
    )

    total = await count_all_comments(db, status=status)

    return {
        "success": True,
        "data": [CommentResponse.model_validate(c) for c in comments],
        "pagination": PaginationMeta.create(total, page, page_size).model_dump(),
    }


@router.post("/{comment_id}/moderate")
async def moderate_comment_endpoint(
    comment_id: str,
    data: CommentModerate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Moderate a comment (Admin only)
    """
    comment = await get_comment(db, comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    from app.models.comment import CommentStatus
    moderated_comment = await moderate_comment(
        db,
        comment,
        CommentStatus(data.status.value),
    )

    return {
        "success": True,
        "data": CommentResponse.model_validate(moderated_comment),
        "message": f"Comment status updated to {data.status.value}",
    }
