from __future__ import annotations
from typing import Any
from orionis.console.request.contracts.cli_request import ICLIRequest

class CLIRequest(ICLIRequest):

    # ruff: noqa: ANN401

    @property
    def signature(self) -> str:
        """
        Return the command signature.

        Returns
        -------
        str
            The command signature as a string.
        """
        return self.__command

    @property
    def command(self) -> str:
        """
        Return the command name for this CLI request.

        Returns
        -------
        str
            The command name as a string.
        """
        return self.__command

    def __init__(
        self,
        command: str | None = None,
        args: dict | None = None,
    ) -> None:
        """
        Initialize CLIRequest with command and arguments.

        Parameters
        ----------
        command : str or None, optional
            Command name for the CLI request.
        args : dict or None, optional
            Dictionary of command line arguments.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If args is not a dictionary or command is not a string.
        """
        # Initialize args as empty dict if not provided
        if args is None:
            args = {}

        # Ensure args is a dictionary
        if not isinstance(args, dict):
            error_msg = "Args must be a dictionary"
            raise TypeError(error_msg)

        # Ensure command is a string if provided
        if command and not isinstance(command, str):
            error_msg = "Command must be a string"
            raise TypeError(error_msg)

        # Store command and arguments as private attributes
        self.__command = command
        self.__args = args

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
        return self.__args.get(key, default)

