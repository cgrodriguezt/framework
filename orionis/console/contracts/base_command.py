from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from orionis.console.args.argument import CLIArgument

class IBaseCommand(ABC):

    # Enable timestamps in console output by default
    timestamps: bool = True

    # Command signature string for registration and help text generation
    signature: str

    # Human-readable description for documentation and help display
    description: str

    @abstractmethod
    async def options(self) -> list[CLIArgument]:
        """
        Define the command-line arguments and options accepted by the command.

        This asynchronous method should be overridden to specify the list of
        CLIArgument objects representing the arguments and options supported.

        Returns
        -------
        List[CLIArgument]
            Returns a list of CLIArgument objects. If no arguments are defined,
            returns an empty list.
        """

    @abstractmethod
    async def handle(self) -> None:
        """
        Execute the main logic for the command.

        This method is the entry point for command execution and must be implemented
        by subclasses. It is called after argument parsing and validation.

        Returns
        -------
        None
            No value is returned. All output should be handled via side effects.
        """

    @abstractmethod
    def setArguments(self, args: dict[str, Any]) -> None:
        """
        Set the internal arguments dictionary with parsed CLI arguments.

        Parameters
        ----------
        args : dict of str to Any
            Dictionary containing parsed CLI arguments and options.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        ValueError
            If `args` is not a dictionary.
        """

    @abstractmethod
    def arguments(self) -> dict[str, Any]:
        """
        Return parsed command-line arguments and options.

        Returns
        -------
        dict[str, Any]
            Dictionary containing all parsed CLI arguments and options.
        """

    @abstractmethod
    def argument(self, key: str, default: str | None = None) -> object:
        """
        Retrieve a command-line argument value by key with optional default.

        Parameters
        ----------
        key : str
            String identifier for the argument in the internal dictionary.
        default : object, optional
            Value to return if key is not found. Defaults to None.

        Returns
        -------
        object
            Value associated with the key, or the default if not found.

        Raises
        ------
        ValueError
            If key is not a string.
        ValueError
            If internal __args attribute is not a dictionary.
        """
