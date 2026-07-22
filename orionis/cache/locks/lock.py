from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, Any, Self
from aiocache.lock import RedLock
from orionis.cache.stores.file import FileCacheBackend

if TYPE_CHECKING:
    import types

# Per-key asyncio locks for the file-based backend (process-scoped).
_FILE_LOCKS: dict[str, asyncio.Lock] = {}

class CacheLock:

    # ruff: noqa: ANN401

    __slots__ = ("_backend", "_impl", "_key", "_timeout")

    def __init__(
        self,
        backend: Any,
        key: str,
        timeout: float | None = None,
    ) -> None:
        """
        Initialize the lock for *key* on *backend*.

        Parameters
        ----------
        backend : Any
            Raw cache backend.
        key : str
            Cache key to lock on.
        timeout : float | None
            Lock timeout in seconds.  ``None`` means no timeout.
        """
        self._backend = backend
        self._key = key
        self._timeout = timeout
        self._impl: asyncio.Lock | RedLock | None = None

    async def __aenter__(self) -> Self:
        """
        Acquire the lock before entering the protected block.

        Returns
        -------
        Self
            This ``CacheLock`` instance.
        """
        if isinstance(self._backend, FileCacheBackend):
            lock = _FILE_LOCKS.setdefault(self._key, asyncio.Lock())
            if self._timeout is not None:
                await asyncio.wait_for(lock.acquire(), timeout=self._timeout)
            else:
                await lock.acquire()
            self._impl = lock
        else:
            self._impl = RedLock(
                self._backend,
                self._key,
                lease=self._timeout or 10,
            )
            await self._impl.__aenter__()

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """
        Release the lock after leaving the protected block.

        Parameters
        ----------
        exc_type : type[BaseException] | None
            Exception type, if any.
        exc_val : BaseException | None
            Exception instance, if any.
        exc_tb : types.TracebackType | None
            Traceback object, if any.
        """
        if isinstance(self._backend, FileCacheBackend):
            if isinstance(self._impl, asyncio.Lock):
                self._impl.release()
        elif isinstance(self._impl, RedLock):
            await self._impl.__aexit__(exc_type, exc_val, exc_tb)
