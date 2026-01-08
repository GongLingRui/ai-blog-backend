"""
Like Model
"""
from sqlalchemy import String, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Like(Base):
    """Like model for articles and comments"""

    __tablename__ = "likes"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_id = Column(String, nullable=False, index=True)
    target_type = Column(String, nullable=False)  # 'article' or 'comment'

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="likes_given")

    def __repr__(self):
        return f"<Like user={self.user_id} target={self.target_type}:{self.target_id}>"
