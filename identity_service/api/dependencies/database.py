"""Database session dependency."""
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from identity_service.infrastructure.container import Container


async def get_db_session(
    container: Container = Depends(lambda: Container()),
) -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    db = container.database()
    async for session in db.get_session():
        yield session
