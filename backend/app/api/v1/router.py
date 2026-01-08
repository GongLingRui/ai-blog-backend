"""
API v1 Router - aggregates all API endpoints
"""
from fastapi import APIRouter

from app.api.v1 import (
    auth,
    users,
    articles,
    categories,
    tags,
    comments,
    likes,
    bookmarks,
    follows,
    upload,
)

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(articles.router, prefix="/articles", tags=["Articles"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(tags.router, prefix="/tags", tags=["Tags"])
api_router.include_router(comments.router, prefix="/comments", tags=["Comments"])
api_router.include_router(likes.router, prefix="/likes", tags=["Likes"])
api_router.include_router(bookmarks.router, prefix="/bookmarks", tags=["Bookmarks"])
api_router.include_router(follows.router, prefix="/follows", tags=["Follows"])
api_router.include_router(upload.router, prefix="/upload", tags=["Upload"])

# TODO: Add more routers
# api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
# api_router.include_router(papers.router, prefix="/papers", tags=["Papers"])
