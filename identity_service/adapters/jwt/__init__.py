"""JWT token service implementation using Authlib."""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from authlib.jose import jwt, JoseError
from authlib.jose.rfc7517 import AsymmetricKey

from identity_service.ports.tokens import TokenService


class JWTTokenService(TokenService):
    """JWT-based token service using Authlib."""

    def __init__(
        self,
        private_key: AsymmetricKey,
        public_key: AsymmetricKey,
        algorithm: str = "RS256",
        issuer: str = "identity-service",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 30,
    ) -> None:
        self.private_key = private_key
        self.public_key = public_key
        self.algorithm = algorithm
        self.issuer = issuer
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(
        self,
        user_id: UUID,
        client_id: UUID,
        scopes: list[str],
        expires_delta: Optional[int] = None,
    ) -> tuple[str, datetime]:
        """Create a new access token."""
        expires_delta_minutes = expires_delta or self.access_token_expire_minutes
        expires_at = datetime.utcnow() + timedelta(minutes=expires_delta_minutes)

        payload = {
            "sub": str(user_id),
            "client_id": str(client_id),
            "scopes": scopes,
            "iss": self.issuer,
            "exp": int(expires_at.timestamp()),
            "iat": int(datetime.utcnow().timestamp()),
            "type": "access",
        }

        token = jwt.encode({"alg": self.algorithm}, payload, self.private_key)
        return token.decode("utf-8"), expires_at

    def create_refresh_token(
        self,
        user_id: UUID,
        client_id: UUID,
        scopes: list[str],
    ) -> str:
        """Create a new refresh token."""
        expires_at = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

        payload = {
            "sub": str(user_id),
            "client_id": str(client_id),
            "scopes": scopes,
            "iss": self.issuer,
            "exp": int(expires_at.timestamp()),
            "iat": int(datetime.utcnow().timestamp()),
            "type": "refresh",
        }

        token = jwt.encode({"alg": self.algorithm}, payload, self.private_key)
        return token.decode("utf-8")

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode a token."""
        try:
            claims = jwt.decode(token, self.public_key)
            claims.validate()
            return dict(claims)
        except JoseError:
            return None

    def decode_token(self, token: str) -> Optional[dict]:
        """Decode a token without verification."""
        try:
            claims = jwt.decode(token, self.public_key, claims_options={"verify_exp": False})
            return dict(claims)
        except JoseError:
            return None
