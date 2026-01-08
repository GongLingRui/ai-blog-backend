"""
User Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """User registration schema"""

    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """User update schema"""

    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    twitter_username: Optional[str] = None
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    expertise: Optional[List[str]] = None


class UserResponse(BaseModel):
    """User response schema"""

    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    twitter_username: Optional[str] = None
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    expertise: List[str] = []
    role: str
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserProfile(UserResponse):
    """Extended user profile with stats"""

    followers_count: int = 0
    following_count: int = 0
    articles_count: int = 0


class UserLogin(BaseModel):
    """User login schema"""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    """Authentication response schema"""

    user: UserProfile
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ChangePassword(BaseModel):
    """Change password schema"""

    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
