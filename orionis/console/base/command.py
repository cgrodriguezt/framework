from __future__ import annotations
from typing import TYPE_CHECKING, Any, ClassVar
from orionis.console.contracts.base_command import IBaseCommand
from orionis.console.dynamic.progress_bar import ProgressBar
from orionis.console.output.console import Console

if TYPE_CHECKING:
    from orionis.console.args.argument import CLIArgument

class BaseCommand(Console, ProgressBar, IBaseCommand):

    # Enable timestamps in console output by default
    timestamps: bool = True

    # Command signature string for registration and help text generation
    signature: str

    # Human-readable description for documentation and help display
    description: str

    # Dictionary to store parsed command-line arguments and options
    __args: ClassVar[dict[str, Any]] = {}

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
        # Validate that the provided arguments are a dictionary
        if not isinstance(args, dict):
            error_msg = (
                f"Arguments must be a dictionary, got "
                f"'{type(args).__name__}' instead."
            )
            raise TypeError(error_msg)

        # Validate that all keys in the arguments dictionary are strings
        for key in args:
            if not isinstance(key, str):
                error_msg = (
                    "Argument keys must be strings, got "
                    f"'{type(key).__name__}' instead."
                )
                raise TypeError(error_msg)

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
        return self.__args

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
        # Validate that the key is a string
        if not isinstance(key, str):
            error_msg = (
                f"Argument key must be a string, got '{type(key).__name__}' instead."
            )
            raise TypeError(error_msg)

        # Ensure internal arguments are stored as a dictionary
        if not isinstance(self.__args, dict):
            error_msg = (
                f"Arguments must be a dictionary, got "
                f"'{type(self.__args).__name__}' instead."
            )
            raise TypeError(error_msg)

        # Return the argument value or the default if not found
        return self.__args.get(key, default)
