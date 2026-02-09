from __future__ import annotations
import base64
import datetime
import hashlib
import json
import time
from pathlib import Path
from typing import ClassVar
from orionis.services.cache.contracts.file_based_cache import IFileBasedCache

class FileBasedCache(IFileBasedCache):

    # ruff: noqa: PLR0911, S324, PLW0108

    CACHE_VERSION = 1

    DECODERS: ClassVar[dict[str, callable]] = {
        "builtins.bytes": lambda v: base64.b64decode(v),
        "datetime.time": lambda v: datetime.time.fromisoformat(v),
        "pathlib.Path": lambda v: Path(v),
        "pathlib._local.WindowsPath": lambda v: Path(v),
        "pathlib._local.PosixPath": lambda v: Path(v),
        "pathlib.WindowsPath": lambda v: Path(v),
        "pathlib.PosixPath": lambda v: Path(v),
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
        Initialize a FileBasedCache instance.

        Parameters
        ----------
        path : Path
            Directory where the cache file will be stored.
        filename : str
            Name of the cache file (without extension).
        monitored_dirs : list[Path] | None, optional
            List of directories to monitor for changes. Defaults to None.
        monitored_files : list[Path] | None, optional
            List of individual files to monitor for changes.
            Defaults to None.

        Returns
        -------
        None
            This method initializes the instance and does not return a value.
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

        # Initialize data and casting dictionaries
        self.__data = {}
        self.__casting = {}

        # Initialize caching optimization variables
        self._sources_hash_cache: str | None = None
        self._last_hash_check: float = 0
        self._hash_check_interval: float = 1.0
        self._path_cache: dict[str, list[str]] = {}

    def __validatePath(
        self,
        path: Path,
        *,
        is_dir: bool = False,
    ) -> None:
        """
        Validate that the provided path is a Path instance and handle creation.

        Parameters
        ----------
        path : Path
            Path to validate.
        is_dir : bool, optional
            If True, validates as directory. If False, validates as file path.
            Defaults to False.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If the provided path is not a Path instance or has wrong type.
        """
        # Validate that path is a Path instance
        if not isinstance(path, Path):
            error_msg = f"Expected Path, got {type(path).__name__}."
            raise TypeError(error_msg)

        # Handle directory path validation and creation
        if is_dir:
            if not path.exists():
                # Create directory with appropriate permissions
                path.mkdir(mode=0o755, parents=True, exist_ok=True)
            elif not path.is_dir():
                error_msg = f"Expected directory Path, got file Path: {path}."
                raise TypeError(error_msg)
        # Handle file path validation and creation
        elif not path.exists():
            # Create parent directories if they don't exist
            path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
            # Create the file if it doesn't exist
            path.touch(mode=0o644, exist_ok=True)
        elif path.is_dir():
            error_msg = f"Expected file Path, got directory Path: {path}."
            raise TypeError(error_msg)

    def __validateFilename(
        self,
        filename: str,
    ) -> None:
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
        # Check if filename is a string type
        if not isinstance(filename, str):
            error_msg = (
                f"Expected str for filename, got {type(filename).__name__}."
            )
            raise TypeError(error_msg)

    def __validateListOfPaths(
        self, paths: list[Path], *, is_dir: bool = False,
    ) -> None:
        """
        Validate that the provided argument is a list of Path instances.

        Parameters
        ----------
        paths : list[Path]
            List of paths to validate.
        is_dir : bool, optional
            If True, validates as directory. If False, validates as file path.
            Defaults to False.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If the provided argument is not a list of Path instances.
        """
        # Validate that paths is a list
        if not isinstance(paths, list):
            error_msg = f"Expected list of Paths, got {type(paths).__name__}."
            raise TypeError(error_msg)

        # Early exit for empty list - no validation needed
        if not paths:
            return

        # Batch validation for better performance - check types first
        non_path_items = [
            i for i, path in enumerate(paths) if not isinstance(path, Path)
        ]
        if non_path_items:
            error_msg = f"Non-Path items found at indices: {non_path_items}"
            raise TypeError(error_msg)

        # Validate existence/creation for each path
        for path in paths:
            self.__validatePath(path, is_dir=is_dir)

    def __validateDict(
        self,
        data: dict,
    ) -> None:
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
        # Check if data is a dictionary type
        if not isinstance(data, dict):
            error_msg = f"Expected dict, got {type(data).__name__}."
            raise TypeError(error_msg)

    def get(
        self,
    ) -> dict | None:
        """
        Retrieve cached data if the cache is valid.

        Returns
        -------
        dict | None
            Cached data if valid and up-to-date, None if cache is invalid,
            missing, or outdated.
        """
        # Return None if cache file does not exist
        if not self.__file.exists():
            return None

        # Load cache file content
        try:
            # Check if file is empty before attempting to read
            if self.__file.stat().st_size == 0:
                return None

            # Read and parse the cache file
            with self.__file.open("r", encoding="utf-8") as f:
                payload: dict = json.load(f)

        except (json.JSONDecodeError, OSError):

            # Handle file corruption or read errors
            return None

        # Extract meta and data sections
        meta: dict | None = payload.get("__meta__")

        # Validate meta information exists
        if not meta:
            return None

        # Validate cache version compatibility
        if meta.get("version") != self.CACHE_VERSION:
            return None

        # Validate sources hash to ensure cache is up-to-date
        if meta.get("sources_hash") != self.__sourcesHash():
            return None

        # Return the rehydrated cached data
        return self.__rehydrate(
            payload["__data__"],
            payload["__casting__"],
        )

    def save(
        self,
        data: dict,
    ) -> tuple[int, str]:
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

        # Encode non-JSON serializable values
        self.__encodeNonJson()
        self.__applyCasting()

        # Prepare the payload with metadata and data
        payload: dict = {
            "__meta__": {
                "version": self.CACHE_VERSION,
                "generated_at": int(time.time()),
                "sources_hash": file_hash,
            },
            "__data__": self.__data,
            "__casting__": self.__casting,
        }

        # Write to a temporary file for atomicity
        tmp: Path = self.__file.with_suffix(".tmp")

        try:
            # Use optimized JSON settings for better performance
            with tmp.open("w", encoding="utf-8") as f:
                json.dump(
                    payload, f, ensure_ascii=False, separators=(",", ":"),
                )

            # Atomically replace the old cache file with the new one
            tmp.replace(self.__file)

        except Exception:

            # Clean up temporary file in case of error
            tmp.unlink(missing_ok=True)
            raise

        # Return the cache version and sources hash
        return self.CACHE_VERSION, file_hash

    def clear(
        self,
    ) -> bool:
        """
        Remove the cache file from disk.

        Returns
        -------
        bool
            True if the cache file was successfully removed, False if it did
            not exist.
        """
        # Attempt to remove the cache file; ignore if it does not exist
        try:
            self.__file.unlink()
            return True
        except FileNotFoundError:
            return False

    def __sourcesHash(
        self,
    ) -> str:
        """
        Compute a SHA-1 hash with caching optimization.

        Parameters
        ----------
        None

        Returns
        -------
        str
            SHA-1 hash of the monitored directories and files' state.
        """
        # Get the current time for interval checking
        current_time = time.time()

        # Check if cached hash is still valid within the interval
        if (self._sources_hash_cache is not None and
            current_time - self._last_hash_check < self._hash_check_interval):
            return self._sources_hash_cache

        # Initialize SHA-1 hash object
        h: hashlib._Hash = hashlib.sha1()

        # Process all monitored directories
        for directory in self.__monitored_dirs:
            self.__hashDir(h, directory)

        # Process all monitored files
        for file in self.__monitored_files:
            self.__hashFile(h, file)

        # Cache the computed hash and update check timestamp
        self._sources_hash_cache = h.hexdigest()
        self._last_hash_check = current_time

        # Return the cached sources hash
        return self._sources_hash_cache

    def __hashDir(
        self,
        h: hashlib._Hash,
        directory: Path,
    ) -> None:
        """
        Update the hash with all Python files in the given directory.

        Uses Path.rglob for optimized recursive file discovery and processes
        files in sorted order for deterministic hash generation.

        Parameters
        ----------
        h : hashlib._Hash
            Hash object to update with directory contents.
        directory : Path
            Directory to recursively scan for Python files.

        Returns
        -------
        None
            This method updates the hash object in place and does not return
            a value.
        """
        # Mark missing directories in the hash and exit early
        if not directory.exists():
            h.update(f"{directory}:missing".encode())
            return

        # Use rglob for efficient recursive file discovery with error handling
        try:
            # Sort files for deterministic hash generation
            py_files = sorted(directory.rglob("*.py"))

            # Hash each Python file found in the directory tree
            for py_file in py_files:
                self.__hashFile(h, py_file)

        except OSError:

            # Handle directory scanning errors by marking in hash
            h.update(f"{directory}:scan_error".encode())

    def __hashFile(
        self,
        h: hashlib._Hash,
        file: Path,
    ) -> None:
        """
        Update the hash with file metadata.

        Optimized to minimize system calls and handle symlinks properly.
        Includes file path, modification time, and size in the hash.
        Marks files with errors in the hash.

        Parameters
        ----------
        h : hashlib._Hash
            Hash object to update.
        file : Path
            File to hash.

        Returns
        -------
        None
            This method updates the hash object in place and does not return
            a value.
        """
        try:

            # Use lstat to avoid following symlinks and get better performance
            stat = file.lstat()

            # Create a single string to minimize calls to hash.update
            file_info = f"{file}:{stat.st_mtime_ns}:{stat.st_size}"
            h.update(file_info.encode())

        except OSError:

            # Mark files with errors in the hash
            h.update(f"{file}:error".encode())

    def __findNonJson( # NOSONAR
        self,
        obj: object,
        path: str = "",
    ) -> list[tuple[str, type, object]]:
        """
        Identify non-JSON-serializable values in a nested structure.

        Uses iterative approach with a stack to avoid deep recursion and
        improve performance when processing complex nested data structures.

        Parameters
        ----------
        obj : object
            Object to inspect for JSON serialization compatibility.
        path : str, optional
            Current path in the nested structure. Defaults to empty string.

        Returns
        -------
        list[tuple[str, type, object]]
            List of tuples containing the path, type, and value of each
            non-JSON-serializable item found.
        """
        # Initialize list to store non-serializable items
        issues: list[tuple[str, type, object]] = []

        # Use stack to avoid deep recursion for complex nested structures
        stack: list[tuple[object, str]] = [(obj, path)]

        # Iterate until all items are processed
        while stack:

            # Pop the last item from the stack
            current_obj, current_path = stack.pop()

            # Check for known non-JSON serializable types first
            if isinstance(current_obj, (bytes, datetime.time, Path)):
                issues.append((current_path, type(current_obj), current_obj))
                continue

            # Skip basic JSON-compatible types
            if isinstance(current_obj, (str, int, float, bool, type(None))):
                continue

            # Process container types recursively
            if isinstance(current_obj, dict):
                for k, v in current_obj.items():
                    new_path = f"{current_path}.{k}" if current_path else str(k)
                    stack.append((v, new_path))
            elif isinstance(current_obj, (list, tuple, set)):
                for i, v in enumerate(current_obj):
                    new_path = (
                        f"{current_path}[{i}]" if current_path else f"[{i}]"
                    )
                    stack.append((v, new_path))
            else:
                # Unknown type, potentially not JSON serializable
                issues.append((current_path, type(current_obj), current_obj))

        # Return the list of non-serializable items found
        return issues

    def __encodeNonJson(
        self,
    ) -> None:
        """
        Encode non-JSON-serializable values in the configuration.

        Identify values in the configuration that cannot be serialized to JSON,
        convert them to serializable representations, and store their metadata
        in the internal casting dictionary for later reconstruction.

        Returns
        -------
        None
            Updates self.__casting in place and does not return a value.
        """
        # Find non-JSON-serializable values in the configuration
        njson: list[tuple[str, type, object]] = self.__findNonJson(self.__data)

        # Process each non-serializable value found
        for path, typ, val in njson:

            # Convert non-JSON-serializable values to serializable forms
            if isinstance(val, datetime.time):
                value = self.ENCODERS[datetime.time](val)
            elif isinstance(val, bytes):
                value = self.ENCODERS[bytes](val)
            elif isinstance(val, Path):
                value = self.ENCODERS[Path](val)
            else:
                # Handle unsupported types with descriptive error
                error_msg = (
                    f"Unsupported non-JSON-serializable type: {typ} in "
                    f"({path}) = {val}"
                )
                raise TypeError(error_msg)

            # Store casting information for rehydration
            self.__casting[path] = {
                "type": f"{typ.__module__}.{typ.__name__}",
                "value": value,
            }

    def __rehydrate(
        self,
        data: dict,
        casting: dict,
    ) -> dict:
        """
        Rehydrate configuration with decoded non-JSON-serializable values.

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

        Raises
        ------
        ValueError
            If an unknown cast type is encountered in the casting dictionary.
        """
        # Process each casting specification to decode serialized values
        for path, spec in casting.items():

            # Get the appropriate decoder for the type
            decoder = self.DECODERS.get(spec["type"])

            # Validate decoder exists for the specified type
            if not decoder:
                error_msg = f"Unknown cast type: {spec['type']}"
                raise ValueError(error_msg)

            # Set the decoded value at the specified path in the config
            self.__setByPath(data, path, decoder(spec["value"]))

        # Return the rehydrated configuration dictionary
        return data

    def __applyCasting(
        self,
    ) -> None:
        """
        Replace non-JSON-serializable values with their serializable forms.

        Iterates through the casting dictionary and replaces the corresponding
        paths in the data with their encoded serializable representations.

        Returns
        -------
        None
            Updates self.__data in place with serializable values.
        """
        # Apply each casting specification to replace values in data
        for path, info in self.__casting.items():
            self.__setByPath(self.__data, path, info["value"])

    def __setByPath(
        self,
        dictionary: dict,
        dot_path: str,
        target_value: object,
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
            Updates the dictionary in place and returns None.
        """
        # Cache path splitting to avoid multiple split operations on similar paths
        if dot_path not in self._path_cache:
            self._path_cache[dot_path] = dot_path.split(".")

        # Retrieve cached keys for the path
        keys = self._path_cache[dot_path]

        # Navigate through nested structure optimally
        current = dictionary
        for key in keys[:-1]:

            # Handle array indices if necessary
            if key.startswith("[") and key.endswith("]"):
                index = int(key[1:-1])
                current = current[index]
            else:
                current = current[key]

        # Set value at final destination
        final_key = keys[-1]
        if final_key.startswith("[") and final_key.endswith("]"):
            index = int(final_key[1:-1])
            current[index] = target_value
        else:
            current[final_key] = target_value
