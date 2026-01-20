from __future__ import annotations
import base64
import datetime
import hashlib
import json
import os
import time
from pathlib import Path
from typing import ClassVar
from orionis.services.cache.contracts.file_based_cache import IFileBasedCache

class FileBasedCache(IFileBasedCache):

    CACHE_VERSION = 1

    DECODERS: ClassVar[dict[str, callable]] = {
        "builtins.bytes": lambda v: base64.b64decode(v),
        "datetime.time": lambda v: datetime.time.fromisoformat(v),
        "pathlib.Path": lambda v: Path(v),
        "pathlib._local.WindowsPath": lambda v: Path(v),
        "pathlib._local.PosixPath": lambda v: Path(v),
    }

    ENCODERS: ClassVar[dict[type, callable]] = {
        bytes: lambda v: base64.b64encode(v).decode(),
        datetime.time: lambda v: v.strftime("%H:%M:%S"),
        Path: lambda v: str(v),
    }

    def __init__(
        self,
        path: Path,
        filename: str,
        monitored_dirs: list[Path] | None = None,
        monitored_files: list[Path] | None = None,
    ) -> None:
        """
        Initialize a JsonCache instance.

        Parameters
        ----------
        path : Path
            Directory where the cache file will be stored.
        filename : str
            Name of the cache file (without extension).
        monitored_dirs : list[Path] | None, optional
            List of directories to monitor for changes. Defaults to None.
        monitored_files : list[Path] | None, optional
            List of individual files to monitor for changes. Defaults to None.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Validate cache path argument
        self.__validatePath(path, is_dir=True)

        # Validate filename argument
        self.__validateFilename(filename)

        # Validate monitored_dirs argument
        self.__validateListOfPaths(monitored_dirs or [], is_dir=True)

        # Validate monitored_files argument
        self.__validateListOfPaths(monitored_files or [], is_dir=False)

        # Store parameters
        self.__path = path
        self.__file = path / f"{filename}"
        self.__monitored_dirs = monitored_dirs or []
        self.__monitored_files = monitored_files or []

        # Ensure the cache directory exists
        self.__path.mkdir(parents=True, exist_ok=True)

        # Initialize casting dictionary
        self.__data = {}
        self.__casting = {}

    def __validatePath(self, path: Path, *, is_dir:bool=False) -> None:
        """
        Validate that the provided path is a Path instance.

        Parameters
        ----------
        path : Path
            Path to validate.
        is_dir : bool, optional
            If True, validates as directory. If False, validates as file path.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If the provided path is not a Path instance.
        """
        # Validate that path is a Path instance
        if not isinstance(path, Path):
            error_msg = f"Expected Path, got {type(path).__name__}."
            raise TypeError(error_msg)

        # If is_dir is True, create directory if it doesn't exist
        if is_dir:
            if not path.exists():
                path.mkdir(mode=0o755, parents=True, exist_ok=True)
            elif not path.is_dir():
                error_msg = f"Expected directory Path, got file Path: {path}."
                raise TypeError(error_msg)
        else:
            # For file paths, create parent directories if they don't exist
            if not path.exists():
                path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
                # Create the file if it doesn't exist
                path.touch(mode=0o644, exist_ok=True)
            elif path.is_dir():
                error_msg = f"Expected file Path, got directory Path: {path}."
                raise TypeError(error_msg)

    def __validateFilename(self, filename: str) -> None:
        """
        Validate that the provided filename is a string.

        Parameters
        ----------
        filename : str
            Filename to validate.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If the provided filename is not a string.
        """
        if not isinstance(filename, str):
            error_msg = f"Expected str for filename, got {type(filename).__name__}."
            raise TypeError(error_msg)

    def __validateListOfPaths(self, paths: list[Path], *, is_dir:bool = False) -> None:
        """
        Validate that the provided argument is a list of Path instances.

        Parameters
        ----------
        paths : list[Path]
            List of paths to validate.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If the provided argument is not a list of Path instances.
        """
        if not isinstance(paths, list):
            error_msg = f"Expected list of Paths, got {type(paths).__name__}."
            raise TypeError(error_msg)
        for path in paths:
            self.__validatePath(path, is_dir=is_dir)

    def __validateDict(self, data: dict) -> None:
        """
        Validate that the provided data is a dictionary.

        Parameters
        ----------
        data : dict
            Data to validate.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If the provided data is not a dictionary.
        """
        if not isinstance(data, dict):
            error_msg = f"Expected dict, got {type(data).__name__}."
            raise TypeError(error_msg)

    def get(self) -> dict | None:
        """
        Retrieve cached data if the cache is valid.

        Returns
        -------
        dict or None
            Cached data if valid, otherwise None.
        """
        # Return None if cache file does not exist
        if not self.__file.exists():
            return None

        # Load cache file content
        try:
            with self.__file.open("r", encoding="utf-8") as f:
                payload: dict = json.load(f)
        except Exception:
            return None

        # Extract meta and data sections
        meta: dict | None = payload.get("__meta__")

        # Validate meta information and cache version
        if not meta:
            return None

        # Validate cache version
        if meta.get("version") != self.CACHE_VERSION:
            return None

        # Validate sources hash to ensure cache is up-to-date
        if meta.get("sources_hash") != self.__sourcesHash():
            return None

        # Return the cached data
        return self.__rehydrate(
            payload["__data__"],
            payload["__casting__"],
        )


    def save(self, data: dict) -> tuple[int, str]:
        """
        Save the provided data to disk atomically.

        Parameters
        ----------
        data : dict
            Data to be cached.

        Returns
        -------
        tuple[int, str]
            Tuple containing the cache version and the sources hash.

        Raises
        ------
        TypeError
            If the provided data is not a dictionary.
        """
        # Validate input data type
        self.__validateDict(data)
        self.__data = data
        # Compute the hash of monitored sources
        file_hash: str = self.__sourcesHash()
        self.__encodeNonJson()
        self.__applyCasting()


        # Prepare the payload with metadata and data
        payload: dict = {
            '__meta__': {
                "version": self.CACHE_VERSION,
                "generated_at": int(time.time()),
                "sources_hash": file_hash,
            },
            "__data__": self.__data,
            "__casting__": self.__casting,
        }

        # Write to a temporary file for atomicity
        tmp: Path = self.__file.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)

        # Atomically replace the old cache file with the new one
        tmp.replace(self.__file)

        # Return the cache version and sources hash
        return self.CACHE_VERSION, file_hash

    def clear(self) -> bool:
        """
        Remove the cache file from disk.

        Returns
        -------
        bool
            True if the cache file was removed, False if it did not exist.
        """
        # Attempt to remove the cache file; ignore if it does not exist
        try:
            self.__file.unlink()
            return True
        except FileNotFoundError:
            return False

    def __sourcesHash(self) -> str:
        """
        Compute a SHA-1 hash representing the state of monitored sources.

        Returns
        -------
        str
            SHA-1 hash of the monitored directories and files' state.
        """
        h: hashlib._Hash = hashlib.sha1()

        # Hash all monitored directories
        for directory in self.__monitored_dirs:
            self.__hashDir(h, directory)

        # Hash all monitored files
        for file in self.__monitored_files:
            self.__hashFile(h, file)

        return h.hexdigest()

    def __hashDir(self, h: hashlib._Hash, directory: Path) -> None:
        """
        Update the hash with all Python files in the given directory.

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
        # If the directory does not exist, mark it in the hash and return
        if not directory.exists():
            h.update(f"{directory}:missing".encode())
            return

        # Walk through the directory and hash all .py files
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

        Notes
        -----
        Includes file path, modification time, and size in the hash.
        Marks files with errors in the hash.
        """
        try:
            stat = file.stat()
            # Update hash with file path, modification time, and size
            h.update(str(file).encode())
            h.update(str(stat.st_mtime_ns).encode())
            h.update(str(stat.st_size).encode())
        except OSError:
            # Mark files with errors in the hash
            h.update(f"{file}:error".encode())

    def __findNonJson(
        self, obj: object, path: str = "",
    ) -> list[tuple[str, type, object]]:
        """
        Identify non-JSON-serializable values in a nested structure.

        Recursively traverse the given object and collect paths to values that
        cannot be serialized to JSON.

        Parameters
        ----------
        obj : object
            Object to inspect for JSON serialization compatibility.
        path : str, optional
            Current path in the nested structure (default is an empty string).

        Returns
        -------
        list[tuple[str, type, object]]
            List of tuples containing the path, type, and value of each
            non-JSON-serializable item found.
        """
        try:
            # Attempt to serialize the object to JSON
            json.dumps(obj)
            return []
        except TypeError:
            # Collect specific non-JSON serialization issues
            return self.__collectNonJsonIssues(obj, path)

    def __collectNonJsonIssues(
        self, obj: object, path: str,
    ) -> list[tuple[str, type, object]]:
        """
        Collect non-JSON-serializable issues from an object.

        Analyze the object type and delegate to appropriate handler methods
        for detailed inspection.

        Parameters
        ----------
        obj : object
            Object to inspect for serialization issues.
        path : str
            Current path in the nested structure.

        Returns
        -------
        list[tuple[str, type, object]]
            List of non-JSON-serializable items found.
        """
        if isinstance(obj, dict):
            # Handle dictionary objects recursively
            return self.__handleDictionary(obj, path)
        if isinstance(obj, (list, tuple, set)):
            # Handle sequence objects recursively
            return self.__handleSequence(obj, path)
        # Return the problematic object itself
        return [(path, type(obj), obj)]

    def __handleDictionary(
        self, obj: dict, path: str,
    ) -> list[tuple[str, type, object]]:
        """
        Handle dictionary objects for non-JSON serialization detection.

        Traverse dictionary items recursively to identify non-serializable
        values within nested structures.

        Parameters
        ----------
        obj : dict
            Dictionary object to inspect for serialization issues.
        path : str
            Current path in the nested structure.

        Returns
        -------
        list[tuple[str, type, object]]
            List of non-JSON-serializable items found in the dictionary.
        """
        issues: list[tuple[str, type, object]] = []
        # Process each key-value pair in the dictionary
        for k, v in obj.items():
            new_path = f"{path}.{k}" if path else str(k)
            issues.extend(self.__findNonJson(v, new_path))
        return issues

    def __handleSequence(
        self, obj: object, path: str,
    ) -> list[tuple[str, type, object]]:
        """
        Handle sequence objects for non-JSON serialization detection.

        Traverse sequence items recursively to identify non-serializable
        values within nested structures.

        Parameters
        ----------
        obj : object
            Sequence object (list, tuple, or set) to inspect.
        path : str
            Current path in the nested structure.

        Returns
        -------
        list[tuple[str, type, object]]
            List of non-JSON-serializable items found in the sequence.
        """
        issues: list[tuple[str, type, object]] = []
        # Process each item in the sequence with index tracking
        for i, v in enumerate(obj):
            new_path = f"{path}[{i}]" if path else f"[{i}]"
            issues.extend(self.__findNonJson(v, new_path))
        return issues

    def __encodeNonJson(self) -> None:
        """
        Encode non-JSON-serializable values in the configuration.

        Identifies values in the configuration that cannot be serialized to JSON,
        converts them to serializable representations, and stores their metadata
        in the internal serializables dictionary.

        Returns
        -------
        None
            This method updates self.__casting in place and does not return
            a value.
        """
        # Find non-JSON-serializable values in the configuration
        njson: list[tuple[str, type, object]] = self.__findNonJson(self.__data)

        for path, typ, val in njson:
            # Convert non-JSON-serializable values to serializable representations
            if isinstance(val, datetime.time):
                value = self.ENCODERS[datetime.time](val)
            elif isinstance(val, bytes):
                value = self.ENCODERS[bytes](val)
            elif isinstance(val, Path):
                value = self.ENCODERS[Path](val)
            else:
                error_msg = (
                    f"Unsupported non-JSON-serializable type: {typ} in "
                    f"({path}) = {val}"
                )
                raise TypeError(error_msg)
            self.__casting[path] = {
                "type": f"{typ.__module__}.{typ.__name__}",
                "value": value,
            }

    def __rehydrate(
        self, data: dict, casting: dict,
    ) -> dict:
        """
        Rehydrate the configuration with decoded non-JSON-serializable values.

        Parameters
        ----------
        data : dict
            The configuration dictionary to update.
        casting : dict
            Dictionary containing casting information for decoding values.

        Returns
        -------
        dict
            The updated configuration dictionary with decoded values.
        """
        for path, spec in casting.items():
            decoder = self.DECODERS.get(spec["type"])
            if not decoder:
                error_msg = f"Unknown cast type: {spec['type']}"
                raise ValueError(error_msg)
            # Set the decoded value at the specified path in the config
            self.__setByPath(data, path, decoder(spec["value"]))
        return data

    def __applyCasting(self) -> None:
        """
        Replace non-JSON-serializable values in the configuration.

        Iterates through the internal serializables dictionary and replaces
        the corresponding paths in the configuration with their serializable
        representations.

        Returns
        -------
        None
            This method updates self.__config in place and does not return
            a value.
        """
        for path, info in self.__casting.items():
            self.__setByPath(self.__data, path, info["value"])

    def __setByPath(
        self, dictionary: dict, dot_path: str, target_value: object,
    ) -> None:
        """
        Set a value in a nested dictionary using a dot-separated path.

        Parameters
        ----------
        dictionary : dict
            The dictionary to update.
        dot_path : str
            The dot-separated path indicating where to set the value.
        target_value : object
            The value to set at the specified path.

        Returns
        -------
        None
            This method updates the dictionary in place and returns None.
        """
        # Traverse the dictionary using the path and set the value at the target key
        keys = dot_path.split(".")
        current = dictionary
        for key in keys[:-1]:
            current = current[key]
        current[keys[-1]] = target_value

