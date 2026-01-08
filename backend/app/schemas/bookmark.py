"""
Bookmark Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BookmarkBase(BaseModel):
    """Base bookmark schema"""

    folder: str = "default"
    notes: Optional[str] = None


class BookmarkCreate(BookmarkBase):
    """Bookmark creation schema"""

    article_id: str


class BookmarkUpdate(BaseModel):
    """Bookmark update schema"""

    folder: Optional[str] = None
    notes: Optional[str] = None


class BookmarkResponse(BookmarkBase):
    """Bookmark response schema"""

    id: str
    user_id: str
    article_id: str
    created_at: datetime


class BookmarkWithArticle(BookmarkResponse):
    """Bookmark with article details"""

    article: dict  # ArticleListItem
