"""
User Model
"""
import enum
from sqlalchemy import String, Boolean, JSON, Column, DateTime, Text, Integer, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class UserRole(str, enum.Enum):
    READER = "reader"
    AUTHOR = "author"
    ADMIN = "admin"


class User(Base):
    """User model"""

    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Profile
    full_name = Column(String)
    avatar_url = Column(String)
    bio = Column(Text)
    website = Column(String)
    location = Column(String)
    twitter_username = Column(String)
    github_username = Column(String)
    linkedin_url = Column(String)
    expertise = Column(ARRAY(String), default=[])
    role = Column(String, default=UserRole.READER, nullable=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Preferences
    notification_preferences = Column(JSON, default={"email": True, "push": False})

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    articles = relationship("Article", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    likes_given = relationship("Like", foreign_keys="Like.user_id", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    followers = relationship("Follow", foreign_keys="Follow.following_id", back_populates="following")
    following = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    papers_submitted = relationship("Paper", back_populates="submitter")

    def __repr__(self):
        return f"<User {self.username}>"
