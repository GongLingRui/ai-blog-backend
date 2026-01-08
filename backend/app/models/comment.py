"""
Comment Model
"""
import enum
from sqlalchemy import String, Column, DateTime, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class CommentStatus(str, enum.Enum):
    PENDING = "pending"
    PUBLISHED = "published"
    REJECTED = "rejected"
    SPAM = "spam"


class Comment(Base):
    """Comment model"""

    __tablename__ = "comments"

    id = Column(String, primary_key=True, index=True)
    article_id = Column(String, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(String, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)

    content = Column(Text, nullable=False)
    status = Column(String, default=CommentStatus.PUBLISHED, nullable=False, index=True)

    like_count = Column(Integer, default=0)
    is_edited = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    article = relationship("Article", back_populates="comments")
    author = relationship("User", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")

    def __repr__(self):
        return f"<Comment {self.id}>"
