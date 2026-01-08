"""
Follow CRUD Operations
"""
from typing import Optional, List
from sqlalchemy import select, and_, delete, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.follow import Follow
from app.models.user import User


async def get_follow(
    db: AsyncSession,
    follower_id: str,
    following_id: str,
) -> Optional[Follow]:
    """Get follow relationship"""
    result = await db.execute(
        select(Follow).where(
            and_(
                Follow.follower_id == follower_id,
                Follow.following_id == following_id,
            )
        )
    )
    return result.scalar_one_or_none()


async def check_if_following(
    db: AsyncSession,
    follower_id: str,
    following_id: str,
) -> bool:
    """Check if user is following another user"""
    follow = await get_follow(db, follower_id, following_id)
    return follow is not None


async def create_follow(
    db: AsyncSession,
    follower_id: str,
    following_id: str,
) -> Follow:
    """Create a follow relationship"""
    import uuid

    follow = Follow(
        id=str(uuid.uuid4()),
        follower_id=follower_id,
        following_id=following_id,
    )

    db.add(follow)
    await db.flush()
    return follow


async def delete_follow(
    db: AsyncSession,
    follower_id: str,
    following_id: str,
) -> None:
    """Delete a follow relationship"""
    follow = await get_follow(db, follower_id, following_id)

    if follow:
        await db.delete(follow)
        await db.flush()


async def get_followers(
    db: AsyncSession,
    user_id: str,
    skip: int = 0,
    limit: int = 20,
) -> List[User]:
    """Get user's followers"""
    result = await db.execute(
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
        .offset(skip)
        .limit(limit)
        .order_by(Follow.created_at.desc())
    )
    return list(result.scalars().all())


async def get_following(
    db: AsyncSession,
    user_id: str,
    skip: int = 0,
    limit: int = 20,
) -> List[User]:
    """Get users that user is following"""
    result = await db.execute(
        select(User)
        .join(Follow, Follow.following_id == User.id)
        .where(Follow.follower_id == user_id)
        .offset(skip)
        .limit(limit)
        .order_by(Follow.created_at.desc())
    )
    return list(result.scalars().all())


async def count_followers(db: AsyncSession, user_id: str) -> int:
    """Count user's followers"""
    result = await db.execute(
        select(func.count(Follow.id)).where(Follow.following_id == user_id)
    )
    return result.scalar() or 0


async def count_following(db: AsyncSession, user_id: str) -> int:
    """Count users that user is following"""
    result = await db.execute(
        select(func.count(Follow.id)).where(Follow.follower_id == user_id)
    )
    return result.scalar() or 0


async def get_mutual_followers(
    db: AsyncSession,
    user_id: str,
    other_user_id: str,
    limit: int = 20,
) -> List[User]:
    """Get mutual followers between two users"""
    result = await db.execute(
        select(User)
        .join(Follow.followers, User.id == Follow.follower_id)
        .where(Follow.following_id == user_id)
        .where(
            User.id.in_(
                select(Follow.follower_id).where(Follow.following_id == other_user_id)
            )
        )
        .limit(limit)
    )
    return list(result.scalars().all())
