from __future__ import annotations
import asyncio
import hashlib
import time
from typing import TYPE_CHECKING, Any
import msgspec
import msgspec.json as _msgjson

if TYPE_CHECKING:
    from pathlib import Path

# Sentinel object to distinguish "key not found" from a stored None value.
_MISSING = object()

class FileCacheBackend:

    # ruff: noqa: ANN401

    __slots__ = ("_path",)

    def __init__(self, path: Path) -> None:
        """
        Initialize the backend and create the cache directory if needed.

        Parameters
        ----------
        path : Path
            Directory where cache files will be stored.
        """
        self._path: Path = path
        path.mkdir(parents=True, exist_ok=True)

    # ── Internal helpers ────────────────────────────────────────────────────

    def __file(self, key: str) -> Path:
        """
        Return the filesystem path for *key*.

        Parameters
        ----------
        key : str
            Cache key.

        Returns
        -------
        Path
            Path to the corresponding ``.json`` file.
        """
        digest = hashlib.sha256(key.encode()).hexdigest()
        return self._path / f"{digest}.json"


    def __readSync(self, file: Path) -> dict | None:
        """
        Read and decode a cache file synchronously.

        Parameters
        ----------
        file : Path
            Path to the cache file.

        Returns
        -------
        dict | None
            Decoded entry, or ``None`` on any error.
        """
        try:
            return _msgjson.decode(file.read_bytes())
        except (OSError, msgspec.DecodeError):
            return None

    def __writeSync(self, file: Path, entry: dict) -> None:
        """
        Atomically write *entry* to *file* via tmp-then-rename.

        Parameters
        ----------
        file : Path
            Target cache file.
        entry : dict
            Serializable cache entry.
        """
        data = _msgjson.encode(entry)
        tmp = file.with_suffix(".tmp")
        tmp.write_bytes(data)
        tmp.replace(file)

    def __unlinkSync(self, file: Path) -> None:
        """
        Remove *file*, ignoring missing-file errors.

        Parameters
        ----------
        file : Path
            File to remove.
        """
        file.unlink(missing_ok=True)

    # ── Public async API (mirrors aiocache BaseCache interface) ─────────────

    async def get(self, key: str, default: Any = None) -> Any:
        """
        Return the cached value for *key*, or *default* when absent/expired.

        Expired entries are deleted on first read (lazy eviction).

        Parameters
        ----------
        key : str
            Cache key.
        default : Any
            Value returned when the key is not found or has expired.

        Returns
        -------
        Any
            Stored value or *default*.
        """
        file = self.__file(key)
        entry = await asyncio.to_thread(self.__readSync, file)
        if entry is None:
            return default

        exp: float | None = entry.get("e")
        if exp is not None and time.monotonic() > exp:
            await asyncio.to_thread(self.__unlinkSync, file)
            return default

        return entry.get("v")

    async def set(self, key: str, value: Any, ttl: float | None = None) -> bool:
        """
        Store *value* under *key* with an optional TTL in seconds.

        Parameters
        ----------
        key : str
            Cache key.
        value : Any
            JSON-serializable value to cache.
        ttl : float | None
            Time-to-live in seconds. None means no expiry.

        Returns
        -------
        bool
            Always True.
        """
        entry: dict[str, Any] = {
            "v": value,
            "e": time.monotonic() + ttl if ttl is not None else None,
        }
        file = self.__file(key)
        await asyncio.to_thread(self.__writeSync, file, entry)
        return True

    async def exists(self, key: str) -> bool:
        """
        Return True if *key* exists and has not expired.

        Parameters
        ----------
        key : str
            Cache key.

        Returns
        -------
        bool
        """
        return await self.get(key, default=_MISSING) is not _MISSING

    async def delete(self, key: str) -> int:
        """
        Remove *key* from the store.

        Parameters
        ----------
        key : str
            Cache key.

        Returns
        -------
        int
            1 if the key existed, 0 otherwise.
        """
        file = self.__file(key)
        try:
            await asyncio.to_thread(file.unlink)
            return 1
        except FileNotFoundError:
            return 0

    async def clear(self) -> bool:
        """
        Remove all cache entries from the store directory.

        Returns
        -------
        bool
            Always True.
        """
        def _clear_all() -> None:
            for f in self._path.glob("*.json"):
                f.unlink(missing_ok=True)
            for f in self._path.glob("*.tmp"):
                f.unlink(missing_ok=True)

        await asyncio.to_thread(_clear_all)
        return True

    async def multiGet(self, keys: list[str], default: Any = None) -> list[Any]:
        """
        Return a list of values for *keys* in the same order.

        Parameters
        ----------
        keys : list[str]
            Cache keys.
        default : Any
            Returned for each missing/expired key.

        Returns
        -------
        list[Any]
        """
        return [await self.get(k, default) for k in keys]

    async def multiSet(
        self,
        pairs: list[tuple[str, Any]],
        ttl: float | None = None,
    ) -> bool:
        """
        Store multiple key/value pairs with an optional TTL.

        Parameters
        ----------
        pairs : list[tuple[str, Any]]
            Sequence of (key, value) pairs.
        ttl : float | None
            Shared TTL applied to every pair.

        Returns
        -------
        bool
            Always True.
        """
        for key, value in pairs:
            await self.set(key, value, ttl=ttl)
        return True

    # aiocache-compatible aliases so CacheRepository.getMany/setMany work
    # with this backend without modification.

    async def multi_get(
        self,
        keys: list[str],
        default: Any = None,
    ) -> list[Any]:
        """
        Return a list of values for *keys* (aiocache-compatible alias).

        Parameters
        ----------
        keys : list[str]
            Cache keys.
        default : Any
            Returned for each missing/expired key.

        Returns
        -------
        list[Any]
        """
        return await self.multiGet(keys, default)

    async def multi_set(
        self,
        pairs: list[tuple[str, Any]],
        ttl: float | None = None,
    ) -> bool:
        """
        Store multiple key/value pairs (aiocache-compatible alias).

        Parameters
        ----------
        pairs : list[tuple[str, Any]]
            Sequence of (key, value) pairs.
        ttl : float | None
            Shared TTL applied to every pair.

        Returns
        -------
        bool
            Always True.
        """
        return await self.multiSet(pairs, ttl=ttl)

    async def add(self, key: str, value: Any, ttl: float | None = None) -> bool:
        """
        Store *value* under *key* only if the key does not already exist.

        Parameters
        ----------
        key : str
            Cache key.
        value : Any
            Value to store.
        ttl : float | None
            Optional TTL in seconds.

        Returns
        -------
        bool
            True on success.

        Raises
        ------
        ValueError
            If the key already exists and has not expired.
        """
        if await self.exists(key):
            msg = f"Key {key!r} already exists in the cache."
            raise ValueError(msg)
        return await self.set(key, value, ttl=ttl)

    async def increment(self, key: str, delta: int = 1) -> int:
        """
        Increment the integer stored at *key* by *delta*.

        Creates the key with value *delta* if it does not exist.

        Parameters
        ----------
        key : str
            Cache key.
        delta : int
            Amount to add (use negative values to decrement).

        Returns
        -------
        int
            New value after increment.
        """
        current = await self.get(key, default=0)
        new_value = int(current) + delta
        await self.set(key, new_value)
        return new_value
