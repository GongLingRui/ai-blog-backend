"""
Follow Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FollowBase(BaseModel):
    """Base follow schema"""

    following_id: str


class FollowResponse(BaseModel):
    """Follow response schema"""

    id: str
    follower_id: str
    following_id: str
    created_at: datetime


class UserFollow(BaseModel):
    """User follow info"""

    id: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_following: bool = False
    followed_at: Optional[datetime] = None
