"""
Comment CRUD Operations
"""
from typing import Optional, List
from sqlalchemy import select, and_, desc, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment import Comment, CommentStatus
from app.models.article import Article
from app.schemas.comment import CommentCreate, CommentUpdate


async def get_comment(db: AsyncSession, comment_id: str) -> Optional[Comment]:
    """Get comment by ID"""
    result = await db.execute(
        select(Comment)
        .options(
            selectinload(Comment.author),
            selectinload(Comment.article),
        )
        .where(Comment.id == comment_id)
    )
    return result.scalar_one_or_none()


async def get_comments(
    db: AsyncSession,
    article_id: str,
    skip: int = 0,
    limit: int = 20,
    parent_id: Optional[str] = None,
    status: str = CommentStatus.PUBLISHED,
) -> List[Comment]:
    """Get comments for an article"""
    query = (
        select(Comment)
        .options(
            selectinload(Comment.author),
        )
        .where(Comment.article_id == article_id)
        .where(Comment.status == status)
    )

    if parent_id is None:
        # Get top-level comments only
        query = query.where(Comment.parent_id.is_(None))
    else:
        query = query.where(Comment.parent_id == parent_id)

    query = query.order_by(Comment.created_at).offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def count_comments(
    db: AsyncSession,
    article_id: str,
    parent_id: Optional[str] = None,
    status: str = CommentStatus.PUBLISHED,
) -> int:
    """Count comments"""
    query = select(func.count(Comment.id)).where(Comment.article_id == article_id)

    if status:
        query = query.where(Comment.status == status)

    if parent_id is None:
        query = query.where(Comment.parent_id.is_(None))
    else:
        query = query.where(Comment.parent_id == parent_id)

    result = await db.execute(query)
    return result.scalar() or 0


async def get_replies(
    db: AsyncSession,
    comment_id: str,
    limit: int = 10,
) -> List[Comment]:
    """Get replies to a comment"""
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.author))
        .where(Comment.parent_id == comment_id)
        .where(Comment.status == CommentStatus.PUBLISHED)
        .order_by(Comment.created_at)
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_comment(
    db: AsyncSession,
    comment_in: CommentCreate,
    author_id: str,
) -> Comment:
    """Create new comment"""
    import uuid

    comment = Comment(
        id=str(uuid.uuid4()),
        article_id=comment_in.article_id,
        author_id=author_id,
        parent_id=comment_in.parent_id,
        content=comment_in.content,
        status=CommentStatus.PUBLISHED,
    )

    db.add(comment)

    # Update article comment count
    await db.execute(
        update(Article)
        .where(Article.id == comment_in.article_id)
        .values(comment_count=Article.comment_count + 1)
    )

    await db.flush()
    await db.refresh(comment)
    return await get_comment(db, comment.id)


async def update_comment(
    db: AsyncSession,
    comment: Comment,
    comment_in: CommentUpdate,
) -> Comment:
    """Update comment"""
    comment.content = comment_in.content
    comment.is_edited = True

    await db.flush()
    await db.refresh(comment)
    return await get_comment(db, comment.id)


async def delete_comment(db: AsyncSession, comment: Comment) -> None:
    """Delete comment"""
    from app.models.article import Article

    article_id = comment.article_id

    await db.delete(comment)
    await db.flush()

    # Update article comment count
    await db.execute(
        update(Article)
        .where(Article.id == article_id)
        .values(comment_count=Article.comment_count - 1)
    )
    await db.flush()


async def get_user_comments(
    db: AsyncSession,
    user_id: str,
    skip: int = 0,
    limit: int = 20,
) -> List[Comment]:
    """Get comments by user"""
    result = await db.execute(
        select(Comment)
        .options(
            selectinload(Comment.author),
            selectinload(Comment.article),
        )
        .where(Comment.author_id == user_id)
        .order_by(desc(Comment.created_at))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_pending_comments(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
) -> List[Comment]:
    """Get all pending comments (for admin review)"""
    result = await db.execute(
        select(Comment)
        .options(
            selectinload(Comment.author),
            selectinload(Comment.article),
        )
        .where(Comment.status == CommentStatus.PENDING)
        .order_by(Comment.created_at)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def count_pending_comments(db: AsyncSession) -> int:
    """Count pending comments"""
    result = await db.execute(
        select(func.count(Comment.id)).where(
            Comment.status == CommentStatus.PENDING
        )
    )
    return result.scalar() or 0


async def moderate_comment(
    db: AsyncSession,
    comment: Comment,
    new_status: CommentStatus,
) -> Comment:
    """Moderate a comment (update status)"""
    comment.status = new_status
    await db.flush()
    await db.refresh(comment)
    return await get_comment(db, comment.id)


async def get_all_comments(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    status: Optional[CommentStatus] = None,
) -> List[Comment]:
    """Get all comments with optional status filter (for admin)"""
    query = (
        select(Comment)
        .options(
            selectinload(Comment.author),
            selectinload(Comment.article),
        )
    )

    if status:
        query = query.where(Comment.status == status)

    query = query.order_by(desc(Comment.created_at)).offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def count_all_comments(
    db: AsyncSession,
    status: Optional[CommentStatus] = None,
) -> int:
    """Count all comments with optional status filter"""
    query = select(func.count(Comment.id))

    if status:
        query = query.where(Comment.status == status)

    result = await db.execute(query)
    return result.scalar() or 0
