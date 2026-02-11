"""Domain entities for the identity service."""

from datetime import datetime, timezone
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
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)

    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)

    def update_password(self, new_hashed_password: str) -> None:
        """Update the user's password."""
        self.hashed_password = new_hashed_password
        self.updated_at = datetime.now(timezone.utc)


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
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    def validate_redirect_uri(self, redirect_uri: str) -> bool:
        """Check if the redirect URI is registered for this client."""
        return redirect_uri in self.redirect_uris

    def validate_grant_type(self, grant_type: str) -> bool:
        """Check if the grant type is allowed for this client."""
        return grant_type in self.grant_types

    def deactivate(self) -> None:
        """Deactivate the client."""
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)


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
        self.created_at = created_at or datetime.now(timezone.utc)

    def is_expired(self) -> bool:
        """Check if the token has expired."""
        return datetime.now(timezone.utc) > self.expires_at


class AuthorizationCode:
    """Authorization code entity for OAuth2 authorization code flow."""

    def __init__(
        self,
        code: str,
        client_id: UUID,
        redirect_uri: str,
        scopes: list[str],
        expires_at: datetime,
        user_id: Optional[UUID] = None,
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
        state: Optional[str] = None,
        code_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        is_used: bool = False,
    ) -> None:
        self.id = code_id or uuid4()
        self.code = code
        self.client_id = client_id
        self.user_id = user_id
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.code_challenge = code_challenge
        self.code_challenge_method = code_challenge_method
        self.state = state
        self.expires_at = expires_at
        self.is_used = is_used
        self.created_at = created_at or datetime.now(timezone.utc)

    def is_expired(self) -> bool:
        """Check if the authorization code has expired."""
        return datetime.now(timezone.utc) > self.expires_at

    def mark_as_used(self) -> None:
        """Mark the authorization code as used."""
        self.is_used = True

    def validate_pkce(self, code_verifier: str) -> bool:
        """Validate PKCE code_verifier against stored code_challenge."""
        if not self.code_challenge:
            return True

        if self.code_challenge_method == "S256":
            import hashlib
            import base64

            computed_challenge = (
                base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
                .decode()
                .rstrip("=")
            )
            return computed_challenge == self.code_challenge
        elif self.code_challenge_method == "plain":
            return code_verifier == self.code_challenge
        else:
            return False
