"""Security utilities for authentication and authorization."""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing token payload (must include 'sub' for user_id)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token with longer expiration.

    Args:
        data: Dictionary containing token payload (must include 'sub' for user_id)

    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict | None:
    """
    Decode and validate a JWT token.

    Args:
        token: The JWT token string to decode

    Returns:
        Token payload dictionary if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def decode_access_token(token: str) -> dict | None:
    """
    Decode and validate an access token specifically.

    Args:
        token: The JWT token string to decode

    Returns:
        Token payload if valid access token, None otherwise
    """
    payload = decode_token(token)
    if payload and payload.get("type") == "access":
        return payload
    return None


def decode_refresh_token(token: str) -> dict | None:
    """
    Decode and validate a refresh token specifically.

    Args:
        token: The JWT token string to decode

    Returns:
        Token payload if valid refresh token, None otherwise
    """
    payload = decode_token(token)
    if payload and payload.get("type") == "refresh":
        return payload
    return None
