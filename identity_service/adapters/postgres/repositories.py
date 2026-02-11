"""PostgreSQL repository implementations."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from identity_service.domain.entities import User, Client, Token
from identity_service.infrastructure.database.models import UserModel, ClientModel, TokenModel
from identity_service.ports.repositories import (
    UserRepository,
    ClientRepository,
    TokenRepository,
)


class PostgresUserRepository(UserRepository):
    """PostgreSQL implementation of UserRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_entity(self, model: UserModel) -> User:
        """Convert database model to domain entity."""
        return User(
            username=model.username,
            email=model.email,
            hashed_password=model.hashed_password,
            user_id=model.id,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: User) -> UserModel:
        """Convert domain entity to database model."""
        return UserModel(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            hashed_password=entity.hashed_password,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, user: User) -> User:
        """Create a new user."""
        model = self._to_model(user)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, user: User) -> User:
        """Update an existing user."""
        model = await self.session.get(UserModel, user.id)
        if not model:
            raise ValueError(f"User with id {user.id} not found")

        model.username = user.username
        model.email = user.email
        model.hashed_password = user.hashed_password
        model.is_active = user.is_active
        model.updated_at = user.updated_at

        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def delete(self, user_id: UUID) -> bool:
        """Delete a user."""
        model = await self.session.get(UserModel, user_id)
        if not model:
            return False

        await self.session.delete(model)
        await self.session.commit()
        return True


class PostgresClientRepository(ClientRepository):
    """PostgreSQL implementation of ClientRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_entity(self, model: ClientModel) -> Client:
        """Convert database model to domain entity."""
        return Client(
            client_name=model.client_name,
            client_secret_hash=model.client_secret_hash,
            redirect_uris=model.redirect_uris,
            grant_types=model.grant_types,
            client_id=model.id,
            scopes=model.scopes,
            is_confidential=model.is_confidential,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Client) -> ClientModel:
        """Convert domain entity to database model."""
        return ClientModel(
            id=entity.id,
            client_name=entity.client_name,
            client_secret_hash=entity.client_secret_hash,
            redirect_uris=entity.redirect_uris,
            grant_types=entity.grant_types,
            scopes=entity.scopes,
            is_confidential=entity.is_confidential,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, client: Client) -> Client:
        """Create a new client."""
        model = self._to_model(client)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, client_id: UUID) -> Optional[Client]:
        """Get client by ID."""
        model = await self.session.get(ClientModel, client_id)
        return self._to_entity(model) if model else None

    async def update(self, client: Client) -> Client:
        """Update an existing client."""
        model = await self.session.get(ClientModel, client.id)
        if not model:
            raise ValueError(f"Client with id {client.id} not found")

        model.client_name = client.client_name
        model.client_secret_hash = client.client_secret_hash
        model.redirect_uris = client.redirect_uris
        model.grant_types = client.grant_types
        model.scopes = client.scopes
        model.is_confidential = client.is_confidential
        model.is_active = client.is_active
        model.updated_at = client.updated_at

        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def delete(self, client_id: UUID) -> bool:
        """Delete a client."""
        model = await self.session.get(ClientModel, client_id)
        if not model:
            return False

        await self.session.delete(model)
        await self.session.commit()
        return True


class PostgresTokenRepository(TokenRepository):
    """PostgreSQL implementation of TokenRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_entity(self, model: TokenModel) -> Token:
        """Convert database model to domain entity."""
        return Token(
            user_id=model.user_id,
            client_id=model.client_id,
            access_token=model.access_token,
            token_type=model.token_type,
            expires_at=model.expires_at,
            scopes=model.scopes,
            token_id=model.id,
            refresh_token=model.refresh_token,
            created_at=model.created_at,
        )

    def _to_model(self, entity: Token) -> TokenModel:
        """Convert domain entity to database model."""
        return TokenModel(
            id=entity.id,
            user_id=entity.user_id,
            client_id=entity.client_id,
            access_token=entity.access_token,
            token_type=entity.token_type,
            expires_at=entity.expires_at,
            scopes=entity.scopes,
            refresh_token=entity.refresh_token,
            created_at=entity.created_at,
        )

    async def create(self, token: Token) -> Token:
        """Create a new token."""
        model = self._to_model(token)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_access_token(self, access_token: str) -> Optional[Token]:
        """Get token by access token value."""
        result = await self.session.execute(
            select(TokenModel).where(TokenModel.access_token == access_token)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_refresh_token(self, refresh_token: str) -> Optional[Token]:
        """Get token by refresh token value."""
        result = await self.session.execute(
            select(TokenModel).where(TokenModel.refresh_token == refresh_token)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def revoke(self, token_id: UUID) -> bool:
        """Revoke a token."""
        model = await self.session.get(TokenModel, token_id)
        if not model:
            return False

        await self.session.delete(model)
        await self.session.commit()
        return True
