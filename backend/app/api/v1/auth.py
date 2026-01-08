"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.crud.user import (
    create_user,
    authenticate_user,
    get_user,
    update_user,
    get_user_by_email,
    get_user_by_username,
    get_user_stats,
)
from app.schemas.user import (
    UserCreate,
    UserLogin,
    AuthResponse,
    TokenResponse,
    UserProfile,
    ChangePassword,
    UserUpdate as UserUpdateSchema,
)
from app.middlewares.auth import get_current_user

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user
    """
    # Check if email already exists
    existing_user = await get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username already exists
    existing_username = await get_user_by_username(db, data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Create user
    user = await create_user(db, data)

    # Create tokens
    token_data = {"sub": user.id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Get user stats
    stats = await get_user_stats(db, user.id)

    # Build user profile with stats
    user_profile = UserProfile.model_validate(user)
    user_profile.followers_count = stats["followers_count"]
    user_profile.following_count = stats["following_count"]
    user_profile.articles_count = stats["articles_count"]

    return AuthResponse(
        user=user_profile,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Login user
    """
    user = await authenticate_user(db, data.email, data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # Create tokens
    token_data = {"sub": user.id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Get user stats
    stats = await get_user_stats(db, user.id)

    # Build user profile with stats
    user_profile = UserProfile.model_validate(user)
    user_profile.followers_count = stats["followers_count"]
    user_profile.following_count = stats["following_count"]
    user_profile.articles_count = stats["articles_count"]

    return AuthResponse(
        user=user_profile,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token
    """
    from app.core.security import decode_token

    payload = decode_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    user = await get_user(db, user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Create new access token
    token_data = {"sub": user.id}
    access_token = create_access_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current authenticated user
    """
    # Get user stats
    stats = await get_user_stats(db, current_user.id)

    # Build user profile with stats
    user_profile = UserProfile.model_validate(current_user)
    user_profile.followers_count = stats["followers_count"]
    user_profile.following_count = stats["following_count"]
    user_profile.articles_count = stats["articles_count"]

    return user_profile


@router.put("/me", response_model=UserProfile)
async def update_current_user_profile(
    user_in: UserUpdateSchema,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user profile
    """
    user = await update_user(db, current_user, user_in)

    # Get user stats
    stats = await get_user_stats(db, user.id)

    # Build user profile with stats
    user_profile = UserProfile.model_validate(user)
    user_profile.followers_count = stats["followers_count"]
    user_profile.following_count = stats["following_count"]
    user_profile.articles_count = stats["articles_count"]

    return user_profile


@router.post("/change-password")
async def change_password(
    data: ChangePassword,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change user password
    """
    from app.core.security import verify_password, get_password_hash

    # Verify old password
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )

    # Update password
    current_user.hashed_password = get_password_hash(data.new_password)
    await db.flush()

    return {"success": True, "message": "Password changed successfully"}
