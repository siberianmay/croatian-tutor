"""Pydantic schemas for authentication."""

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Response schema for authentication tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Request schema for token refresh."""

    refresh_token: str


class UserRegister(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: str | None = Field(None, max_length=100)
    referral_code: str = Field(..., min_length=1)


class UserLogin(BaseModel):
    """Schema for user login (alternative to OAuth2 form)."""

    email: EmailStr
    password: str


class AuthUser(BaseModel):
    """Schema for authenticated user response."""

    id: int
    email: str
    name: str | None
    is_active: bool

    model_config = {"from_attributes": True}
