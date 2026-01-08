"""
Notification Model
"""
import enum
from sqlalchemy import String, Column, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class NotificationType(str, enum.Enum):
    COMMENT = "comment"
    LIKE = "like"
    FOLLOW = "follow"
    MENTION = "mention"
    SYSTEM = "system"


class Notification(Base):
    """Notification model for user notifications"""

    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text)
    link = Column(String)  # URL to navigate to when clicked

    is_read = Column(Boolean, default=False, index=True)
    data = Column(JSON)  # Additional data

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.type} for user {self.user_id}>"
