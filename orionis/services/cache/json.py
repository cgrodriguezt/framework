from __future__ import annotations
import json
import os
import hashlib
import time
from pathlib import Path
from typing import Any

class JsonCache:
    """
    Provide a lightweight JSON cache with source invalidation.

    Features
    --------
    - Directory monitoring (.py files)
    - Individual file monitoring
    - Fast invalidation (mtime_ns + size)
    - Atomic writes
    - Schema versioning

    Notes
    -----
    Not intended for secrets.
    """

    CACHE_VERSION = 1

    def __init__(
        self,
        path: Path,
        filename: str,
        monitored_dirs: list[Path] | None = None,
        monitored_files: list[Path] | None = None,
    ) -> None:
        """
        Initialize the JsonCache instance.

        Parameters
        ----------
        path : Path
            Directory where the cache file will be stored.
        filename : str
            Name of the cache file (without extension).
        monitored_dirs : list[Path] | None
            List of directories to monitor for changes.
        monitored_files : list[Path] | None
            List of individual files to monitor for changes.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.__path = path
        self.__file = path / f"{filename}.json"
        self.__monitored_dirs = monitored_dirs or []
        self.__monitored_files = monitored_files or []
        # Ensure the cache directory exists
        self.__path.mkdir(parents=True, exist_ok=True)

    def get(self) -> Any | None:
        """
        Retrieve cached data if the cache is valid.

        Returns
        -------
        Any | None
            Cached data if valid, otherwise None.
        """
        if not self.__file.exists():
            return None

        try:
            with self.__file.open("r", encoding="utf-8") as f:
                payload: dict = json.load(f)
        except Exception:
            return None

        meta = payload.get("meta")
        data = payload.get("data")

        if not meta:
            return None

        if meta.get("version") != self.CACHE_VERSION:
            return None

        if meta.get("sources_hash") != self.__sourcesHash():
            return None

        return data

    def save(self, data: Any) -> None:
        """
        Persist data to disk atomically.

        Parameters
        ----------
        data : Any
            Data to be cached.

        Returns
        -------
        None
            This method does not return a value.
        """
        payload = {
            "meta": {
                "version": self.CACHE_VERSION,
                "generated_at": int(time.time()),
                "sources_hash": self.__sourcesHash(),
            },
            "data": data,
        }

        tmp = self.__file.with_suffix(".tmp")
        # Write to a temporary file for atomicity
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)

        os.replace(tmp, self.__file)

    def clear(self) -> None:
        """
        Remove the cache file from disk.

        Returns
        -------
        None
            This method does not return a value.
        """
        try:
            self.__file.unlink()
        except FileNotFoundError:
            pass

    def __sourcesHash(self) -> str:
        """
        Compute a hash representing the monitored source state.

        Returns
        -------
        str
            SHA-1 hash of monitored sources' state.
        """
        h = hashlib.sha1()

        # Hash monitored directories
        for directory in self.__monitored_dirs:
            self.__hashDir(h, directory)

        # Hash monitored individual files
        for file in self.__monitored_files:
            self.__hashFile(h, file)

        return h.hexdigest()

    def __hashDir(self, h: hashlib._Hash, directory: Path) -> None:
        """
        Update the hash with all .py files in a directory.

        Parameters
        ----------
        h : hashlib._Hash
            Hash object to update.
        directory : Path
            Directory to hash.

        Returns
        -------
        None
            This method does not return a value.
        """
        if not directory.exists():
            # Mark missing directories in the hash
            h.update(f"{directory}:missing".encode())
            return

        for root, _, files in os.walk(directory):
            for name in files:
                if not name.endswith(".py"):
                    continue
                self.__hashFile(h, Path(root) / name)

    def __hashFile(self, h: hashlib._Hash, file: Path) -> None:
        """
        Update the hash with file metadata.

        Parameters
        ----------
        h : hashlib._Hash
            Hash object to update.
        file : Path
            File to hash.

        Returns
        -------
        None
            This method does not return a value.
        """
        try:
            stat = file.stat()
            # Include file path, modification time, and size in the hash
            h.update(str(file).encode())
            h.update(str(stat.st_mtime_ns).encode())
            h.update(str(stat.st_size).encode())
        except OSError:
            # Mark files with errors in the hash
            h.update(f"{file}:error".encode())
