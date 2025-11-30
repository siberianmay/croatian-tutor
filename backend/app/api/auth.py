"""Authentication API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    verify_password,
)
from app.api.dependencies import get_current_user
from app.config import settings
from app.crud.user import UserCRUD
from app.database import get_db
from app.models.user import User
from app.schemas.auth import AuthUser, Token, TokenRefresh, UserLogin, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_crud(db: Annotated[AsyncSession, Depends(get_db)]) -> UserCRUD:
    """Dependency for UserCRUD."""
    return UserCRUD(db)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserRegister,
    crud: Annotated[UserCRUD, Depends(get_user_crud)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    Register a new user account.

    Requires valid referral code. Creates the user and returns access/refresh tokens.
    """
    # Validate referral code
    if not settings.REFERRAL_CODE or user_in.referral_code != settings.REFERRAL_CODE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid referral code",
        )

    # Check if email already exists
    existing_user = await crud.get_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = await crud.create(user_in)
    await db.commit()

    # Generate tokens
    token_data = {"sub": str(user.id)}
    return Token(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    crud: Annotated[UserCRUD, Depends(get_user_crud)],
) -> Token:
    """
    Authenticate user and return tokens.

    Accepts JSON body with email and password.
    """
    # Find user by email
    user = await crud.get_by_email(credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate tokens
    token_data = {"sub": str(user.id)}
    return Token(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    crud: Annotated[UserCRUD, Depends(get_user_crud)],
) -> Token:
    """
    Refresh access token using refresh token.

    Returns new access and refresh tokens.
    """
    # Decode and validate refresh token
    payload = decode_refresh_token(token_data.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user ID from token
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user still exists and is active
    user = await crud.get(int(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate new tokens
    new_token_data = {"sub": str(user.id)}
    return Token(
        access_token=create_access_token(new_token_data),
        refresh_token=create_refresh_token(new_token_data),
    )


@router.get("/me", response_model=AuthUser)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> AuthUser:
    """
    Get current authenticated user info.

    Requires valid access token.
    """
    return AuthUser.model_validate(current_user)
