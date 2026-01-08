"""
Pytest configuration and fixtures for AI Muse Blog testing
"""
import os
import sys
import asyncio
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.config import settings
from app.core.database import Base, get_db
from app.models.user import User
from app.models.article import Article, Category, Tag
from app.models.comment import Comment
from app.models.bookmark import Bookmark
from app.models.like import Like
from app.models.follow import Follow
from app.core.security import create_access_token, get_password_hash

# Test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/ai_muse_blog_test"
)

# Create async engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False
)

# Create async session factory
TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator:
    """Create test client with database override"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def temp_upload_dir() -> Generator:
    """Create temporary upload directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# ============ Test Data Fixtures ============

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User",
        bio="Test bio",
        avatar_url=None,
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user2(db_session: AsyncSession) -> User:
    """Create second test user"""
    user = User(
        username="testuser2",
        email="test2@example.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User 2",
        bio="Test bio 2",
        avatar_url=None,
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_superuser(db_session: AsyncSession) -> User:
    """Create test superuser"""
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpass123"),
        full_name="Admin User",
        bio="Admin",
        avatar_url=None,
        is_active=True,
        is_superuser=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_category(db_session: AsyncSession, test_user: User) -> Category:
    """Create test category"""
    category = Category(
        name="Technology",
        slug="technology",
        description="Tech articles"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest_asyncio.fixture
async def test_article(db_session: AsyncSession, test_user: User, test_category: Category) -> Article:
    """Create test article"""
    article = Article(
        title="Test Article",
        slug="test-article",
        content="This is a test article content",
        excerpt="Test excerpt",
        cover_image=None,
        author_id=test_user.id,
        category_id=test_category.id,
        status="published",
        view_count=0
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)
    return article


@pytest_asyncio.fixture
async def test_comment(db_session: AsyncSession, test_user: User, test_article: Article) -> Comment:
    """Create test comment"""
    comment = Comment(
        content="This is a test comment",
        author_id=test_user.id,
        article_id=test_article.id,
        parent_id=None
    )
    db_session.add(comment)
    await db_session.commit()
    await db_session.refresh(comment)
    return comment


@pytest_asyncio.fixture
async def test_bookmark(db_session: AsyncSession, test_user: User, test_article: Article) -> Bookmark:
    """Create test bookmark"""
    bookmark = Bookmark(
        user_id=test_user.id,
        article_id=test_article.id
    )
    db_session.add(bookmark)
    await db_session.commit()
    await db_session.refresh(bookmark)
    return bookmark


@pytest_asyncio.fixture
async def test_like(db_session: AsyncSession, test_user: User, test_article: Article) -> Like:
    """Create test like"""
    like = Like(
        user_id=test_user.id,
        article_id=test_article.id
    )
    db_session.add(like)
    await db_session.commit()
    await db_session.refresh(like)
    return like


@pytest_asyncio.fixture
async def test_follow(db_session: AsyncSession, test_user: User, test_user2: User) -> Follow:
    """Create test follow"""
    follow = Follow(
        follower_id=test_user.id,
        following_id=test_user2.id
    )
    db_session.add(follow)
    await db_session.commit()
    await db_session.refresh(follow)
    return follow


# ============ Auth Fixtures ============

@pytest.fixture
def user_token(test_user: User) -> str:
    """Generate access token for test user"""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
def user2_token(test_user2: User) -> str:
    """Generate access token for second test user"""
    return create_access_token(data={"sub": str(test_user2.id)})


@pytest.fixture
def superuser_token(test_superuser: User) -> str:
    """Generate access token for superuser"""
    return create_access_token(data={"sub": str(test_superuser.id)})


@pytest.fixture
def user_headers(user_token: str) -> dict:
    """Generate headers with user authorization"""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def superuser_headers(superuser_token: str) -> dict:
    """Generate headers with superuser authorization"""
    return {"Authorization": f"Bearer {superuser_token}"}


# ============ Pytest Configuration ============

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line("markers", "asyncio: mark test as async")


@pytest.fixture(autouse=True)
def override_settings(monkeypatch):
    """Override settings for testing"""
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("UPLOAD_DIR", tempfile.gettempdir())
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "False")
