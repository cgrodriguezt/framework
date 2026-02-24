import argparse
import sys
from typing import TYPE_CHECKING, Any
from orionis.console.core.loader import Loader
from orionis.console.core.contracts.reactor import IReactor
from orionis.console.entities.command import Command
from orionis.console.fluent.contracts.command import ICommand
from orionis.console.output.executor import Executor
from orionis.console.output.help_command import HelpCommand
from orionis.console.request.cli_request import CLIRequest
from orionis.failure.contracts.catch import ICatch
from orionis.failure.enums.kernel_type import KernelContext
from orionis.foundation.contracts.application import IApplication
from orionis.services.log.contracts.log_service import ILogger
from orionis.support.performance.counter import PerformanceCounter

if TYPE_CHECKING:
    from orionis.console.base.contracts.command import IBaseCommand

class Reactor(IReactor):

    # ruff: noqa: PLR0913, SLF001, BLE001,TRY400, TC001

    def __init__(
        self,
        app: IApplication,
        loader: Loader,
        executer: Executor,
        logger: ILogger,
        catch: ICatch,
        performance_counter: PerformanceCounter,
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

        # Store the catch instance for exception handling
        self.__catch = catch

        # Initialize cache for command information
        self.__cache_info: list[dict] | None = None

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
        RuntimeError
            Raised if argument parsing fails for reasons other than SystemExit.
        """
        # Initialize parsed_args to None
        parsed_args = None

        # Parse arguments only if the command expects them and has an ArgumentParser
        if (
            command.args is not None and
            isinstance(command.args, argparse.ArgumentParser)
        ):

            # Use an empty list if no arguments are provided
            if args is None:
                args = []

            # Try to parse the provided arguments using the command's ArgumentParser
            try:
                parsed_args = command.args.parse_args(args)

            # Handle ArgumentError by raising a RuntimeError with details
            except BaseException:
                HelpCommand.printActions(
                    command.signature,
                    command.args._actions,
                )
                sys.exit()

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

    async def info(self) -> list[dict]:
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
        # Return cached command info if already computed
        if self.__cache_info:
            return self.__cache_info

        # Prepare a list to hold command information
        commands_info = []

        # Ensure all commands are loaded before retrieving their information
        all_commands: dict[str, Command] = await self.__loader.all()

        # Iterate through all registered commands in the internal registry
        for command in all_commands.values():

            # Skip internal commands (those with double underscores)
            if command.signature.startswith("__") and command.signature.endswith("__"):
                continue

            # Append command information to the list
            commands_info.append({
                "signature": command.signature,
                "description": command.description,
            })

        # Return the sorted list of command information by signature
        self.__cache_info = sorted(commands_info, key=lambda x: x["signature"])
        return self.__cache_info

    async def call(
        self,
        signature: str,
        args: list[str] | None = None,
    ) -> int:
        """
        Execute a registered command by its signature.

        Parameters
        ----------
        signature : str
            Command signature to execute.
        args : list of str or None, optional
            Arguments to pass to the command.

        Returns
        -------
        int
            The output produced by the command execution.

        Raises
        ------
        ValueError
            If the command is not found.
        Exception
            If command execution fails.
        """
        # Create a new scope for the command execution context
        async with self.__app.beginScope() as scope:

            # Set the kernel type in the scope for contextual awareness
            # during command execution
            scope.set("kernel", KernelContext.CONSOLE)

            # Initialize a CLIRequest instance for this command execution
            request = CLIRequest(command=signature)

            # Inject a new CLIRequest instance into the application
            # scope for this command execution
            self.__app.scopedInstanceWithoutContract(request)

            # Validate that the command signature is a string
            if not isinstance(signature, str):
                error_msg = "Command signature must be a string."
                await self.__catch.exception(TypeError(error_msg))
                return 1

            # Validate that the command signature is not empty
            if not signature:
                error_msg = "Command signature cannot be empty."
                await self.__catch.exception(ValueError(error_msg))
                return 1

            # Retrieve the command from the registry by its signature
            command = await self.__loader.get(signature)
            if command is None:
                error_msg = f"Command '{signature}' not found."
                await self.__catch.exception(ValueError(error_msg))
                return 1

            # Start execution timer for performance measurement
            await self.__performance_counter.astart()

            try:

                # Log the command execution start if timestamps are enabled
                if command.timestamps:
                    self.__executer.running(program=signature)

                # Parse and deep copy the arguments to avoid side effects
                dict_args = self.__parseCommandArgs(command, args)

                # Set arguments in the CLIRequest instance
                request._inject_arguments(dict_args)

                # Instantiate the command class using the application container
                command_instance: IBaseCommand = await self.__app.build(command.obj)

                # Set arguments in the command instance if possible
                if hasattr(command_instance, "_inject_arguments"):
                    command_instance._inject_arguments(dict_args)

                # Execute the command's handle method and capture its output
                await self.__app.call(command_instance, command.method)

                # Stop the timer and log completion if timestamps are enabled
                await self.__performance_counter.astop()
                elapsed_time = round(await self.__performance_counter.agetSeconds(), 2)
                if command.timestamps:
                    self.__executer.done(program=signature, time=f"{elapsed_time}s")

                # Log successful execution
                info_msg = (
                    f"Command '{signature}' executed successfully in "
                    f"({elapsed_time}) seconds."
                )
                self.__logger.info(info_msg)

                # Return success code
                return 0

            except Exception as e:

                # Log the error in the logger service
                error_msg = f"Command '{signature}' execution failed: {e}"
                self.__logger.error(error_msg)

                # Stop the timer and log failure if timestamps are enabled
                await self.__performance_counter.astop()
                elapsed_time = round(await self.__performance_counter.agetSeconds(), 2)
                if command and command.timestamps:
                    self.__executer.fail(program=signature, time=f"{elapsed_time}s")

                # Delegate exception handling to the catch service
                await self.__catch.exception(e)

                # Return a failure code
                return 1
