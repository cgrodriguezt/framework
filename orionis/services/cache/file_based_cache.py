from __future__ import annotations
import hashlib
import time
from pathlib import Path
from orionis.services.cache.serializer import Serializer

class FileBasedCache:

    # ruff: noqa: S324

    CACHE_VERSION = 1

    def __init__(
        self,
        path: Path,
        filename: str,
        monitored_dirs: list[Path] | None = None,
        monitored_files: list[Path] | None = None,
    ) -> None:
        """
        Initialize the FileBasedCache instance.

        Parameters
        ----------
        path : Path
            Directory path where the cache file will be stored.
        filename : str
            Name of the cache file.
        monitored_dirs : list[Path] or None, optional
            List of directories to monitor for changes.
        monitored_files : list[Path] or None, optional
            List of files to monitor for changes.

        Returns
        -------
        None
            This method does not return a value.
        """
        if not isinstance(path, Path):
            error_msg = "path must be Path"
            raise TypeError(error_msg)

        self.__path = path
        self.__file = path / filename

        # Directories and files to monitor for cache invalidation
        self.__monitored_dirs = monitored_dirs or []
        self.__monitored_files = monitored_files or []

        # Ensure the cache directory exists
        self.__path.mkdir(parents=True, exist_ok=True)

        # Internal cache for source hash and timing
        self.__sourcesHashCache: str | None = None
        self.__lastHashCheck: float = 0.0
        self.__hashInterval: float = 0.5

    def get(self) -> dict | None:
        """
        Retrieve cached data if valid.

        Returns
        -------
        dict or None
            The cached data if valid, otherwise None.
        """
        # Return None if cache file does not exist
        if not self.__file.exists():
            return None

        # Load payload from cache file
        payload = Serializer.loadFromFile(self.__file)
        if not payload:
            return None

        # Extract metadata and validate
        meta = payload.get("__meta__")
        if not meta:
            return None

        # Check cache version
        if meta.get("version") != self.CACHE_VERSION:
            return None

        # Check if sources hash matches
        if meta.get("sourcesHash") != self.__computeSourcesHash():
            return None

        # Return cached data
        return payload["__data__"]

    def save(self, data: dict) -> tuple[int, str]:
        """
        Save the provided data to the cache file if it has changed.

        Parameters
        ----------
        data : dict
            The data to be cached.

        Returns
        -------
        tuple[int, str]
            A tuple containing the cache version and the sources hash.
        """
        # Validate that the input data is a dictionary
        if not isinstance(data, dict):
            error_msg = "data must be dict"
            raise TypeError(error_msg)

        # Compute the hash of monitored sources for cache validation
        sourcesHash = self.__computeSourcesHash()

        newPayload = {
            "__meta__": {
                "version": self.CACHE_VERSION,
                "generatedAt": int(time.time()),
                "sourcesHash": sourcesHash,
            },
            "__data__": data,
        }

        # If the cache file exists, check if the content has actually changed
        if self.__file.exists():

            # Load the existing cache content for comparison
            existing = Serializer.loadFromFile(self.__file)

            # If the existing cache is valid, compare it with the new payload
            if existing:

                # Extract existing metadata for comparison
                existingMeta = existing.get("__meta__", {})

                # Compare version, sources hash, and data to determine
                # if we need to rewrite the cache file
                sameVersion = existingMeta.get("version") == self.CACHE_VERSION
                sameHash = existingMeta.get("sourcesHash") == sourcesHash
                sameData = existing.get("__data__") == data

                # Nothing changed, do not rewrite the cache file
                if sameVersion and sameHash and sameData:
                    return self.CACHE_VERSION, sourcesHash

        # Write to the cache file only if the content has changed
        Serializer.dumpToFile(newPayload, self.__file)

        return self.CACHE_VERSION, sourcesHash

    def clear(self) -> bool:
        """
        Remove the cache file if it exists.

        Returns
        -------
        bool
            True if the cache file was removed, False if it did not exist.
        """
        try:
            self.__file.unlink()
            return True
        except FileNotFoundError:
            return False

    def __computeSourcesHash(self) -> str:
        """
        Compute and return a hash representing the state of monitored sources.

        This method generates a SHA-1 hash based on the modification time and size
        of all monitored files and Python files in monitored directories, excluding
        the cache file itself. The hash is cached for a short interval to avoid
        redundant computation.

        Returns
        -------
        str
            The computed SHA-1 hash as a hexadecimal string.
        """
        now = time.time()

        # Use cached hash if within the allowed interval
        if (
            self.__sourcesHashCache
            and now - self.__lastHashCheck < self.__hashInterval
        ):
            return self.__sourcesHashCache

        hasher = hashlib.sha1()
        filesToHash: list[str] = []

        # Collect all Python files in monitored directories, excluding the cache file
        for directory in self.__monitored_dirs:
            if directory.exists():
                for file in directory.rglob("*.py"):
                    resolved = file.resolve()
                    if resolved == self.__file.resolve():
                        continue
                    filesToHash.append(resolved.as_posix())

        # Collect all monitored files, excluding the cache file
        for file in self.__monitored_files:
            if file.exists():
                resolved = file.resolve()
                if resolved == self.__file.resolve():
                    continue
                filesToHash.append(resolved.as_posix())

        # Ensure deterministic ordering and uniqueness
        filesToHash = sorted(set(filesToHash))

        # Update hash with file path, modification time, and size
        for filePath in filesToHash:
            p = Path(filePath)
            stat = p.stat()
            hasher.update(
                f"{filePath}:{stat.st_mtime_ns}:{stat.st_size}".encode()
            )

        self.__sourcesHashCache = hasher.hexdigest()
        self.__lastHashCheck = now

        return self.__sourcesHashCache