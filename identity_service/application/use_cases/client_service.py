"""Client service use cases."""
import secrets
from typing import Optional
from uuid import UUID

from passlib.context import CryptContext

from identity_service.domain.entities import Client
from identity_service.ports.repositories import ClientRepository


class ClientService:
    """Service for OAuth2 client-related operations."""

    def __init__(self, client_repository: ClientRepository) -> None:
        self.client_repository = client_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def generate_client_secret(self) -> str:
        """Generate a secure client secret."""
        return secrets.token_urlsafe(32)

    def hash_secret(self, secret: str) -> str:
        """Hash a client secret."""
        return self.pwd_context.hash(secret)

    def verify_secret(self, plain_secret: str, hashed_secret: str) -> bool:
        """Verify a client secret against a hash."""
        return self.pwd_context.verify(plain_secret, hashed_secret)

    async def create_client(
        self,
        client_name: str,
        redirect_uris: list[str],
        grant_types: list[str],
        scopes: Optional[list[str]] = None,
        is_confidential: bool = True,
    ) -> tuple[Client, str]:
        """Create a new OAuth2 client. Returns (client, plain_secret)."""
        # Generate and hash client secret
        plain_secret = self.generate_client_secret()
        hashed_secret = self.hash_secret(plain_secret)

        # Create client entity
        client = Client(
            client_name=client_name,
            client_secret_hash=hashed_secret,
            redirect_uris=redirect_uris,
            grant_types=grant_types,
            scopes=scopes or [],
            is_confidential=is_confidential,
        )

        created_client = await self.client_repository.create(client)
        return created_client, plain_secret

    async def get_client_by_id(self, client_id: UUID) -> Optional[Client]:
        """Get a client by ID."""
        return await self.client_repository.get_by_id(client_id)

    async def authenticate_client(self, client_id: UUID, client_secret: str) -> Optional[Client]:
        """Authenticate a client by ID and secret."""
        client = await self.client_repository.get_by_id(client_id)
        if not client:
            return None

        if not client.is_active:
            return None

        if not self.verify_secret(client_secret, client.client_secret_hash):
            return None

        return client

    async def validate_client_grant(
        self, client_id: UUID, grant_type: str, redirect_uri: Optional[str] = None
    ) -> bool:
        """Validate client grant type and redirect URI."""
        client = await self.client_repository.get_by_id(client_id)
        if not client or not client.is_active:
            return False

        if not client.validate_grant_type(grant_type):
            return False

        if redirect_uri and not client.validate_redirect_uri(redirect_uri):
            return False

        return True

    async def deactivate_client(self, client_id: UUID) -> Client:
        """Deactivate a client."""
        client = await self.client_repository.get_by_id(client_id)
        if not client:
            raise ValueError(f"Client with id {client_id} not found")

        client.deactivate()
        return await self.client_repository.update(client)
