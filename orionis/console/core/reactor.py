from __future__ import annotations
import argparse
from typing import TYPE_CHECKING, Any
from orionis.console.contracts.cli_request import ICLIRequest
from orionis.console.contracts.reactor import IReactor
from orionis.console.exceptions import CLIOrionisRuntimeError
from orionis.console.request.cli_request import CLIRequest
from orionis.services.introspection.instances.reflection import ReflectionInstance

if TYPE_CHECKING:
    from orionis.console.contracts.base_command import IBaseCommand
    from orionis.console.contracts.loader import ILoader
    from orionis.console.entities.command import Command
    from orionis.console.contracts.executor import IExecutor
    from orionis.services.log.contracts.log_service import ILogger
    from orionis.support.performance.contracts.counter import IPerformanceCounter
    from orionis.console.contracts.command import ICommand
    from orionis.foundation.contracts.application import IApplication

class Reactor(IReactor):

    def __init__(
        self,
        app: IApplication,
        loader: ILoader,
        executer: IExecutor,
        logger: ILogger,
        performance_counter: IPerformanceCounter,
    ) -> None:
        """
        Initialize Reactor instance for command discovery and management.

        Set up the command processing environment, establish the application context,
        and initialize internal registries for command lookup and execution.

        Parameters
        ----------
        app : IApplication
            Application instance for command processing.

        Returns
        -------
        None
            This constructor does not return any value.
        """
        # Set the application instance for command processing
        self.__app = app

        # Initialize the list for fluent command definitions
        self.__loader = loader

        # Initialize the executor for command output management
        self.__executer = executer

        # Initialize the logger service for logging command execution details
        self.__logger = logger

        # Initialize the performance counter for measuring command execution time
        self.__performance_counter = performance_counter

    def __parseCommandArgs(
        self,
        command: Command,
        args: list[str] | None = None,
    ) -> dict:
        """
        Parse command-line arguments for a command using its ArgumentParser.

        Parameters
        ----------
        command : Command
            Command object containing the argument parser and metadata.
        args : Optional[list[str]], default None
            List of command-line arguments to parse. If None, an empty list is used.

        Returns
        -------
        dict
            Dictionary with parsed argument names and values. Returns an empty dict
            if no arguments are expected or provided.

        Raises
        ------
        SystemExit
            Raised by argparse if argument parsing fails or help is requested.
        CLIOrionisRuntimeError
            Raised if argument parsing fails for reasons other than SystemExit.
        """
        # Initialize parsed_args to None
        parsed_args = None

        # Parse arguments only if the command expects them and has an ArgumentParser
        if (command.args is not None and
            isinstance(command.args, argparse.ArgumentParser)):

            # Use an empty list if no arguments are provided
            if args is None:
                args = []

            # Try to parse the provided arguments using the command's ArgumentParser
            try:
                parsed_args = command.args.parse_args(args)

            # Handle ArgumentError by raising a CLIOrionisRuntimeError with details
            except argparse.ArgumentError as e:
                error_msg = (
                    "Failed to parse arguments for command "
                    f"'{command.signature}': {e}\n"
                    f"{command.args.format_help()}\n"
                    "Please check the command syntax and available options."
                )
                raise CLIOrionisRuntimeError(error_msg) from e

            # Handle SystemExit, which occurs on invalid arguments or help request
            except SystemExit:
                error_msg = (
                    f"Argument parsing for command '{command.signature}' resulted in "
                    "SystemExit. This typically occurs when invalid arguments are "
                    "provided or help is requested."
                )
                raise SystemExit(error_msg) from None

        # Convert the parsed arguments to a dictionary if possible
        if isinstance(parsed_args, argparse.Namespace):
            return vars(parsed_args)

        # Return parsed_args directly if it is already a dictionary
        if isinstance(parsed_args, dict):
            return parsed_args

        # Return an empty dictionary if no arguments were parsed
        return {}

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
        # Register the command using the loader's fluent interface
        return self.__loader.addFluentCommand(signature, handler)

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
        # Prepare a list to hold command information
        commands_info = []

        # Iterate through all registered commands in the internal registry
        for command in self.__loader.all().values():

            # Skip internal commands (those with double underscores)
            if command.signature.startswith("__") and command.signature.endswith("__"):
                continue

            # Append command information to the list
            commands_info.append({
                "signature": command.signature,
                "description": command.description,
            })

        # Return the sorted list of command information by signature
        return sorted(commands_info, key=lambda x: x["signature"])

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
        # Scope Request instances to this command execution context
        with self.__app.createScope():

            # Retrieve the command from the registry by its signature
            command = self.__loader.get(signature)
            if command is None:
                error_msg = f"Command '{signature}' not found."
                raise ValueError(error_msg)

            # Start execution timer for performance measurement
            self.__performance_counter.start()

            # Log the command execution start with RUNNING state if timestamps enabled
            if command.timestamps:
                self.__executer.running(program=signature)

            try:

                # Instantiate the command class using the application container
                command_instance: IBaseCommand = self.__app.build(command.obj)

                # Inject parsed arguments into the command instance
                dict_args = self.__parseCommandArgs(command, args)

                # Only set arguments if the command instance has a setArguments method
                if ReflectionInstance(command_instance).hasMethod("setArguments"):
                    command_instance.setArguments(dict_args.copy())

                # Inject a scoped CLIRequest instance into the application container
                self.__app.scopedInstance(
                    ICLIRequest,
                    CLIRequest(
                        command=signature,
                        args=dict_args.copy(),
                    ),
                )

                # Execute the command's handle method and capture its output
                output = self.__app.call(command_instance, command.method)

                # Calculate elapsed time and log completion with DONE state if enabled
                self.__performance_counter.stop()
                elapsed_time = round(self.__performance_counter.getSeconds(), 2)
                if command.timestamps:
                    self.__executer.done(program=signature, time=f"{elapsed_time}s")

                # Log successful execution in the logger service
                info_msg = (
                    f"Command '{signature}' executed successfully in "
                    f"({elapsed_time}) seconds."
                )
                self.__logger.info(info_msg)

                # Return the output produced by the command, if any
                return output

            except Exception as e:

                # Log the error in the logger service
                error_msg = f"Command '{signature}' execution failed: {e}"
                self.__logger.error(error_msg)  # noqa: TRY400

                # Calculate elapsed time and log failure with ERROR state if enabled
                self.__performance_counter.stop()
                elapsed_time = round(self.__performance_counter.getSeconds(), 2)
                if command.timestamps:
                    self.__executer.fail(program=signature, time=f"{elapsed_time}s")

                # Propagate the exception after logging
                raise
