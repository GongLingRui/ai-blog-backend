"""
Bookmark Model
"""
from sqlalchemy import String, Column, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Bookmark(Base):
    """Bookmark model for saving articles"""

    __tablename__ = "bookmarks"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    article_id = Column(String, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    folder = Column(String, default="default")
    notes = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="bookmarks")

    def __repr__(self):
        return f"<Bookmark user={self.user_id} article={self.article_id}>"
