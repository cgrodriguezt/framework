from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class ICLIRequest(ABC):

    # ruff: noqa: ANN401

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

    @property
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
    def arguments(self) -> dict[str, Any]:
        """
        Return all parsed command-line arguments and options.

        Provides direct access to the internal arguments dictionary for the command.

        Returns
        -------
        Dict[str, Any]
            The dictionary of all parsed arguments and options.
        """

    @abstractmethod
    def argument(self, key: str, default: Any = None) -> Any:
        """
        Retrieve the value of a command-line argument by key, with optional default.

        Parameters
        ----------
        key : str
            Argument name to retrieve.
        default : Any, optional
            Value to return if key is not found. Defaults to None.

        Returns
        -------
        Any
            Value of the argument if found, else the default value.

        Raises
        ------
        ValueError
            If key is not a string or internal arguments are not a dictionary.
        """
