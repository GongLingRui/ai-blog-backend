"""
Article Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class AuthorSummary(BaseModel):
    """Author summary for article"""

    id: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class CategorySummary(BaseModel):
    """Category summary for article"""

    id: str
    name: str
    slug: str
    color: Optional[str] = None


class TagSummary(BaseModel):
    """Tag summary for article"""

    id: str
    name: str
    slug: str
    color: Optional[str] = None


class ArticleBase(BaseModel):
    """Base article schema"""

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    cover_image_url: Optional[str] = None
    category_id: Optional[str] = None
    tags: List[str] = []


class ArticleCreate(ArticleBase):
    """Article creation schema"""

    status: str = Field("draft", regex="^(draft|published|archived)$")


class ArticleUpdate(BaseModel):
    """Article update schema"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    cover_image_url: Optional[str] = None
    category_id: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = Field(None, regex="^(draft|published|archived)$")


class ArticleResponse(BaseModel):
    """Article response schema"""

    id: str
    title: str
    slug: str
    content: str
    excerpt: Optional[str] = None
    cover_image_url: Optional[str] = None
    author: AuthorSummary
    category: Optional[CategorySummary] = None
    tags: List[TagSummary] = []
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    reading_time: Optional[int] = None
    is_featured: bool = False
    is_top: bool = False
    status: str
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ArticleListItem(BaseModel):
    """Article list item (minimal data)"""

    id: str
    title: str
    slug: str
    excerpt: Optional[str] = None
    cover_image_url: Optional[str] = None
    author: AuthorSummary
    category: Optional[CategorySummary] = None
    tags: List[TagSummary] = []
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    reading_time: Optional[int] = None
    is_featured: bool = False
    is_top: bool = False
    published_at: Optional[datetime] = None


class ArticleSearchParams(BaseModel):
    """Article search parameters"""

    search: Optional[str] = None
    category_id: Optional[str] = None
    tag_id: Optional[str] = None
    author_id: Optional[str] = None
    status: str = "published"
    sort: str = "published_at"
    order: str = "desc"
