from __future__ import annotations
from typing import Any, overload
from collections.abc import Callable, Awaitable
from orionis.cache.locks.lock import CacheLock
from orionis.cache.repository import CacheRepository

class Cache:
    """Type stubs for the Cache facade."""

    # Store access
    @staticmethod
    def store(name: str | None = None) -> CacheRepository: ...

    # Core operations
    @staticmethod
    def get(key: str) -> Awaitable[Any]: ...
    @staticmethod
    def set(key: str, value: Any, ttl: float | None = None) -> Awaitable[bool]: ...
    @staticmethod
    def has(key: str) -> Awaitable[bool]: ...
    @staticmethod
    def delete(key: str) -> Awaitable[bool]: ...
    @staticmethod
    def clear() -> Awaitable[bool]: ...

    # Bulk operations
    @staticmethod
    def getMany(keys: list[str]) -> Awaitable[dict[str, Any]]: ...
    @staticmethod
    def setMany(values: dict[str, Any], ttl: float | None = None) -> Awaitable[bool]: ...

    # Convenience patterns
    @staticmethod
    def remember(key: str, ttl: float | None, resolver: Callable) -> Awaitable[Any]: ...
    @staticmethod
    def rememberForever(key: str, resolver: Callable) -> Awaitable[Any]: ...
    @staticmethod
    def pull(key: str) -> Awaitable[Any]: ...

    # Atomic operations
    @staticmethod
    def add(key: str, value: Any, ttl: float | None = None) -> Awaitable[bool]: ...
    @staticmethod
    def increment(key: str, amount: int = 1) -> Awaitable[int]: ...
    @staticmethod
    def decrement(key: str, amount: int = 1) -> Awaitable[int]: ...

    # Locking
    @staticmethod
    def lock(key: str, timeout: float | None = None) -> CacheLock: ...
