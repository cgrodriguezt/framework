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
        Register a fluent command with the given signature and handler.

        Parameters
        ----------
        signature : str
            Command signature to register.
        handler : list of type[Any], str or None
            Handler class and optional method name.

        Returns
        -------
        ICommand
            The registered command instance.
        """

    @abstractmethod
    def info(self) -> list[dict]:
        """
        Return registered commands metadata.

        Retrieve all loaded commands from the internal registry, skipping internal
        commands (those with double underscores). Each command is represented as a
        dictionary containing its signature and description.

        Returns
        -------
        list of dict
            List of dictionaries with 'signature' and 'description' for each command.
        """

    @abstractmethod
    def call(
        self,
        signature: str,
        args: list[str] | None = None,
    ) -> object | None:
        """
        Execute a registered command by its signature.

        Parameters
        ----------
        signature : str
            Signature of the command to execute.
        args : list of str or None, optional
            List of arguments to pass to the command.

        Returns
        -------
        object or None
            Output produced by the command, or None if no output is returned.

        Raises
        ------
        ValueError
            If the command is not found.
        Exception
            If command execution fails.
        """
