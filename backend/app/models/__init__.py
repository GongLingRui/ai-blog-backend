"""
SQLAlchemy Models
"""
from sqlalchemy.orm import DeclarativeBase

from app.core.database import Base

# Import all models
from app.models.user import User
from app.models.category import Category
from app.models.tag import Tag
from app.models.article import Article, ArticleTag
from app.models.comment import Comment
from app.models.like import Like
from app.models.bookmark import Bookmark
from app.models.follow import Follow
from app.models.notification import Notification
from app.models.paper import Paper

__all__ = [
    "Base",
    "User",
    "Category",
    "Tag",
    "Article",
    "ArticleTag",
    "Comment",
    "Like",
    "Bookmark",
    "Follow",
    "Notification",
    "Paper",
]
