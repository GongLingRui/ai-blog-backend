"""
Test User CRUD operations
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import (
    get_user,
    get_user_by_email,
    get_user_by_username,
    get_users,
    count_users,
    create_user,
    update_user,
    authenticate_user,
    get_user_stats
)
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import UserRole


@pytest.mark.asyncio
async def test_get_user(db_session: AsyncSession, test_user):
    """Test getting user by ID"""
    user = await get_user(db_session, test_user.id)
    assert user is not None
    assert user.id == test_user.id
    assert user.username == test_user.username
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_get_user_not_found(db_session: AsyncSession):
    """Test getting non-existent user"""
    user = await get_user(db_session, "non-existent-id")
    assert user is None


@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession, test_user):
    """Test getting user by email"""
    user = await get_user_by_email(db_session, test_user.email)
    assert user is not None
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_get_user_by_username(db_session: AsyncSession, test_user):
    """Test getting user by username"""
    user = await get_user_by_username(db_session, test_user.username)
    assert user is not None
    assert user.username == test_user.username


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test creating new user"""
    user_in = UserCreate(
        username="newuser",
        email="newuser@example.com",
        password="password123",
        full_name="New User"
    )
    user = await create_user(db_session, user_in)

    assert user.username == "newuser"
    assert user.email == "newuser@example.com"
    assert user.full_name == "New User"
    assert user.role == UserRole.READER
    assert user.hashed_password is not None
    assert user.id is not None


@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession, test_user):
    """Test updating user"""
    user_in = UserUpdate(
        full_name="Updated Name",
        bio="Updated bio"
    )
    updated_user = await update_user(db_session, test_user, user_in)

    assert updated_user.full_name == "Updated Name"
    assert updated_user.bio == "Updated bio"
    assert updated_user.username == test_user.username  # Unchanged


@pytest.mark.asyncio
async def test_authenticate_user_success(db_session: AsyncSession, test_user):
    """Test authenticating user with correct credentials"""
    user = await authenticate_user(db_session, test_user.email, "testpass123")
    assert user is not None
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(db_session: AsyncSession, test_user):
    """Test authenticating user with wrong password"""
    user = await authenticate_user(db_session, test_user.email, "wrongpassword")
    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_non_existent(db_session: AsyncSession):
    """Test authenticating non-existent user"""
    user = await authenticate_user(db_session, "nonexistent@example.com", "password")
    assert user is None


@pytest.mark.asyncio
async def test_get_users(db_session: AsyncSession, test_user, test_user2):
    """Test getting list of users"""
    users = await get_users(db_session, skip=0, limit=10)
    assert len(users) >= 2
    assert any(u.id == test_user.id for u in users)
    assert any(u.id == test_user2.id for u in users)


@pytest.mark.asyncio
async def test_get_users_with_search(db_session: AsyncSession, test_user, test_user2):
    """Test searching users"""
    # Search by username
    users = await get_users(db_session, search="testuser")
    assert len(users) >= 1
    assert test_user.username in [u.username for u in users]

    # Search by email
    users = await get_users(db_session, search="test2@example.com")
    assert len(users) >= 1
    assert test_user2.email in [u.email for u in users]


@pytest.mark.asyncio
async def test_count_users(db_session: AsyncSession, test_user, test_user2):
    """Test counting users"""
    count = await count_users(db_session)
    assert count >= 2


@pytest.mark.asyncio
async def test_get_user_stats(db_session: AsyncSession, test_user, test_article, test_follow):
    """Test getting user statistics"""
    stats = await get_user_stats(db_session, test_user.id)

    assert "followers_count" in stats
    assert "following_count" in stats
    assert "articles_count" in stats
    assert stats["followers_count"] >= 0
    assert stats["following_count"] >= 0
    assert stats["articles_count"] >= 0
