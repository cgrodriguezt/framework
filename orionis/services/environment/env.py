from orionis.services.environment.contracts.env import IEnv
from orionis.services.environment.dot_env import DotEnv
from typing import Any, Optional, Dict

def env(key: str, default: Any = None, is_path: bool = False) -> Any:
    """
    Retrieve the value of an environment variable by key.

    Args:
        key (str): The name of the environment variable to retrieve.
        default (Any, optional): The value to return if the key is not found. Defaults to None.
        is_path (bool, optional): If True, the value will be treated as a file path. Defaults to False.

    Returns:
        Any: The value of the environment variable if found, otherwise the default value.
    """
    return DotEnv().get(key, default, is_path)

class Env(IEnv):
    """
    Env is a utility class that provides static methods for managing environment variables
    using the DotEnv class. It allows getting, setting, unsetting, listing, destroying,
    and serializing environment variables.
    """

    _dotenv_instance: Optional[DotEnv] = None

    @classmethod
    def _dotenv(cls) -> DotEnv:
        """
        Returns a singleton instance of the DotEnv class.

        If the instance does not exist, it creates a new one and stores it in the class attribute.
        Subsequent calls will return the same instance.

        Returns:
            DotEnv: The singleton instance of the DotEnv class.
        """
        if cls._dotenv_instance is None:
            cls._dotenv_instance = DotEnv()
        return cls._dotenv_instance

    @staticmethod
    def get(key: str, default: Any = None, is_path: bool = False) -> Any:
        """
        Retrieve the value of an environment variable.

        Args:
            key (str): The name of the environment variable to retrieve.
            default (Any, optional): The value to return if the environment variable is not found. Defaults to None.
            is_path (bool, optional): If True, treat the value as a filesystem path. Defaults to False.

        Returns:
            Any: The value of the environment variable if found, otherwise the default value.
        """
        return Env._dotenv().get(key, default, is_path)

    @staticmethod
    def set(key: str, value: str, is_path: bool = False) -> bool:
        """
        Sets an environment variable with the specified key and value.

        Args:
            key (str): The name of the environment variable to set.
            value (str): The value to assign to the environment variable.
            is_path (bool, optional): If True, treats the value as a file system path. Defaults to False.

        Returns:
            bool: True if the environment variable was set successfully, False otherwise.
        """
        return Env._dotenv().set(key, value, is_path)

    @staticmethod
    def unset(key: str) -> bool:
        """
        Removes the specified environment variable from the environment.

        Args:
            key (str): The name of the environment variable to remove.

        Returns:
            bool: True if the variable was successfully removed, False otherwise.
        """
        return Env._dotenv().unset(key)

    @staticmethod
    def all() -> Dict[str, Any]:
        """
        Retrieve all environment variables as a dictionary.

        Returns:
            Dict[str, Any]: A dictionary containing all environment variables loaded by the dotenv configuration.
        """
        return Env._dotenv().all()

    @staticmethod
    def toJson() -> str:
        """
        Serializes the environment variables managed by the Env class into a JSON-formatted string.

        Returns:
            str: A JSON string representation of the environment variables.
        """
        return Env._dotenv().toJson()

    @staticmethod
    def toBase64() -> str:
        """
        Converts the environment variables loaded by the dotenv instance to a Base64-encoded string.

        Returns:
            str: The Base64-encoded representation of the environment variables.
        """
        return Env._dotenv().toBase64()
