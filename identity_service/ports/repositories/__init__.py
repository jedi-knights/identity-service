"""Repository port interfaces."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from identity_service.domain.entities import User, Client, Token, AuthorizationCode


class UserRepository(ABC):
    """Port interface for user persistence."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user."""
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete a user."""
        pass


class ClientRepository(ABC):
    """Port interface for OAuth2 client persistence."""

    @abstractmethod
    async def create(self, client: Client) -> Client:
        """Create a new client."""
        pass

    @abstractmethod
    async def get_by_id(self, client_id: UUID) -> Optional[Client]:
        """Get client by ID."""
        pass

    @abstractmethod
    async def update(self, client: Client) -> Client:
        """Update an existing client."""
        pass

    @abstractmethod
    async def delete(self, client_id: UUID) -> bool:
        """Delete a client."""
        pass


class TokenRepository(ABC):
    """Port interface for token persistence."""

    @abstractmethod
    async def create(self, token: Token) -> Token:
        """Create a new token."""
        pass

    @abstractmethod
    async def get_by_access_token(self, access_token: str) -> Optional[Token]:
        """Get token by access token value."""
        pass

    @abstractmethod
    async def get_by_refresh_token(self, refresh_token: str) -> Optional[Token]:
        """Get token by refresh token value."""
        pass

    @abstractmethod
    async def revoke(self, token_id: UUID) -> bool:
        """Revoke a token."""
        pass


class AuthorizationCodeRepository(ABC):
    """Port interface for authorization code persistence."""

    @abstractmethod
    async def create(self, auth_code: AuthorizationCode) -> AuthorizationCode:
        """Create a new authorization code."""
        pass

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[AuthorizationCode]:
        """Get authorization code by code value."""
        pass

    @abstractmethod
    async def mark_as_used(self, code_id: UUID) -> bool:
        """Mark an authorization code as used."""
        pass

    @abstractmethod
    async def delete(self, code_id: UUID) -> bool:
        """Delete an authorization code."""
        pass

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Delete expired authorization codes and return count deleted."""
        pass
