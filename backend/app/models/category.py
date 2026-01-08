"""
Category Model
"""
from sqlalchemy import String, Column, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Category(Base):
    """Category model for organizing articles"""

    __tablename__ = "categories"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(String)
    icon = Column(String)
    color = Column(String)  # Hex color code

    parent_id = Column(String, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    articles = relationship("Article", back_populates="category")
    parent = relationship("Category", remote_side=[id], backref="children")
    papers = relationship("Paper", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"
