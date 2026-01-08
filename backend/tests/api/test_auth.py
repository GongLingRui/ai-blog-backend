"""
Test Authentication API endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Test successful user registration"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["username"] == "newuser"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    """Test registration with duplicate email"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "different",
            "email": test_user.email,
            "password": "password123"
        }
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient, test_user):
    """Test registration with duplicate username"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": test_user.username,
            "email": "different@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 400
    assert "already taken" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "testpass123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == test_user.email


@pytest.mark.asyncio
async def test_login_wrong_email(client: AsyncClient):
    """Test login with wrong email"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 401
    assert "Incorrect" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    """Test login with wrong password"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401
    assert "Incorrect" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, user_headers):
    """Test getting current authenticated user"""
    response = await client.get(
        "/api/v1/auth/me",
        headers=user_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert "username" in data


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test getting current user without authentication"""
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient, user_headers):
    """Test updating user profile"""
    response = await client.put(
        "/api/v1/auth/me",
        headers=user_headers,
        json={
            "full_name": "Updated Name",
            "bio": "Updated bio"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["bio"] == "Updated bio"


@pytest.mark.asyncio
async def test_change_password_success(client: AsyncClient, user_headers):
    """Test changing password successfully"""
    response = await client.post(
        "/api/v1/auth/change-password",
        headers=user_headers,
        json={
            "old_password": "testpass123",
            "new_password": "newpassword123"
        }
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_change_password_wrong_old(client: AsyncClient, user_headers):
    """Test changing password with wrong old password"""
    response = await client.post(
        "/api/v1/auth/change-password",
        headers=user_headers,
        json={
            "old_password": "wrongpassword",
            "new_password": "newpassword123"
        }
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, test_user):
    """Test refreshing access token"""
    # First login to get refresh token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "testpass123"
        }
    )
    refresh_token = login_response.json()["refresh_token"]

    # Use refresh token to get new access token
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient):
    """Test refreshing with invalid token"""
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.token.here"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, user_headers):
    """Test logout"""
    response = await client.post(
        "/api/v1/auth/logout",
        headers=user_headers
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_request_password_reset(client: AsyncClient, test_user):
    """Test requesting password reset"""
    response = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": test_user.email}
    )

    # Should succeed even if email doesn't exist (security best practice)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_reset_password(client: AsyncClient):
    """Test resetting password with token"""
    # This would require a valid reset token from email
    # For now, test with invalid token
    response = await client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": "invalid_token",
            "new_password": "newpassword123"
        }
    )

    # Should fail with invalid token
    assert response.status_code in [400, 401]


@pytest.mark.asyncio
async def test_delete_account(client: AsyncClient, user_headers):
    """Test deleting user account"""
    response = await client.delete(
        "/api/v1/auth/me",
        headers=user_headers
    )

    assert response.status_code == 204 or response.status_code == 200


@pytest.mark.asyncio
async def test_verify_email(client: AsyncClient):
    """Test email verification"""
    # This would require a valid verification token from email
    response = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": "invalid_token"}
    )

    # Should fail with invalid token
    assert response.status_code in [400, 404]


@pytest.mark.asyncio
async def test_resend_verification_email(client: AsyncClient, user_headers):
    """Test resending verification email"""
    response = await client.post(
        "/api/v1/auth/resend-verification",
        headers=user_headers
    )

    assert response.status_code == 200
