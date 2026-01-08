"""
Test Follow CRUD operations
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.follow import (
    get_follow,
    get_user_followers,
    get_user_following,
    create_follow,
    delete_follow,
    is_following,
    count_followers,
    count_following,
    toggle_follow
)
from app.models.follow import Follow


@pytest.mark.asyncio
async def test_get_follow(db_session: AsyncSession, test_follow):
    """Test getting follow by ID"""
    follow = await get_follow(db_session, test_follow.id)
    assert follow is not None
    assert follow.id == test_follow.id
    assert follow.follower_id == test_follow.follower_id
    assert follow.following_id == test_follow.following_id


@pytest.mark.asyncio
async def test_get_follow_not_found(db_session: AsyncSession):
    """Test getting non-existent follow"""
    follow = await get_follow(db_session, "non-existent-id")
    assert follow is None


@pytest.mark.asyncio
async def test_create_follow(db_session: AsyncSession, test_user, test_user2):
    """Test creating new follow"""
    follow = await create_follow(db_session, test_user.id, test_user2.id)

    assert follow.follower_id == test_user.id
    assert follow.following_id == test_user2.id
    assert follow.id is not None


@pytest.mark.asyncio
async def test_delete_follow(db_session: AsyncSession, test_follow):
    """Test deleting follow"""
    await delete_follow(db_session, test_follow)

    # Verify follow is deleted
    follow = await get_follow(db_session, test_follow.id)
    assert follow is None


@pytest.mark.asyncio
async def test_get_user_followers(db_session: AsyncSession, test_user2, test_follow):
    """Test getting user's followers"""
    followers = await get_user_followers(db_session, user_id=test_user2.id)
    assert len(followers) >= 1
    assert test_follow.id in [f.id for f in followers]


@pytest.mark.asyncio
async def test_get_user_following(db_session: AsyncSession, test_user, test_follow):
    """Test getting who user is following"""
    following = await get_user_following(db_session, user_id=test_user.id)
    assert len(following) >= 1
    assert test_follow.id in [f.id for f in following]


@pytest.mark.asyncio
async def test_is_following(db_session: AsyncSession, test_user, test_user2, test_follow):
    """Test checking if user is following another"""
    is_following_result = await is_following(db_session, test_user.id, test_user2.id)
    assert is_following_result is True


@pytest.mark.asyncio
async def test_is_not_following(db_session: AsyncSession, test_user, test_user2):
    """Test checking if user is not following"""
    # Delete the test follow first
    follows = await get_user_following(db_session, user_id=test_user.id)
    for follow in follows:
        await db_session.delete(follow)
    await db_session.flush()

    is_following_result = await is_following(db_session, test_user.id, test_user2.id)
    assert is_following_result is False


@pytest.mark.asyncio
async def test_count_followers(db_session: AsyncSession, test_user2, test_follow):
    """Test counting user's followers"""
    count = await count_followers(db_session, user_id=test_user2.id)
    assert count >= 1


@pytest.mark.asyncio
async def test_count_following(db_session: AsyncSession, test_user, test_follow):
    """Test counting who user is following"""
    count = await count_following(db_session, user_id=test_user.id)
    assert count >= 1


@pytest.mark.asyncio
async def test_toggle_follow_create(db_session: AsyncSession, test_user, test_user2):
    """Test toggling follow to create"""
    # Ensure no follow exists
    follows = await get_user_following(db_session, user_id=test_user.id)
    for follow in follows:
        await db_session.delete(follow)
    await db_session.flush()

    # Toggle to create
    follow = await toggle_follow(db_session, test_user.id, test_user2.id)
    assert follow is not None
    assert follow.follower_id == test_user.id
    assert follow.following_id == test_user2.id


@pytest.mark.asyncio
async def test_toggle_follow_delete(db_session: AsyncSession, test_user, test_user2, test_follow):
    """Test toggling follow to delete"""
    # Toggle to delete
    result = await toggle_follow(db_session, test_user.id, test_user2.id)

    # Verify follow is deleted
    is_following_result = await is_following(db_session, test_user.id, test_user2.id)
    assert is_following_result is False


@pytest.mark.asyncio
async def test_cannot_follow_self(db_session: AsyncSession, test_user):
    """Test that user cannot follow themselves"""
    follow = await create_follow(db_session, test_user.id, test_user.id)
    assert follow is None


@pytest.mark.asyncio
async def test_duplicate_follow(db_session: AsyncSession, test_user, test_user2):
    """Test that duplicate follows are handled"""
    # Create first follow
    await create_follow(db_session, test_user.id, test_user2.id)

    # Try to create duplicate
    duplicate = await create_follow(db_session, test_user.id, test_user2.id)

    # Should either return existing or fail gracefully
    assert duplicate is not None


@pytest.mark.asyncio
async def test_follow_with_pagination(db_session: AsyncSession, test_user, test_user2):
    """Test getting followers with pagination"""
    # Create multiple users and follows
    for i in range(5):
        from app.crud.user import create_user
        from app.schemas.user import UserCreate

        user_in = UserCreate(
            username=f"follower{i}",
            email=f"follower{i}@example.com",
            password="password123"
        )
        new_user = await create_user(db_session, user_in)
        await create_follow(db_session, new_user.id, test_user2.id)

    # Get with pagination
    followers = await get_user_followers(db_session, user_id=test_user2.id, skip=0, limit=3)
    assert len(followers) == 3
