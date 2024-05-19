"""Cache-related services and implementations, designed for fast data lookup."""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
import time

class CacheService(ABC):
    """CacheService provides basic key-value cache storage."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Looks up value for the specified key."""

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Assigns value to the specified key."""

    @abstractmethod
    def set_ttl(self, key: str, ttl: Optional[int]) -> None:
        """Assigns TTL to the specified key."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Deletes the specified key."""


def get_cache_service() -> CacheService:
    """Dependency factory to create instance of CacheService."""
    return InMemoryCacheService()


class InMemoryCacheService(CacheService):
    """
    A very basic in-memory dictionary-based CacheService implementation.
    Only suitable for testing or running in development environment.
    """

    def __init__(self) -> None:
        self._mem: Dict[str, Any] = {}
        self._ttl: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Any]:
        expire_at = self._ttl.get(key, None)
        time_now = time.time()
        if expire_at is not None and expire_at <= time_now:
            self.delete(key)
            return None
        return self._mem.get(key, None)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self._mem[key] = value
        if ttl is not None:
            self.set_ttl(key, ttl)

    def set_ttl(self, key: str, ttl: Optional[int]) -> None:
        if ttl is None or ttl == 0:
            self._ttl.pop(key, None)
        else:
            self._ttl[key] = time.time() + ttl

    def delete(self, key: str) -> None:
        self._mem.pop(key, None)
