"""
Comment Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class CommentStatus(str, Enum):
    """Comment status enum"""
    PENDING = "pending"
    PUBLISHED = "published"
    REJECTED = "rejected"
    SPAM = "spam"


class CommentAuthor(BaseModel):
    """Comment author summary"""

    id: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class CommentBase(BaseModel):
    """Base comment schema"""

    content: str = Field(..., min_length=1, max_length=5000)


class CommentCreate(CommentBase):
    """Comment creation schema"""

    article_id: str
    parent_id: Optional[str] = None


class CommentUpdate(BaseModel):
    """Comment update schema"""

    content: str = Field(..., min_length=1, max_length=5000)


class CommentModerate(BaseModel):
    """Comment moderation schema"""

    status: CommentStatus


class CommentResponse(CommentBase):
    """Comment response schema"""

    id: str
    article_id: str
    author: CommentAuthor
    parent_id: Optional[str] = None
    like_count: int = 0
    is_edited: bool = False
    status: CommentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None


class CommentWithReplies(CommentResponse):
    """Comment with nested replies"""

    replies: List["CommentWithReplies"] = []


# Update forward reference
CommentWithReplies.model_rebuild()
