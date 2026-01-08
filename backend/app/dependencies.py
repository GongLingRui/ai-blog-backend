"""
FastAPI dependencies
"""
from typing import Optional
from fastapi import Depends, Header, HTTPException, status

from app.core.database import get_db
from app.core.security import decode_token
from sqlalchemy.ext.asyncio import AsyncSession


async def get_current_user_id(
    authorization: Optional[str] = Header(None),
) -> Optional[str]:
    """
    Get current user ID from JWT token
    """
    if not authorization:
        return None

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None

        payload = decode_token(token)
        if payload and payload.get("type") == "access":
            return payload.get("sub")
    except Exception:
        return None

    return None


def require_auth(user_id: Optional[str] = Depends(get_current_user_id)) -> str:
    """
    Require authentication - raise 401 if not authenticated
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


class RoleChecker:
    """
    Role checker dependency
    """

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user_role: str) -> bool:
        """
        Check if user has required role
        """
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return True
