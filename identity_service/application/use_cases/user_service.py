"""User service use cases."""
import secrets
from typing import Optional
from uuid import UUID

from passlib.context import CryptContext

from identity_service.domain.entities import User
from identity_service.ports.repositories import UserRepository


class UserService:
    """Service for user-related operations."""

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """Hash a password."""
        # Bcrypt has a 72-byte limit, truncate if necessary
        return self.pwd_context.hash(password[:72])

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    async def create_user(self, username: str, email: str, password: str) -> User:
        """Create a new user."""
        # Check if username or email already exists
        existing_user = await self.user_repository.get_by_username(username)
        if existing_user:
            raise ValueError(f"Username '{username}' already exists")

        existing_email = await self.user_repository.get_by_email(email)
        if existing_email:
            raise ValueError(f"Email '{email}' already exists")

        # Create user with hashed password
        hashed_password = self.hash_password(password)
        user = User(username=username, email=email, hashed_password=hashed_password)

        return await self.user_repository.create(user)

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password."""
        user = await self.user_repository.get_by_username(username)
        if not user:
            return None

        if not self.verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID."""
        return await self.user_repository.get_by_id(user_id)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return await self.user_repository.get_by_username(username)

    async def update_user_password(self, user_id: UUID, new_password: str) -> User:
        """Update a user's password."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        hashed_password = self.hash_password(new_password)
        user.update_password(hashed_password)

        return await self.user_repository.update(user)

    async def deactivate_user(self, user_id: UUID) -> User:
        """Deactivate a user."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        user.deactivate()
        return await self.user_repository.update(user)

    async def activate_user(self, user_id: UUID) -> User:
        """Activate a user."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        user.activate()
        return await self.user_repository.update(user)
