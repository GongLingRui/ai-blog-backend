"""
User CRUD Operations
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


async def get_user(db: AsyncSession, user_id: str) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    role: Optional[str] = None,
    search: Optional[str] = None,
) -> List[User]:
    """Get list of users with filters"""
    query = select(User)

    if role:
        query = query.where(User.role == role)

    if search:
        query = query.where(
            (User.username.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )

    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


async def count_users(
    db: AsyncSession,
    role: Optional[str] = None,
    search: Optional[str] = None,
) -> int:
    """Count users with filters"""
    from sqlalchemy import func

    query = select(func.count(User.id))

    if role:
        query = query.where(User.role == role)

    if search:
        query = query.where(
            (User.username.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )

    result = await db.execute(query)
    return result.scalar() or 0


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create new user"""
    import uuid

    user = User(
        id=str(uuid.uuid4()),
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role=UserRole.READER,
    )

    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user: User, user_in: UserUpdate) -> User:
    """Update user"""
    update_data = user_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_user_stats(db: AsyncSession, user_id: str) -> dict:
    """Get user statistics"""
    from sqlalchemy import func
    from app.models.follow import Follow
    from app.models.article import Article, ArticleStatus

    # Count followers
    followers_result = await db.execute(
        select(func.count()).where(Follow.following_id == user_id)
    )
    followers_count = followers_result.scalar() or 0

    # Count following
    following_result = await db.execute(
        select(func.count()).where(Follow.follower_id == user_id)
    )
    following_count = following_result.scalar() or 0

    # Count articles
    articles_result = await db.execute(
        select(func.count())
        .where(Article.author_id == user_id)
        .where(Article.status == ArticleStatus.PUBLISHED)
    )
    articles_count = articles_result.scalar() or 0

    return {
        "followers_count": followers_count,
        "following_count": following_count,
        "articles_count": articles_count,
    }
