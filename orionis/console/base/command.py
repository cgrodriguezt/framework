from __future__ import annotations
from typing import TYPE_CHECKING, Any
from orionis.console.base.contracts.command import IBaseCommand
from orionis.console.output.console import Console

if TYPE_CHECKING:
    from orionis.console.args.argument import CLIArgument

class BaseCommand(Console, IBaseCommand):

    # ruff: noqa: ANN401

    # Enable timestamps in console output by default
    timestamps: bool = True

    # Command signature string for registration and help text generation
    signature: str

    # Human-readable description for documentation and help display
    description: str

    def __init__(self) -> None:
        """
        Initialize the BaseCommand instance.

        Initializes the internal arguments dictionary and calls the superclass
        initializer.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__()
        self.__args: dict[str, Any] = {}

    def argumentDefinitions(self) -> list[CLIArgument]:
        """
        Define the command-line arguments and options for the command.

        Returns
        -------
        list of CLIArgument
            List of argument and option definitions for the command.
        """
        # Return an empty list by default; override in subclasses as needed
        return []

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
        error_msg = "The 'handle' method must be implemented in the subclass."
        raise NotImplementedError(error_msg)

    def _injectArguments(self, args: dict[str, Any]) -> None:
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
        """
        # Assign the parsed arguments to the internal storage
        self.__args = args

    def arguments(self) -> dict[str, Any]:
        """
        Return all parsed command-line arguments and options.

        Provides direct access to the internal arguments dictionary for the command.

        Returns
        -------
        Dict[str, Any]
            The dictionary of all parsed arguments and options.
        """
        # Return the internal arguments dictionary
        return self.__args.copy()

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
        # Validate that the key is a string
        if not isinstance(key, str):
            error_msg = (
                f"Argument key must be a string, got '{type(key).__name__}' instead."
            )
            raise TypeError(error_msg)

        # Return the argument value or the default if not found
        value = self.__args.get(key)
        if value is None:
            return default
