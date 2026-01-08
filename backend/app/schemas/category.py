"""
Category Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """Base category schema"""

    name: str = Field(..., min_length=1, max_length=50)
    slug: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Category creation schema"""

    parent_id: Optional[str] = None
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    """Category update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    slug: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None


class CategoryResponse(CategoryBase):
    """Category response schema"""

    id: str
    parent_id: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    articles_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
