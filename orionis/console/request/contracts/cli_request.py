from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class ICLIRequest(ABC):

    @property
    @abstractmethod
    def signature(self) -> str:
        """
        Return the command signature.

        Returns
        -------
        str
            The command signature as a string.
        """

    @abstractmethod
    def setCommand(self, command: str) -> None:
        """
        Set the command name for this CLI request.

        Parameters
        ----------
        command : str
            The command name to set.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If the provided command is not a string.
        """

    @abstractmethod
    def setArguments(self, args: dict) -> None:
        """
        Set the command line arguments for this CLI request.

        Parameters
        ----------
        args : dict
            Dictionary of command line arguments to set.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If the provided args is not a dictionary.
        """

    @abstractmethod
    def command(self) -> str:
        """
        Return the command name for this CLI request.

        Returns
        -------
        str
            The command name as a string.
        """

    @abstractmethod
    def arguments(self) -> dict:
        """
        Return all command line arguments as a dictionary.

        Provides direct access to the internal arguments dictionary containing
        all parsed CLI parameters.

        Returns
        -------
        dict
            Dictionary of argument names and their corresponding values.
        """

    @abstractmethod
    def argument(self, name: str, default: type[Any] | None = None) -> type[Any] | None:
        """
        Get the value of a command line argument by name.

        Parameters
        ----------
        name : str
            Name of the argument to retrieve.
        default : Any or None, optional
            Value to return if the argument is not found. Defaults to None.

        Returns
        -------
        Any or None
            Value of the argument if present, otherwise the default value.
        """
