from __future__ import annotations
from orionis.services.environment.contracts.env import IEnv
from orionis.services.environment.core.dot_env import DotEnv
from typing import Any

class Env(IEnv):

    # Shared singleton instance for DotEnv
    _dotenv_instance = None

    @classmethod
    def _getSingletonInstance(
        cls,
    ) -> DotEnv:
        """
        Get the shared DotEnv singleton instance.

        Ensure that only one instance of DotEnv is created and reused throughout
        the Env class. If the instance does not exist, it will be created.

        Returns
        -------
        DotEnv
            The shared DotEnv instance used for environment variable operations.
        """
        # Check if the singleton instance has already been created
        if cls._dotenv_instance is None:

            # Create a new DotEnv instance if it does not exist
            cls._dotenv_instance = DotEnv()

        # Return the existing or newly created DotEnv instance
        return cls._dotenv_instance

    @classmethod
    def get(
        cls,
        key: str,
        default: object | None = None,
    ) -> object:
        """
        Retrieve the value of an environment variable by its key.

        Parameters
        ----------
        key : str
            The name of the environment variable to retrieve.
        default : object | None, optional
            The value to return if the environment variable is not found.
            Defaults to None.

        Returns
        -------
        object
            The value of the environment variable if it exists, otherwise the
            provided default value.
        """
        # Get the shared DotEnv singleton instance to access environment variables
        dotenv = cls._getSingletonInstance()

        # Return the value for the specified key, or the default if not present
        return dotenv.get(key, default)

    @classmethod
    def set(
        cls,
        key: str,
        value: str,
        _type: str | None = None,
    ) -> bool:
        """
        Set or update an environment variable in the .env file.

        Parameters
        ----------
        key : str
            The name of the environment variable to set or update.
        value : str
            The value to assign to the environment variable.
        _type : str | None, optional
            Type hint for the variable. Supported types include 'str', 'int',
            'float', 'bool', 'list', 'dict', 'tuple', 'set', 'base64', and
            'path'. Defaults to None.

        Returns
        -------
        bool
            True if the environment variable was set successfully, False
            otherwise.
        """
        # Get the shared DotEnv singleton instance for variable operations
        dotenv = cls._getSingletonInstance()

        # Set the environment variable with key, value, and optional type hint
        return dotenv.set(key, value, _type)

    @classmethod
    def unset(
        cls,
        key: str,
    ) -> bool:
        """
        Remove an environment variable from the .env file.

        Parameters
        ----------
        key : str
            The name of the environment variable to remove.

        Returns
        -------
        bool
            True if the environment variable was removed successfully,
            False otherwise.
        """
        # Get the shared DotEnv singleton instance for variable operations
        dotenv = cls._getSingletonInstance()

        # Remove the environment variable with the specified key
        return dotenv.unset(key)

    @classmethod
    def all(
        cls,
    ) -> dict[str, Any]:
        """
        Retrieve all environment variables as a dictionary.

        Access the shared DotEnv singleton instance and return all loaded
        environment variables in dictionary format for inspecting current
        environment configuration.

        Returns
        -------
        dict[str, Any]
            Dictionary containing all environment variables loaded by DotEnv.
        """
        # Get the shared DotEnv singleton instance to access variables
        dotenv = cls._getSingletonInstance()

        # Return all environment variables as a dictionary
        return dotenv.all()

    @classmethod
    def reload(cls) -> bool:
        """
        Reload environment variables from the .env file.

        Reset the DotEnv singleton instance and reload all environment variables
        from the .env file. Useful when the .env file has been modified
        externally and the latest values need to be reflected in the application.

        Returns
        -------
        bool
            True if the environment variables were reloaded successfully,
            False otherwise.
        """
        # Reset the singleton instance to ensure fresh reload of variables
        cls._dotenv_instance = None

        # Create a new DotEnv instance and load the .env file
        dotenv = cls._getSingletonInstance()

        # Attempt to reload environment variables from the .env file
        try:
            return dotenv.reload()
        except (OSError, ValueError):
            return False
