from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orionis.console.entities.command import Command
    from orionis.console.contracts.command import ICommand

class ILoader(ABC):

    @abstractmethod
    def get(self, signature: str) -> Command | None:
        """
        Retrieve a registered command by its signature.

        Load all commands if not already loaded. Return the Command instance
        associated with the given signature, or None if not found.

        Parameters
        ----------
        signature : str
            Unique identifier for the command.

        Returns
        -------
        Command or None
            The Command object if found, otherwise None.
        """

    @abstractmethod
    def all(self) -> dict[str, Command]:
        """
        Return all registered commands.

        Load core, custom, and fluent commands if not already loaded. Return the
        internal dictionary containing all registered Command instances.

        Returns
        -------
        dict[str, Command]
            Dictionary of command signatures mapped to Command objects.
        """

    @abstractmethod
    def addFluentCommand(
        self,
        signature: str,
        handler: list[type[Any], str | None],
    ) -> ICommand:
        """
        Define a new command using the fluent interface.

        Create a command with the given signature and handler. The handler must be
        a list containing the class and optionally the method name. Validate input
        types and conventions. Return the created ICommand instance.

        Parameters
        ----------
        signature : str
            Unique identifier for the command.
        handler : list of Any
            List containing the class and optionally the method name.

        Returns
        -------
        ICommand
            The created FluentCommand instance.

        Raises
        ------
        TypeError
            If the signature is not a string or the handler is not a valid list.
        ValueError
            If the signature does not meet naming conventions.
        """
