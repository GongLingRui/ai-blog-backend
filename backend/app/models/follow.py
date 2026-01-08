"""
Follow Model
"""
from sqlalchemy import String, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Follow(Base):
    """Follow model for user following"""

    __tablename__ = "follows"

    id = Column(String, primary_key=True, index=True)
    follower_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    following_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following = relationship("User", foreign_keys=[following_id], back_populates="followers")

    def __repr__(self):
        return f"<Follow {self.follower_id} -> {self.following_id}>"
