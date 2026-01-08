"""
Tag Model
"""
from sqlalchemy import String, Column, DateTime, Integer
from sqlalchemy.sql import func

from app.core.database import Base


class Tag(Base):
    """Tag model for article tags"""

    __tablename__ = "tags"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(String)
    color = Column(String)  # Hex color code
    usage_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Tag {self.name}>"
