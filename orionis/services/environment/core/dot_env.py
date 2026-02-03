from __future__ import annotations
import os
import ast
import threading
from pathlib import Path
from dotenv import dotenv_values, load_dotenv, set_key, unset_key
from orionis.services.environment.enums import EnvironmentValueType
from orionis.services.environment.validators import ValidateKeyName, ValidateTypes
from orionis.support.patterns.singleton import Singleton
from orionis.services.environment.dynamic.caster import EnvironmentCaster

class DotEnv(metaclass=Singleton):

    # ruff: noqa: PLR0911, FBT001

    # Thread-safe singleton instance lock
    _lock = threading.RLock()

    def __init__(
        self,
        path: str | None = None,
    ) -> None:
        """
        Initialize the DotEnv service and prepare the `.env` file.

        Parameters
        ----------
        path : str or None, optional
            Path to the `.env` file. Defaults to `.env` in the current working
            directory.

        Raises
        ------
        OSError
            If the `.env` file cannot be created or accessed.
        RuntimeError
            If an unexpected error occurs during initialization.

        Returns
        -------
        None
            This method does not return a value.
        """
        try:
            # Ensure thread-safe initialization to avoid race conditions.
            with self._lock:

                # Set the default .env file path to the current working directory.
                self.__resolved_path = Path.cwd() / ".env"

                # If a custom path is provided, resolve and use it.
                if path:
                    self.__resolved_path = Path(path).expanduser().resolve()

                # Create the .env file if it does not exist.
                if not self.__resolved_path.exists():
                    self.__resolved_path.touch()

                # Load environment variables from the .env file into the process env.
                load_dotenv(self.__resolved_path, override=True)

        except OSError as e:

            # Raise a specific error if the .env file cannot be created or accessed.
            error_msg = (
                "Failed to create or access the .env "
                f"file at {self.__resolved_path}: {e}"
            )
            raise OSError(error_msg) from e

        except Exception as e:

            # Raise a general error for any other exceptions during initialization.
            error_msg = (
                f"An unexpected error occurred while initializing DotEnv: {e}"
            )
            raise RuntimeError(error_msg) from e

    def set(
        self,
        key: str,
        value: str | float | bool | list | dict | tuple | set,
        type_hint: str | EnvironmentValueType | None = None,
        *,
        only_os: bool = False,
    ) -> bool:
        """
        Set an environment variable in the `.env` file and process environment.

        Parameters
        ----------
        key : str
            Name of the environment variable to set.
        value : str | float | bool | list | dict | tuple | set
            Value to assign to the environment variable.
        type_hint : str | EnvironmentValueType | None, optional
            Type hint to guide serialization of the value.
        only_os : bool, optional
            If True, set only in the process environment, not in the `.env` file.

        Returns
        -------
        bool
            True if the environment variable was set successfully.

        Raises
        ------
        OrionisEnvironmentValueError
            If the provided key is not a valid environment variable name.

        Notes
        -----
        Ensures thread safety, validates the key, serializes the value, writes to
        the `.env` file, and updates the process environment.
        """
        # Ensure thread-safe operation during the set process.
        with self._lock:
            # Validate the environment variable key name.
            __key: str = ValidateKeyName(key)

            # If a type hint is provided, validate and serialize the value.
            if type_hint is not None:
                __type = ValidateTypes(value, type_hint)
                __value = self.__serializeValue(value, __type)
            else:
                __value = self.__serializeValue(value)

            # Set the environment variable in the .env file unless only_os is True.
            if not only_os:
                set_key(self.__resolved_path, __key, __value)

            # Update the environment variable in the current process environment.
            os.environ[__key] = __value

            # Indicate successful operation.
            return True

    def get(
        self,
        key: str,
        default: object | None = None,
    ) -> object:
        """
        Retrieve the value of an environment variable.

        Parameters
        ----------
        key : str
            Name of the environment variable to retrieve.
        default : Any or None, optional
            Value to return if the key is not found. Defaults to None.

        Returns
        -------
        Any
            Parsed value of the environment variable if found, otherwise `default`.

        Raises
        ------
        OrionisEnvironmentValueError
            If `key` is not a valid environment variable name.
        """
        # Ensure thread-safe operation while retrieving the environment variable.
        with self._lock:

            # Validate the environment variable key name.
            __key = ValidateKeyName(key)

            # Attempt to get the value from the .env file.
            value = dotenv_values(self.__resolved_path).get(__key)

            # If not found in the .env file, check the current environment variables.
            if value is None:
                value = os.environ.get(__key)

            # Parse and return the value if found, otherwise return the default.
            return self.__parseValue(value) if value is not None else default

    def unset(
        self,
        key: str,
        *,
        only_os: bool = False,
    ) -> bool:
        """
        Remove an environment variable from the `.env` file and process environment.

        Parameters
        ----------
        key : str
            Name of the environment variable to remove.
        only_os : bool, optional
            If True, remove only from the process environment, not from the `.env` file.

        Returns
        -------
        bool
            True if the environment variable was removed or did not exist.

        Raises
        ------
        OrionisEnvironmentValueError
            If the provided key is not a valid environment variable name.

        Notes
        -----
        This method is thread-safe. If the variable does not exist, returns True.
        """
        # Ensure thread-safe operation during the unset process.
        with self._lock:
            # Validate the environment variable key name.
            validated_key: str = ValidateKeyName(key)

            # Remove the key from the .env file unless only_os is True.
            if not only_os:
                unset_key(self.__resolved_path, validated_key)

            # Remove the key from the current process environment, if present.
            os.environ.pop(validated_key, None)

            # Indicate successful operation.
            return True

    def all(self) -> dict:
        """
        Return all environment variables from the resolved `.env` file.

        Returns
        -------
        dict
            Dictionary mapping environment variable names (str) to their parsed
            Python values. Only variables present in the `.env` file are included.
        """
        # Acquire lock for thread-safe access to the .env file.
        with self._lock:

            # Read all raw key-value pairs from the .env file.
            raw_values = dotenv_values(self.__resolved_path)

            # Parse each value and return as a dictionary.
            return {k: self.__parseValue(v) for k, v in raw_values.items()}

    def __serializeValue(
        self,
        value: object,
        type_hint: str | EnvironmentValueType | None = None,
    ) -> str:
        """
        Serialize a Python value for storage in a .env file.

        Parameters
        ----------
        value : object
            The value to serialize. Supported types include None, str, int, float,
            bool, list, dict, tuple, and set.
        type_hint : str | EnvironmentValueType | None, optional
            An explicit type hint to guide serialization.

        Returns
        -------
        str
            The serialized string representation of the input value, suitable for
            storage in a .env file. Returns "null" for None values.
        """
        # Handle None values explicitly
        if value is None:
            return "null"

        # Use EnvironmentCaster for serialization if a type hint is provided
        if type_hint:
            return EnvironmentCaster(value).to(type_hint)

        # Serialize strings by stripping whitespace
        if isinstance(value, str):
            return value.strip()

        # Serialize booleans as lowercase strings ("true" or "false")
        if isinstance(value, bool):
            return str(value).lower()

        # Serialize integers and floats as strings
        if isinstance(value, (int, float)):
            return str(value)

        # Serialize collections (list, dict, tuple, set) using repr
        if isinstance(value, (list, dict, tuple, set)):
            return repr(value)

        # Fallback: convert any other type to string
        return str(value)

    def __parseValue(
        self,
        value: object,
    ) -> object:
        """
        Parse a value from the .env file into its corresponding Python type.

        Parameters
        ----------
        value : object
            The value to parse, typically a string from the .env file or a Python
            object.

        Returns
        -------
        object
            The parsed Python value. Returns None for recognized null
            representations, a boolean for "true"/"false" strings, a Python
            literal (list, dict, int, etc.) if possible, or the original string
            if no conversion is possible.

        Notes
        -----
        Recognizes 'none', 'null', 'nan', 'nil' (case-insensitive) as null
        values. Attempts to use `EnvironmentCaster` for advanced type parsing.
        Falls back to `ast.literal_eval` for literal evaluation. Returns the
        original string if all parsing attempts fail.
        """
        # Return None if the value is None
        if value is None:
            return None

        # Return immediately if already a basic Python type
        if isinstance(value, (bool, int, float, dict, list, tuple, set)):
            return value

        # Convert the value to string for further processing
        value_str: str = str(value)

        # Handle empty strings and common null representations
        if not value_str or value_str.lower().strip() in {
            "none", "null", "nan", "nil",
        }:
            return None

        # Boolean detection for string values (case-insensitive)
        lower_val: str = value_str.lower().strip()
        if lower_val in ("true", "false"):
            return lower_val == "true"

        # Attempt to parse using EnvironmentCaster for advanced types
        env_type_prefixes = {str(e.value) for e in EnvironmentValueType}
        if any(value_str.startswith(prefix) for prefix in env_type_prefixes):
            return EnvironmentCaster(value_str).get()

        # Attempt to parse using ast.literal_eval for Python literals
        try:
            return ast.literal_eval(value_str)
        except (ValueError, SyntaxError):
            # Return the original string if parsing fails
            return value_str

    def reload(self) -> bool:
        """
        Reload environment variables from the `.env` file.

        Reload all environment variables from the `.env` file into the current
        process environment, overriding any existing values.

        Returns
        -------
        bool
            True if environment variables were successfully reloaded.

        Raises
        ------
        RuntimeError
            If an error occurs during the reload operation.
        """
        try:
            # Ensure thread-safe operation during reload
            with self._lock:
                # Reload environment variables, overriding existing ones
                load_dotenv(self.__resolved_path, override=True)
                return True
        except Exception as e:
            error_msg = (
                f"An error occurred while reloading environment variables: {e}"
            )
            raise RuntimeError(error_msg) from e
