import ast
import os
from pathlib import Path
from typing import Any, Optional, Union
from dotenv import dotenv_values, load_dotenv, set_key, unset_key
from orionis.luminate.patterns.singleton.meta_class import Singleton

class DotEnv(metaclass=Singleton):
    """
    DotEnv is a singleton class for managing environment variables using a `.env` file.
    This class provides methods to load, get, set, unset, and list environment variables,
    with automatic serialization and deserialization of common Python data types.
    It ensures that changes to the `.env` file are reflected in the current process's
    environment variables and vice versa.
    """

    def __init__(self, path: str = None) -> None:
        """
        Initializes the environment service by resolving the path to the `.env` file, ensuring its existence,
        and loading environment variables from it.
        Args:
            path (str, optional): The path to the `.env` file. If not provided, defaults to a `.env` file
                in the current working directory.
        Raises:
            OSError: If the `.env` file cannot be created when it does not exist.
        """

        # Path to the `.env` file - If no path is provided, use the default path
        if path:
            self._resolved_path = Path(path).expanduser().resolve()
        else:
            self._resolved_path = Path(os.getcwd()) / ".env"

        # Ensure that the `.env` file exists
        if not self._resolved_path.exists():
            self._resolved_path.touch()

        # Load environment variables from the `.env` file
        load_dotenv(self._resolved_path)

    def destroy(self) -> bool:
        """
        Deletes the `.env` file at the resolved path.
        Returns:
            bool: True if the `.env` file was successfully deleted, False if the file did not exist.
        """

        # Deletes the `.env` file and returns True if it was successfully deleted.
        if self._resolved_path.exists():
            os.remove(self._resolved_path)
            return True
        return False

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieve the value of an environment variable.
        This method attempts to fetch the value of the specified environment variable `key`
        from a `.env` file. If the variable is not found in the `.env` file, it falls back
        to the system environment variables. If the variable is still not found, the provided
        `default` value is returned.
        Args:
            key (str): The name of the environment variable to retrieve.
            default (Optional[Any], optional): The value to return if the environment variable is not found. Defaults to None.
        Returns:
            Any: The value of the environment variable, parsed if found; otherwise, the `default` value.
        """

        # Gets the value of an environment variable from the `.env` file or from system environment variables.
        value = dotenv_values(self._resolved_path).get(key)
        if value is None:
            value = os.getenv(key)

        # If the value is not found, return the default value
        return self.__parseValue(value) if value is not None else default

    def set(self, key: str, value: Union[str, int, float, bool, list, dict]) -> bool:
        """
        Sets the value of an environment variable in both the `.env` file and the current system environment.
        Args:
            key (str): The name of the environment variable to set.
            value (Union[str, int, float, bool, list, dict]): The value to assign to the environment variable.
                The value will be serialized before being written to the `.env` file.
        Notes:
            - The value is serialized for storage in the `.env` file.
            - The environment variable is also set in the current process's environment, making it immediately available.
        """

        # Serializes and sets the value of an environment variable in the `.env` file.
        serialized_value = self.__serializeValue(value)

        # Sets the value in the `.env` file
        set_key(str(self._resolved_path), key, serialized_value)

        # Also sets the value in the system environment variables
        # so that it is available in the current environment.
        # This is useful if you need to access the environment variable immediately
        os.environ[key] = str(value)

        # Return True to indicate that the operation was successful
        return True

    def unset(self, key: str) -> bool:
        """
        Removes an environment variable from both the `.env` file and the current system environment.
        Args:
            key (str): The name of the environment variable to remove.
        This method updates the `.env` file by removing the specified key and also ensures
        that the variable is no longer present in the current process's environment variables.
        """

        # Removes an environment variable from the `.env` file and from the system environment.
        unset_key(str(self._resolved_path), key)

        # Also removes the environment variable from the system
        # so that it is not available in the current environment.
        os.environ.pop(key, None)

        # Return True to indicate that the operation was successful
        return True

    def all(self) -> dict:
        """
        Returns all environment variables from the `.env` file as a dictionary.

        Reads the environment variables from the resolved `.env` file path, parses each value
        using the `__parseValue` method, and returns a dictionary mapping variable names to their
        parsed values.

        Returns:
            dict: A dictionary containing all environment variables and their parsed values.
        """

        # Returns all environment variables from the `.env` file as a dictionary,
        # parsing the values using __parseValue.
        raw_values = dotenv_values(self._resolved_path)
        return {k: self.__parseValue(v) for k, v in raw_values.items()}

    def toJson(self) -> str:
        """
        Converts the environment variables from the `.env` file into a JSON string.

        This method retrieves all environment variables, parses their values using the
        `__parseValue` method, and returns a JSON string representation of the resulting dictionary.

        Returns:
            str: A JSON string representing all environment variables and their parsed values.
        """

        # Converts the environment variables to a JSON string.
        import json
        return json.dumps(self.all(), indent=4)

    def toBase64(self) -> str:
        """
        Converts the environment variables from the `.env` file into a Base64 encoded string.

        This method retrieves all environment variables, parses their values using the
        `__parseValue` method, and returns a Base64 encoded string representation of the resulting dictionary.

        Returns:
            str: A Base64 encoded string representing all environment variables and their parsed values.
        """

        # Converts the environment variables to a Base64 encoded string.
        import base64
        import json
        return base64.b64encode(json.dumps(self.all()).encode()).decode()

    def __parseValue(self, value: Any) -> Any:
        """
        Parses a given value and attempts to convert it into an appropriate Python data type.
        The function handles the following conversions:
            - Returns None for None, empty strings, or string representations of null values ('none', 'null', 'nan').
            - Returns the value unchanged if it is already a primitive type (bool, int, float).
            - Converts string representations of booleans ('true', 'false') to their respective boolean values.
            - Converts string representations of integers and floats to their respective numeric types.
            - Attempts to evaluate the string as a Python literal (e.g., lists, dicts, tuples).
            - Returns the original string if no conversion is possible.
        Args:
            value (Any): The value to parse.
        Returns:
            Any: The parsed value in its appropriate Python data type, or the original string if no conversion is possible.
        """

        # Parses a string value into a Python data type.
        if value is None:
            return None

        # If it is already a primitive type, return it
        if isinstance(value, (bool, int, float)):
            return value

        value_str = str(value).strip()

        # Special cases: empty or representations of None
        if not value_str or value_str.lower() in {'none', 'null', 'nan'}:
            return None

        # Booleans
        if value_str.lower() == 'true':
            return True
        if value_str.lower() == 'false':
            return False

        # Try to convert to int
        try:
            if value_str.isdigit() or (value_str.startswith('-') and value_str[1:].isdigit()):
                return int(value_str)
        except Exception:
            pass

        # Try to convert to float
        try:
            float_val = float(value_str)
            # Avoid converting strings like '1e10' to float if it is not really a number
            if '.' in value_str or 'e' in value_str.lower():
                return float_val
        except Exception:
            pass

        # Try to evaluate as Python literal (lists, dicts, etc.)
        try:
            return ast.literal_eval(value_str)
        except Exception:
            pass

        # If all else fails, return the original string
        return value_str

    def __serializeValue(self, value: Any) -> str:
        """
        Serializes a Python value into a string suitable for storing in a `.env` file.
        Supported types:
            - None: serialized as the string "None"
            - str: returned as-is
            - bool: converted to "true" or "false"
            - int, float: converted to their string representation
            - list, dict: converted to their string representation using repr()
        Raises:
            TypeError: If the value is an instance of a custom class or an unsupported type (e.g., set, tuple).
        Args:
            value (Any): The value to serialize.
        Returns:
            str: The serialized string representation of the value.
        """

        # if it is None, return "None"
        # This is useful to avoid problems when saving None in the .env file
        if value is None:
            return "None"

        # If it is a string, return it as is
        if isinstance(value, str):
            return value

        # If it is a boolean, convert it to string
        if isinstance(value, bool):
            return str(value).lower()

        # If it is a number, convert it to string
        if isinstance(value, int):
            return str(value)

        # If is a float, convert it to string
        if isinstance(value, float):
            value = str(value)
            if 'e' in value or 'E' in value:
                raise ValueError('scientific notation is not supported, use a string instead')
            return value

        # If it is a list or dictionary, convert them to string
        if isinstance(value, (list, dict)):
            return repr(value)

        # If it is an object of a custom class, raise an error
        # This is useful to avoid problems when saving class instances in the .env file
        if hasattr(value, '__dict__'):
            raise TypeError(f"Type {type(value).__name__} is not serializable for .env")

        # If it is an unsupported data type, raise an error
        # This is useful to avoid problems when saving unsupported data types in the .env file
        # such as sets, tuples, etc.
        if not isinstance(value, (list, dict, bool, int, float, str)):
            raise TypeError(f"Type {type(value).__name__} is not serializable for .env")

        # Serializes a Python data type into a string for storing in the `.env` file.
        # Only allows simple serializable types and not class instances.
        if isinstance(value, (list, dict, bool, int, float, str)):
            # Prevent serializing instances of custom classes
            if type(value).__module__ != "builtins" and not isinstance(value, str):
                raise TypeError(f"Type {type(value).__name__} is not serializable for .env")
            return repr(value) if not isinstance(value, str) else value
        raise TypeError(f"Type {type(value).__name__} is not serializable for .env")
