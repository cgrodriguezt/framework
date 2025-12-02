from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from orionis.console.contracts.command import ICommand

class IReactor(ABC):

    @abstractmethod
    def command(
        self,
        signature: str,
        handler: list[type[Any], str | None],
    ) -> ICommand:
        """
        Define a new command using a fluent interface.

        Create a command with the specified signature and handler.
        Chain methods to configure additional properties.

        Parameters
        ----------
        signature : str
            Unique identifier for the command. Must follow naming conventions.
        handler : list[type[Any], str | None]
            List containing the handler type and optional handler name.

        Returns
        -------
        ICommand
            Instance for further configuration via method chaining.

        Raises
        ------
        TypeError
            If signature is not str or handler is not callable.
        ValueError
            If signature does not meet naming conventions.
        """

    @abstractmethod
    def info(self) -> list[dict]:
        """
        Retrieve metadata for all registered commands.

        Return a list of dictionaries with command signature, description, and
        timestamps status.

        Returns
        -------
        list[dict]
            List of command metadata dictionaries.

        """

    @abstractmethod
    def call(
        self,
        signature: str,
        args: list[str] | None = None,
    ) -> object | None:
        """
        Execute a registered command synchronously by signature.

        Find and run a command using its signature and optional arguments.
        Handle timing, logging, and errors.

        Parameters
        ----------
        signature : str
            Unique identifier of the command to execute.
        args : Optional[List[str]], default None
            Arguments to pass to the command.

        Returns
        -------
        object | None
            Output from the command's handle method, or None on error.

        Raises
        ------
        CLIOrionisValueError
            If command is not found.
        SystemExit
            If argument parsing fails.
        Exception
            Propagates exceptions after logging.

        Notes
        -----
        - Logs execution and errors if timestamps enabled.
        - Parses and injects arguments into the command.
        """
