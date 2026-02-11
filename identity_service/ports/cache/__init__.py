"""Cache port interface."""
from abc import ABC, abstractmethod
from typing import Optional


class CachePort(ABC):
    """Port interface for caching operations."""

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: str, expiry_seconds: Optional[int] = None) -> bool:
        """Set value in cache with optional expiry."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass
