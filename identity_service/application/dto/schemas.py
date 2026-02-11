"""Data Transfer Objects (DTOs) for API layer."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# User DTOs
class UserCreate(BaseModel):
    """Schema for creating a user."""

    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    """Schema for user response."""

    id: UUID
    username: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


# Client DTOs
class ClientCreate(BaseModel):
    """Schema for creating an OAuth2 client."""

    client_name: str = Field(..., min_length=1, max_length=255)
    redirect_uris: list[str] = Field(..., min_length=1)
    grant_types: list[str] = Field(..., min_length=1)
    scopes: Optional[list[str]] = None
    is_confidential: bool = True


class ClientResponse(BaseModel):
    """Schema for client response."""

    id: UUID
    client_name: str
    redirect_uris: list[str]
    grant_types: list[str]
    scopes: list[str]
    is_confidential: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientWithSecret(BaseModel):
    """Schema for client response with secret (only shown on creation)."""

    id: UUID
    client_name: str
    client_secret: str
    redirect_uris: list[str]
    grant_types: list[str]
    scopes: list[str]
    is_confidential: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


# Token DTOs
class TokenRequest(BaseModel):
    """Schema for OAuth2 token request."""

    grant_type: str
    username: Optional[str] = None
    password: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    scope: Optional[str] = None


class TokenResponse(BaseModel):
    """Schema for OAuth2 token response."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class TokenIntrospection(BaseModel):
    """Schema for token introspection response."""

    active: bool
    scope: Optional[str] = None
    client_id: Optional[str] = None
    username: Optional[str] = None
    token_type: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    sub: Optional[str] = None
