"""
Bookmark CRUD Operations
"""
from typing import Optional, List
from sqlalchemy import select, and_, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bookmark import Bookmark
from app.schemas.bookmark import BookmarkCreate


async def get_bookmark(
    db: AsyncSession,
    user_id: str,
    article_id: str,
) -> Optional[Bookmark]:
    """Get bookmark by user and article"""
    result = await db.execute(
        select(Bookmark).where(
            and_(
                Bookmark.user_id == user_id,
                Bookmark.article_id == article_id,
            )
        )
    )
    return result.scalar_one_or_none()


async def check_if_bookmarked(
    db: AsyncSession,
    user_id: str,
    article_id: str,
) -> bool:
    """Check if user has bookmarked article"""
    bookmark = await get_bookmark(db, user_id, article_id)
    return bookmark is not None


async def create_bookmark(
    db: AsyncSession,
    user_id: str,
    article_id: str,
    folder: str = "default",
    notes: Optional[str] = None,
) -> Bookmark:
    """Create a bookmark"""
    import uuid

    bookmark = Bookmark(
        id=str(uuid.uuid4()),
        user_id=user_id,
        article_id=article_id,
        folder=folder,
        notes=notes,
    )

    db.add(bookmark)
    await db.flush()
    return bookmark


async def delete_bookmark(
    db: AsyncSession,
    user_id: str,
    article_id: str,
) -> None:
    """Delete a bookmark"""
    bookmark = await get_bookmark(db, user_id, article_id)

    if bookmark:
        await db.delete(bookmark)
        await db.flush()


async def get_user_bookmarks(
    db: AsyncSession,
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    folder: Optional[str] = None,
) -> List[Bookmark]:
    """Get bookmarks by user"""
    query = select(Bookmark).where(Bookmark.user_id == user_id)

    if folder:
        query = query.where(Bookmark.folder == folder)

    query = query.order_by(Bookmark.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def count_user_bookmarks(
    db: AsyncSession,
    user_id: str,
    folder: Optional[str] = None,
) -> int:
    """Count bookmarks by user"""
    query = select(func.count(Bookmark.id)).where(Bookmark.user_id == user_id)

    if folder:
        query = query.where(Bookmark.folder == folder)

    result = await db.execute(query)
    return result.scalar() or 0


async def get_user_folders(db: AsyncSession, user_id: str) -> List[str]:
    """Get unique folder names for user"""
    result = await db.execute(
        select(Bookmark.folder)
        .where(Bookmark.user_id == user_id)
        .distinct()
        .order_by(Bookmark.folder)
    )
    return [row[0] for row in result.fetchall()]


async def update_bookmark(
    db: AsyncSession,
    bookmark: Bookmark,
    folder: Optional[str] = None,
    notes: Optional[str] = None,
) -> Bookmark:
    """Update bookmark"""
    if folder is not None:
        bookmark.folder = folder
    if notes is not None:
        bookmark.notes = notes

    await db.flush()
    await db.refresh(bookmark)
    return bookmark
