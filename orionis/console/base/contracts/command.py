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
        Specify the command-line arguments and options for the command.

        This asynchronous method should be overridden in subclasses to return a list
        of CLIArgument objects, each describing a supported argument or option.

        Returns
        -------
        List[CLIArgument]
            An empty list by default. Subclasses should return a list of CLIArgument
            objects representing the accepted arguments and options.
        """

    @abstractmethod
    async def handle(self) -> None:
        """
        Run the main logic for the command.

        This method must be implemented by subclasses to define the command's
        behavior. It is called after argument parsing and validation.

        Returns
        -------
        None
            No value is returned. Output should be handled via console methods.

        Raises
        ------
        NotImplementedError
            Raised if not implemented in a subclass.
        """

    @abstractmethod
    def setArguments(self, args: dict[str, Any]) -> None:
        """
        Set the internal arguments dictionary with parsed command-line arguments.

        Parameters
        ----------
        args : Dict[str, Any]
            Dictionary of parsed command-line arguments and options.

        Returns
        -------
        None
            No return value.

        Raises
        ------
        ValueError
            If `args` is not a dictionary.
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
    def argument(self, key: str, default: str | None = None) -> object:
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
