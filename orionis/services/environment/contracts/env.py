from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class IEnv(ABC):

    @classmethod
    @abstractmethod
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

    @classmethod
    @abstractmethod
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

    @classmethod
    @abstractmethod
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

    @classmethod
    @abstractmethod
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

    @classmethod
    @abstractmethod
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
