"""
Like Schemas
"""
from datetime import datetime
from pydantic import BaseModel


class LikeCreate(BaseModel):
    """Like creation schema"""

    target_id: str
    target_type: str  # 'article' or 'comment'


class LikeResponse(BaseModel):
    """Like response schema"""

    id: str
    user_id: str
    target_id: str
    target_type: str
    created_at: datetime
