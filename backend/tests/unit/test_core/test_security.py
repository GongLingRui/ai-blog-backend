"""
Test security functions (password hashing, JWT)
"""
import pytest
from datetime import timedelta, datetime
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)


def test_password_hashing():
    """Test password hashing and verification"""
    password = "test_password_123"
    hashed = get_password_hash(password)

    # Hash should be different from original password
    assert hashed != password
    assert len(hashed) > 50  # Bcrypt hashes are long

    # Verify correct password
    assert verify_password(password, hashed) is True

    # Verify incorrect password
    assert verify_password("wrong_password", hashed) is False


def test_password_hash_uniqueness():
    """Test that same password generates different hashes"""
    password = "same_password"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)

    # Bcrypt uses random salt, so hashes should be different
    assert hash1 != hash2

    # But both should verify correctly
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


def test_create_access_token():
    """Test creating access token"""
    data = {"sub": "user123", "username": "testuser"}
    token = create_access_token(data)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 50  # JWT tokens are long


def test_create_access_token_with_expiration():
    """Test creating access token with custom expiration"""
    data = {"sub": "user123"}
    expires = timedelta(minutes=30)
    token = create_access_token(data, expires_delta=expires)

    assert token is not None
    assert isinstance(token, str)


def test_create_refresh_token():
    """Test creating refresh token"""
    data = {"sub": "user123"}
    token = create_refresh_token(data)

    assert token is not None
    assert isinstance(token, str)


def test_decode_valid_token():
    """Test decoding valid token"""
    data = {"sub": "user123", "username": "testuser"}
    token = create_access_token(data)

    payload = decode_token(token)

    assert payload is not None
    assert payload["sub"] == "user123"
    assert payload["username"] == "testuser"
    assert "exp" in payload
    assert "type" in payload
    assert payload["type"] == "access"


def test_decode_refresh_token():
    """Test decoding refresh token"""
    data = {"sub": "user123"}
    token = create_refresh_token(data)

    payload = decode_token(token)

    assert payload is not None
    assert payload["sub"] == "user123"
    assert "exp" in payload
    assert payload["type"] == "refresh"


def test_decode_invalid_token():
    """Test decoding invalid token"""
    invalid_token = "invalid.token.here"
    payload = decode_token(invalid_token)

    assert payload is None


def test_decode_expired_token():
    """Test decoding expired token"""
    from jose import jwt
    from app.config import settings

    # Create expired token
    data = {"sub": "user123"}
    expire = datetime.utcnow() - timedelta(minutes=1)
    data.update({"exp": expire, "type": "access"})

    expired_token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    payload = decode_token(expired_token)
    assert payload is None


def test_token_expiration_time():
    """Test that access token expires at correct time"""
    from app.config import settings

    data = {"sub": "user123"}
    token = create_access_token(data)
    payload = decode_token(token)

    # Check expiration is approximately correct (within 1 minute)
    exp_timestamp = payload["exp"]
    expected_exp = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    time_diff = abs(expected_exp.timestamp() - exp_timestamp)
    assert time_diff < 60  # Within 1 minute


def test_token_contains_type():
    """Test that tokens include type field"""
    data = {"sub": "user123"}

    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)

    access_payload = decode_token(access_token)
    refresh_payload = decode_token(refresh_token)

    assert access_payload["type"] == "access"
    assert refresh_payload["type"] == "refresh"


def test_different_users_different_tokens():
    """Test that different users get different tokens"""
    token1 = create_access_token({"sub": "user1"})
    token2 = create_access_token({"sub": "user2"})

    assert token1 != token2

    payload1 = decode_token(token1)
    payload2 = decode_token(token2)

    assert payload1["sub"] == "user1"
    assert payload2["sub"] == "user2"


def test_empty_password_hash():
    """Test hashing empty password"""
    password = ""
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("", hashed) is True


def test_complex_password():
    """Test hashing complex password with special characters"""
    password = "P@ssw0rd!#$%^&*()_+-=[]{}|;':\",./<>?"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True
    assert verify_password("P@ssw0rd!", hashed) is False


def test_unicode_password():
    """Test hashing password with unicode characters"""
    password = "密码123🔐"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True
    assert verify_password("密码123", hashed) is False
