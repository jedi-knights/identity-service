"""Token service port interfaces."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID


class TokenService(ABC):
    """Port interface for token operations."""

    @abstractmethod
    def create_access_token(
        self,
        user_id: UUID,
        client_id: UUID,
        scopes: list[str],
        expires_delta: Optional[int] = None,
    ) -> tuple[str, datetime]:
        """Create a new access token. Returns (token, expiry_datetime)."""
        pass

    @abstractmethod
    def create_refresh_token(
        self,
        user_id: UUID,
        client_id: UUID,
        scopes: list[str],
    ) -> str:
        """Create a new refresh token."""
        pass

    @abstractmethod
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode a token. Returns token payload if valid."""
        pass

    @abstractmethod
    def decode_token(self, token: str) -> Optional[dict]:
        """Decode a token without verification."""
        pass
