"""Database connection management."""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from identity_service.infrastructure.config.settings import Settings


class DatabaseConnection:
    """Database connection manager."""

    def __init__(self, settings: Settings) -> None:
        self.engine = create_async_engine(
            settings.database_url, echo=settings.db_echo, future=True
        )
        self.async_session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session."""
        async with self.async_session_factory() as session:
            yield session

    async def close(self) -> None:
        """Close the database connection."""
        await self.engine.dispose()
