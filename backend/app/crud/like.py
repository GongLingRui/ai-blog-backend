"""
Like CRUD Operations
"""
from typing import Optional, List
from sqlalchemy import select, and_, delete, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.like import Like
from app.models.article import Article
from app.models.comment import Comment


async def get_like(
    db: AsyncSession,
    user_id: str,
    target_id: str,
    target_type: str,
) -> Optional[Like]:
    """Get like by user, target, and type"""
    result = await db.execute(
        select(Like).where(
            and_(
                Like.user_id == user_id,
                Like.target_id == target_id,
                Like.target_type == target_type,
            )
        )
    )
    return result.scalar_one_or_none()


async def check_if_liked(
    db: AsyncSession,
    user_id: str,
    target_id: str,
    target_type: str,
) -> bool:
    """Check if user has liked target"""
    like = await get_like(db, user_id, target_id, target_type)
    return like is not None


async def create_like(
    db: AsyncSession,
    user_id: str,
    target_id: str,
    target_type: str,
) -> Like:
    """Create a like"""
    import uuid

    like = Like(
        id=str(uuid.uuid4()),
        user_id=user_id,
        target_id=target_id,
        target_type=target_type,
    )

    db.add(like)

    # Update like count
    if target_type == "article":
        await db.execute(
            update(Article)
            .where(Article.id == target_id)
            .values(like_count=Article.like_count + 1)
        )
    elif target_type == "comment":
        await db.execute(
            update(Comment)
            .where(Comment.id == target_id)
            .values(like_count=Comment.like_count + 1)
        )

    await db.flush()
    return like


async def delete_like(
    db: AsyncSession,
    user_id: str,
    target_id: str,
    target_type: str,
) -> None:
    """Delete a like"""
    like = await get_like(db, user_id, target_id, target_type)

    if like:
        # Update like count
        if target_type == "article":
            await db.execute(
                update(Article)
                .where(Article.id == target_id)
                .values(like_count=Article.like_count - 1)
            )
        elif target_type == "comment":
            await db.execute(
                update(Comment)
                .where(Comment.id == target_id)
                .values(like_count=Comment.like_count - 1)
            )

        await db.delete(like)
        await db.flush()


async def get_article_likes(
    db: AsyncSession,
    article_id: str,
    skip: int = 0,
    limit: int = 20,
) -> List[Like]:
    """Get likes for an article"""
    result = await db.execute(
        select(Like)
        .where(and_(Like.target_id == article_id, Like.target_type == "article"))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def count_article_likes(db: AsyncSession, article_id: str) -> int:
    """Count likes for an article"""
    result = await db.execute(
        select(func.count(Like.id)).where(
            and_(Like.target_id == article_id, Like.target_type == "article")
        )
    )
    return result.scalar() or 0


async def get_user_likes(
    db: AsyncSession,
    user_id: str,
    skip: int = 0,
    limit: int = 20,
) -> List[Like]:
    """Get likes by user"""
    result = await db.execute(
        select(Like)
        .where(Like.user_id == user_id)
        .order_by(Like.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())
