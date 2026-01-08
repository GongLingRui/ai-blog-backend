"""
Test Comment CRUD operations
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.comment import (
    get_comment,
    get_comments,
    get_replies,
    create_comment,
    update_comment,
    delete_comment,
    get_user_comments,
    get_pending_comments,
    count_comments,
    count_pending_comments,
    moderate_comment,
    get_all_comments,
    count_all_comments
)
from app.schemas.comment import CommentCreate, CommentUpdate
from app.models.comment import CommentStatus


@pytest.mark.asyncio
async def test_get_comment(db_session: AsyncSession, test_comment):
    """Test getting comment by ID"""
    comment = await get_comment(db_session, test_comment.id)
    assert comment is not None
    assert comment.id == test_comment.id
    assert comment.content == test_comment.content


@pytest.mark.asyncio
async def test_get_comment_with_relations(db_session: AsyncSession, test_comment):
    """Test getting comment with author and article"""
    comment = await get_comment(db_session, test_comment.id)
    assert comment is not None
    assert comment.author is not None
    assert comment.article is not None


@pytest.mark.asyncio
async def test_create_comment(db_session: AsyncSession, test_user, test_article):
    """Test creating new comment"""
    comment_in = CommentCreate(
        article_id=test_article.id,
        content="New test comment"
    )
    comment = await create_comment(db_session, comment_in, test_user.id)

    assert comment.content == "New test comment"
    assert comment.author_id == test_user.id
    assert comment.article_id == test_article.id
    assert comment.status == CommentStatus.PUBLISHED


@pytest.mark.asyncio
async def test_create_reply(db_session: AsyncSession, test_user, test_article, test_comment):
    """Test creating reply to comment"""
    comment_in = CommentCreate(
        article_id=test_article.id,
        parent_id=test_comment.id,
        content="This is a reply"
    )
    reply = await create_comment(db_session, comment_in, test_user.id)

    assert reply.content == "This is a reply"
    assert reply.parent_id == test_comment.id


@pytest.mark.asyncio
async def test_update_comment(db_session: AsyncSession, test_comment):
    """Test updating comment"""
    comment_in = CommentUpdate(content="Updated comment content")
    updated_comment = await update_comment(db_session, test_comment, comment_in)

    assert updated_comment.content == "Updated comment content"
    assert updated_comment.is_edited is True


@pytest.mark.asyncio
async def test_delete_comment(db_session: AsyncSession, test_comment):
    """Test deleting comment"""
    await delete_comment(db_session, test_comment)

    # Verify comment is deleted
    comment = await get_comment(db_session, test_comment.id)
    assert comment is None


@pytest.mark.asyncio
async def test_get_comments(db_session: AsyncSession, test_article, test_comment):
    """Test getting comments for article"""
    comments = await get_comments(db_session, article_id=test_article.id)
    assert len(comments) >= 1
    assert test_comment.id in [c.id for c in comments]


@pytest.mark.asyncio
async def test_get_top_level_comments_only(db_session: AsyncSession, test_article, test_comment):
    """Test that only top-level comments are returned"""
    # Create a reply
    from app.schemas.comment import CommentCreate
    reply_in = CommentCreate(
        article_id=test_article.id,
        parent_id=test_comment.id,
        content="Reply"
    )
    await create_comment(db_session, reply_in, test_comment.author_id)

    # Get top-level comments
    comments = await get_comments(db_session, article_id=test_article.id)
    assert all(c.parent_id is None for c in comments)


@pytest.mark.asyncio
async def test_get_replies(db_session: AsyncSession, test_article, test_user, test_comment):
    """Test getting replies to a comment"""
    # Create a reply
    from app.schemas.comment import CommentCreate
    reply_in = CommentCreate(
        article_id=test_article.id,
        parent_id=test_comment.id,
        content="Test reply"
    )
    reply = await create_comment(db_session, reply_in, test_user.id)

    # Get replies
    replies = await get_replies(db_session, comment_id=test_comment.id)
    assert len(replies) >= 1
    assert reply.id in [r.id for r in replies]


@pytest.mark.asyncio
async def test_count_comments(db_session: AsyncSession, test_article, test_comment):
    """Test counting comments"""
    count = await count_comments(db_session, article_id=test_article.id)
    assert count >= 1


@pytest.mark.asyncio
async def test_get_user_comments(db_session: AsyncSession, test_user, test_comment):
    """Test getting comments by user"""
    comments = await get_user_comments(db_session, user_id=test_user.id)
    assert len(comments) >= 1
    assert test_comment.id in [c.id for c in comments]


@pytest.mark.asyncio
async def test_moderate_comment(db_session: AsyncSession, test_comment):
    """Test moderating comment"""
    # Create pending comment
    test_comment.status = CommentStatus.PENDING
    await db_session.flush()

    # Approve comment
    moderated = await moderate_comment(db_session, test_comment, CommentStatus.PUBLISHED)
    assert moderated.status == CommentStatus.PUBLISHED


@pytest.mark.asyncio
async def test_get_pending_comments(db_session: AsyncSession, test_comment):
    """Test getting pending comments"""
    # Set comment to pending
    test_comment.status = CommentStatus.PENDING
    await db_session.flush()

    pending = await get_pending_comments(db_session)
    assert test_comment.id in [c.id for c in pending]


@pytest.mark.asyncio
async def test_count_pending_comments(db_session: AsyncSession, test_comment):
    """Test counting pending comments"""
    # Set comment to pending
    test_comment.status = CommentStatus.PENDING
    await db_session.flush()

    count = await count_pending_comments(db_session)
    assert count >= 1


@pytest.mark.asyncio
async def test_get_all_comments(db_session: AsyncSession, test_comment):
    """Test getting all comments"""
    comments = await get_all_comments(db_session)
    assert len(comments) >= 1
    assert test_comment.id in [c.id for c in comments]


@pytest.mark.asyncio
async def test_count_all_comments(db_session: AsyncSession, test_comment):
    """Test counting all comments"""
    count = await count_all_comments(db_session)
    assert count >= 1


@pytest.mark.asyncio
async def test_comment_status_filtering(db_session: AsyncSession, test_user, test_article):
    """Test filtering comments by status"""
    from app.schemas.comment import CommentCreate

    # Create pending comment
    pending_in = CommentCreate(
        article_id=test_article.id,
        content="Pending comment"
    )
    pending_comment = await create_comment(db_session, pending_in, test_user.id)
    pending_comment.status = CommentStatus.PENDING
    await db_session.flush()

    # Get only published comments
    published = await get_comments(db_session, article_id=test_article.id, status=CommentStatus.PUBLISHED)
    assert pending_comment.id not in [c.id for c in published]
