"""
Classic Paper Model
"""
from sqlalchemy import String, Column, DateTime, Text, Integer, ARRAY, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Paper(Base):
    """Classic AI paper model"""

    __tablename__ = "papers"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    authors = Column(ARRAY(String), nullable=False)
    year = Column(Integer)
    abstract = Column(Text)

    pdf_url = Column(String)
    arxiv_id = Column(String, index=True)
    doi = Column(String)
    publication_venue = Column(String)

    citation_count = Column(Integer, default=0)

    category_id = Column(String, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    tags = Column(ARRAY(String), default=[])

    submitted_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_approved = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="papers")
    submitter = relationship("User", back_populates="papers_submitted")

    def __repr__(self):
        return f"<Paper {self.title}>"
