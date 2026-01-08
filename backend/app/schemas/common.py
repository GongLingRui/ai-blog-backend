"""
Common schemas and utilities
"""
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""

    success: bool = True
    data: T
    message: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated API response"""

    success: bool = True
    data: List[T]
    pagination: dict


class PaginationParams(BaseModel):
    """Pagination parameters"""

    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort: str = "created_at"
    order: str = Field("desc", regex="^(asc|desc)$")


class PaginationMeta(BaseModel):
    """Pagination metadata"""

    total: int
    page: int
    page_size: int
    pages: int

    @classmethod
    def create(cls, total: int, page: int, page_size: int) -> "PaginationMeta":
        """Create pagination metadata"""
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(total=total, page=page, page_size=page_size, pages=pages)


class ErrorResponse(BaseModel):
    """Error response"""

    success: bool = False
    error: "ErrorDetail"


class ErrorDetail(BaseModel):
    """Error detail"""

    code: str
    message: str
    details: Optional[dict] = None


# Update forward references
ApiResponse.model_rebuild()
