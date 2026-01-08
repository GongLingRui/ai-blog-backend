"""
Tag Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    """Base tag schema"""

    name: str = Field(..., min_length=1, max_length=50)
    slug: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    color: Optional[str] = None


class TagCreate(TagBase):
    """Tag creation schema"""

    pass


class TagUpdate(BaseModel):
    """Tag update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    slug: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    color: Optional[str] = None


class TagResponse(TagBase):
    """Tag response schema"""

    id: str
    usage_count: int = 0
    created_at: datetime
