"""OAuth2 service use cases."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from identity_service.application.use_cases.client_service import ClientService
from identity_service.application.use_cases.user_service import UserService
from identity_service.domain.entities import Token
from identity_service.ports.cache import CachePort
from identity_service.ports.repositories import TokenRepository
from identity_service.ports.tokens import TokenService


class OAuth2Service:
    """Service for OAuth2 operations."""

    def __init__(
        self,
        user_service: UserService,
        client_service: ClientService,
        token_service: TokenService,
        token_repository: TokenRepository,
        cache: CachePort,
    ) -> None:
        self.user_service = user_service
        self.client_service = client_service
        self.token_service = token_service
        self.token_repository = token_repository
        self.cache = cache

    async def password_grant(
        self,
        username: str,
        password: str,
        client_id: UUID,
        client_secret: str,
        scopes: Optional[list[str]] = None,
    ) -> Optional[Token]:
        """Handle password grant flow."""
        # Authenticate client
        client = await self.client_service.authenticate_client(client_id, client_secret)
        if not client:
            return None

        # Validate grant type
        if not client.validate_grant_type("password"):
            return None

        # Authenticate user
        user = await self.user_service.authenticate_user(username, password)
        if not user:
            return None

        # Use requested scopes or default to client scopes
        token_scopes = scopes or client.scopes

        # Create tokens
        access_token, expires_at = self.token_service.create_access_token(
            user.id, client.id, token_scopes
        )
        refresh_token = self.token_service.create_refresh_token(user.id, client.id, token_scopes)

        # Store token
        token = Token(
            user_id=user.id,
            client_id=client.id,
            access_token=access_token,
            token_type="Bearer",
            expires_at=expires_at,
            scopes=token_scopes,
            refresh_token=refresh_token,
        )

        return await self.token_repository.create(token)

    async def refresh_token_grant(
        self, refresh_token: str, client_id: UUID, client_secret: str
    ) -> Optional[Token]:
        """Handle refresh token grant flow."""
        # Authenticate client
        client = await self.client_service.authenticate_client(client_id, client_secret)
        if not client:
            return None

        # Validate grant type
        if not client.validate_grant_type("refresh_token"):
            return None

        # Verify refresh token
        token_payload = self.token_service.verify_token(refresh_token)
        if not token_payload or token_payload.get("type") != "refresh":
            return None

        # Get existing token
        existing_token = await self.token_repository.get_by_refresh_token(refresh_token)
        if not existing_token:
            return None

        # Revoke old token
        await self.token_repository.revoke(existing_token.id)

        # Create new tokens
        user_id = UUID(token_payload["sub"])
        scopes = token_payload.get("scopes", [])

        access_token, expires_at = self.token_service.create_access_token(
            user_id, client.id, scopes
        )
        new_refresh_token = self.token_service.create_refresh_token(user_id, client.id, scopes)

        # Store new token
        token = Token(
            user_id=user_id,
            client_id=client.id,
            access_token=access_token,
            token_type="Bearer",
            expires_at=expires_at,
            scopes=scopes,
            refresh_token=new_refresh_token,
        )

        return await self.token_repository.create(token)

    async def introspect_token(self, token: str) -> Optional[dict]:
        """Introspect a token and return its details."""
        # Try to get from cache first
        cache_key = f"token:introspect:{token}"
        cached = await self.cache.get(cache_key)
        if cached:
            return {"active": True}

        # Verify token
        payload = self.token_service.verify_token(token)
        if not payload:
            return {"active": False}

        # Check if token exists in database
        token_entity = await self.token_repository.get_by_access_token(token)
        if not token_entity or token_entity.is_expired():
            return {"active": False}

        # Cache the result
        ttl = int((token_entity.expires_at - datetime.utcnow()).total_seconds())
        if ttl > 0:
            await self.cache.set(cache_key, "1", ttl)

        return {
            "active": True,
            "scope": " ".join(payload.get("scopes", [])),
            "client_id": payload.get("client_id"),
            "username": payload.get("sub"),
            "token_type": "Bearer",
            "exp": payload.get("exp"),
            "iat": payload.get("iat"),
            "sub": payload.get("sub"),
        }

    async def revoke_token(self, token: str) -> bool:
        """Revoke a token."""
        token_entity = await self.token_repository.get_by_access_token(token)
        if not token_entity:
            return False

        # Delete from cache
        cache_key = f"token:introspect:{token}"
        await self.cache.delete(cache_key)

        # Revoke from database
        return await self.token_repository.revoke(token_entity.id)
