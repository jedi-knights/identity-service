"""OAuth2 service use cases."""

import hashlib
import secrets
from base64 import urlsafe_b64encode
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from identity_service.application.use_cases.client_service import ClientService
from identity_service.application.use_cases.user_service import UserService
from identity_service.domain.entities import Token, AuthorizationCode
from identity_service.ports.cache import CachePort
from identity_service.ports.repositories import TokenRepository, AuthorizationCodeRepository
from identity_service.ports.tokens import TokenService


class OAuth2Service:
    """Service for OAuth2 operations."""

    def __init__(
        self,
        user_service: UserService,
        client_service: ClientService,
        token_service: TokenService,
        token_repository: TokenRepository,
        authorization_code_repository: AuthorizationCodeRepository,
        cache: CachePort,
    ) -> None:
        self.user_service = user_service
        self.client_service = client_service
        self.token_service = token_service
        self.token_repository = token_repository
        self.authorization_code_repository = authorization_code_repository
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
        ttl = int((token_entity.expires_at - datetime.now(timezone.utc)).total_seconds())
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

    async def revoke_token(self, token: str, token_type_hint: Optional[str] = None) -> bool:
        """Revoke a token (RFC 7009)."""
        token_entity = None

        if token_type_hint == "refresh_token":
            token_entity = await self.token_repository.get_by_refresh_token(token)
            if not token_entity:
                token_entity = await self.token_repository.get_by_access_token(token)
        else:
            token_entity = await self.token_repository.get_by_access_token(token)
            if not token_entity:
                token_entity = await self.token_repository.get_by_refresh_token(token)

        if not token_entity:
            return True

        cache_key = f"token:introspect:{token}"
        await self.cache.delete(cache_key)

        return await self.token_repository.revoke(token_entity.id)

    async def create_authorization_code(
        self,
        client_id: UUID,
        user_id: UUID,
        redirect_uri: str,
        scopes: list[str],
        state: Optional[str] = None,
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
    ) -> AuthorizationCode:
        """Create an authorization code for the authorization code flow."""
        code = urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        auth_code = AuthorizationCode(
            code=code,
            client_id=client_id,
            user_id=user_id,
            redirect_uri=redirect_uri,
            scopes=scopes,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            expires_at=expires_at,
        )

        return await self.authorization_code_repository.create(auth_code)

    async def authorization_code_grant(
        self,
        code: str,
        client_id: UUID,
        client_secret: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None,
    ) -> Optional[Token]:
        """Handle authorization code grant flow (RFC 6749 Section 4.1)."""
        client = await self.client_service.authenticate_client(client_id, client_secret)
        if not client:
            return None

        if not client.validate_grant_type("authorization_code"):
            return None

        auth_code = await self.authorization_code_repository.get_by_code(code)
        if not auth_code:
            return None

        if auth_code.is_expired():
            await self.authorization_code_repository.delete(auth_code.id)
            return None

        if auth_code.is_used:
            await self.authorization_code_repository.delete(auth_code.id)
            return None

        if auth_code.client_id != client_id:
            return None

        if auth_code.redirect_uri != redirect_uri:
            return None

        if auth_code.code_challenge:
            if not code_verifier:
                return None
            if not auth_code.validate_pkce(code_verifier):
                return None

        await self.authorization_code_repository.mark_as_used(auth_code.id)

        if not auth_code.user_id:
            return None

        access_token, expires_at = self.token_service.create_access_token(
            auth_code.user_id, client.id, auth_code.scopes
        )
        refresh_token = self.token_service.create_refresh_token(
            auth_code.user_id, client.id, auth_code.scopes
        )

        token = Token(
            user_id=auth_code.user_id,
            client_id=client.id,
            access_token=access_token,
            token_type="Bearer",
            expires_at=expires_at,
            scopes=auth_code.scopes,
            refresh_token=refresh_token,
        )

        created_token = await self.token_repository.create(token)

        await self.authorization_code_repository.delete(auth_code.id)

        return created_token

    async def client_credentials_grant(
        self, client_id: UUID, client_secret: str, scopes: Optional[list[str]] = None
    ) -> Optional[Token]:
        """Handle client credentials grant flow (RFC 6749 Section 4.4)."""
        client = await self.client_service.authenticate_client(client_id, client_secret)
        if not client:
            return None

        if not client.validate_grant_type("client_credentials"):
            return None

        token_scopes = scopes or client.scopes

        access_token, expires_at = self.token_service.create_access_token(
            client.id, client.id, token_scopes
        )

        token = Token(
            user_id=client.id,
            client_id=client.id,
            access_token=access_token,
            token_type="Bearer",
            expires_at=expires_at,
            scopes=token_scopes,
            refresh_token=None,
        )

        return await self.token_repository.create(token)
