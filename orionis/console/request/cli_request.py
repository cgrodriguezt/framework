from __future__ import annotations
from typing import Any
from orionis.console.request.contracts.cli_request import ICLIRequest

class CLIRequest(ICLIRequest):

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

    def setCommand(self, command: str) -> None:
        """
        Set the command name for this CLI request.

        Parameters
        ----------
        command : str
            The command name to set.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If the provided command is not a string.
        """
        # Validate that the command is a string
        if not isinstance(command, str):
            error_msg = "Command must be a string"
            raise TypeError(error_msg)

        # Update the private attribute with the new command name
        self.__command = command

    def setArguments(self, args: dict) -> None:
        """
        Set the command line arguments for this CLI request.

        Parameters
        ----------
        args : dict
            Dictionary of command line arguments to set.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If the provided args is not a dictionary.
        """
        # Validate that args is a dictionary
        if not isinstance(args, dict):
            error_msg = "Args must be a dictionary"
            raise TypeError(error_msg)

        # Update the private attribute with the new arguments
        self.__args = args

    def command(self) -> str:
        """
        Return the command name for this CLI request.

        Returns
        -------
        str
            The command name as a string.
        """
        # Return the command name stored in the private attribute
        return self.__command

    def arguments(self) -> dict:
        """
        Return all command line arguments as a dictionary.

        Provides direct access to the internal arguments dictionary containing
        all parsed CLI parameters.

        Returns
        -------
        dict
            Dictionary of argument names and their corresponding values.
        """
        # Return the internal arguments dictionary for full access to CLI parameters
        return self.__args

    def argument(self, name: str, default: type[Any] | None = None) -> type[Any] | None:
        """
        Get the value of a command line argument by name.

        Parameters
        ----------
        name : str
            Name of the argument to retrieve.
        default : Any or None, optional
            Value to return if the argument is not found. Defaults to None.

        Returns
        -------
        Any or None
            Value of the argument if present, otherwise the default value.
        """
        # Check if the argument exists and is not None
        if name not in self.__args or self.__args[name] is None:
            return default

        # Return the argument value or default if not found
        return self.__args.get(name, default)
