"""Domain entities for the identity service."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class User:
    """User entity representing an authenticated user."""

    def __init__(
        self,
        username: str,
        email: str,
        hashed_password: str,
        user_id: Optional[UUID] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self.id = user_id or uuid4()
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def update_password(self, new_hashed_password: str) -> None:
        """Update the user's password."""
        self.hashed_password = new_hashed_password
        self.updated_at = datetime.utcnow()


class Client:
    """OAuth2 client entity."""

    def __init__(
        self,
        client_name: str,
        client_secret_hash: str,
        redirect_uris: list[str],
        grant_types: list[str],
        client_id: Optional[UUID] = None,
        scopes: Optional[list[str]] = None,
        is_confidential: bool = True,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self.id = client_id or uuid4()
        self.client_name = client_name
        self.client_secret_hash = client_secret_hash
        self.redirect_uris = redirect_uris
        self.grant_types = grant_types
        self.scopes = scopes or []
        self.is_confidential = is_confidential
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def validate_redirect_uri(self, redirect_uri: str) -> bool:
        """Check if the redirect URI is registered for this client."""
        return redirect_uri in self.redirect_uris

    def validate_grant_type(self, grant_type: str) -> bool:
        """Check if the grant type is allowed for this client."""
        return grant_type in self.grant_types

    def deactivate(self) -> None:
        """Deactivate the client."""
        self.is_active = False
        self.updated_at = datetime.utcnow()


class Token:
    """Access token entity."""

    def __init__(
        self,
        user_id: UUID,
        client_id: UUID,
        access_token: str,
        token_type: str,
        expires_at: datetime,
        scopes: list[str],
        token_id: Optional[UUID] = None,
        refresh_token: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        self.id = token_id or uuid4()
        self.user_id = user_id
        self.client_id = client_id
        self.access_token = access_token
        self.token_type = token_type
        self.expires_at = expires_at
        self.scopes = scopes
        self.refresh_token = refresh_token
        self.created_at = created_at or datetime.utcnow()

    def is_expired(self) -> bool:
        """Check if the token has expired."""
        return datetime.utcnow() > self.expires_at
