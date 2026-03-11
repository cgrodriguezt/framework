from __future__ import annotations
from typing import TYPE_CHECKING, Any
from orionis.console.base.contracts.command import IBaseCommand
from orionis.console.output.console import Console

if TYPE_CHECKING:
    from orionis.console.args.argument import Argument

class BaseCommand(Console, IBaseCommand):

    # ruff: noqa: ANN401

    # Enable timestamps in console output by default
    timestamps: bool = True

    # Command signature string for registration and help text generation
    signature: str

    # Human-readable description for documentation and help display
    description: str

    # List of Argument instances defining command-line options and arguments
    arguments: list[Argument] = []

    # Parsed argument values
    _arguments: dict[str, Any] = {}

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

    def getArgument(self, key: str, default: Any | None = None) -> Any | None:
        """
        Retrieve the value of a command-line argument.

        Parameters
        ----------
        key : str
            The name of the argument to retrieve.
        default : Any or None, optional
            The value to return if the argument is not present. Defaults to None.

        Returns
        -------
        Any or None
            The value of the argument if present, otherwise the default value.
        """
        # Validate that the key is a string
        if not isinstance(key, str):
            error_msg = "Argument key must be a string."
            raise ValueError(error_msg)

        # Return the argument value or the default if not found
        return self._arguments.get(key, default)

    def getArguments(self) -> dict[str, Any]:
        """
        Retrieve all parsed command-line arguments.

        Returns
        -------
        dict[str, Any]
            A copy of the dictionary containing all parsed arguments.
        """
        # Return a shallow copy to prevent external modification
        return self._arguments.copy()

    def _injectArguments(self, args: dict[str, Any]) -> None:
        """
        Inject parsed CLI arguments into the command instance.

        Parameters
        ----------
        args : dict[str, Any]
            Dictionary containing parsed command-line arguments.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If the provided arguments are not a dictionary.
        """
        # Ensure the input is a dictionary of arguments
        if not isinstance(args, dict):
            error_msg = "Arguments must be provided as a dictionary."
            raise TypeError(error_msg)

        # Store the parsed arguments in the internal state for later retrieval
        self._arguments.update(args)