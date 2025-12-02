from __future__ import annotations
import argparse
import os
from pathlib import Path
import re
from typing import Any
from orionis.console.args.argument import CLIArgument
from orionis.console.base.command import BaseCommand
from orionis.console.contracts.base_command import IBaseCommand
from orionis.console.contracts.cli_request import ICLIRequest
from orionis.console.contracts.command import ICommand
from orionis.console.contracts.reactor import IReactor
from orionis.console.entities.command import Command
from orionis.console.exceptions import CLIOrionisValueError, CLIOrionisRuntimeError
from orionis.console.contracts.executor import IExecutor
from orionis.console.exceptions import CLIOrionisTypeError
from orionis.console.request.cli_request import CLIRequest
from orionis.foundation.contracts.application import IApplication
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.services.introspection.instances.reflection import ReflectionInstance
from orionis.services.introspection.modules.reflection import ReflectionModule
from orionis.services.log.contracts.log_service import ILogger
from orionis.support.performance.contracts.counter import IPerformanceCounter
from orionis.console.fluent.command import Command as FluentCommand

class Reactor(IReactor):

    def __init__(
        self,
        app: IApplication,
    ):
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

        # Initialize the internal command registry
        self.__commands: dict[str, Command] = {}

        # Initialize the executor for command output management
        self.__executer: IExecutor = self.__app.make(IExecutor)

        # Initialize the logger service for logging command execution details
        self.__logger: ILogger = self.__app.make(ILogger)

        # Initialize the performance counter for measuring command execution time
        self.__performance_counter: IPerformanceCounter = self.__app.make(IPerformanceCounter)

        # List to hold fluent command definitions
        self.__fluent_commands: list[ICommand] = []

    def __loadCommands(self) -> None:
        """
        Load all available commands into the internal registry.

        This method loads core, custom, and fluent commands into the reactor's registry.
        It uses internal flags to avoid duplicate loading and ensures each command set
        is loaded only once per instance.

        The loading order is:
            1. Core commands (if not loaded)
            2. Custom commands (if not loaded)
            3. Fluent commands (if not loaded)

        Custom commands can override core commands if they share the same signature.

        Returns
        -------
        None
            The method does not return any value. All commands are registered internally.
        """
        # Load core commands if not already loaded
        if not hasattr(self, "_Reactor__load__core_commands") or not self.__load__core_commands:
            self.__loadCoreCommands()
            self.__load__core_commands = True

        # Load custom user-defined commands if not already loaded
        if not hasattr(self, "_Reactor__load__custom_commands") or not self.__load__custom_commands:
            self.__loadCustomCommands()
            self.__load__custom_commands = True

        # Load fluent interface commands if not already loaded
        if not hasattr(self, "_Reactor__load_fluent_commands") or not self.__load_fluent_commands:
            self.__loadFluentCommands()
            self.__load_fluent_commands = True

    def __loadFluentCommands(self) -> None: # NOSONAR
        """
        Load and register commands defined using the fluent interface.

        Iterate through all commands defined via the fluent interface and register
        them in the internal command registry. Validate structure and metadata before
        registration. Return None.
        """
        # Import library for dynamic module importing
        import importlib

        # Get the routes directory path from the application instance
        routes_path = self.__app.path("routes")

        # Check if routes directory exists
        if not os.path.exists(routes_path):
            return

        # Get the project root directory for module path resolution
        root_path = str(self.__app.path("root"))

        # List all .py files in the routes directory and subdirectories
        for current_directory, _, files in os.walk(routes_path):

            # Iterate through each file in the current directory
            for file in files:

                # Only process Python files
                if file.endswith(".py"):

                    # Construct the full file path
                    file_path = os.path.join(current_directory, file)

                    # Read file content to check for Reactor.command usage
                    try:

                        # Open and read the file content
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read()

                        # Check if the file contains a Reactor.command definition
                        if "from orionis.support.facades.reactor import Reactor" in content:

                            # Sanitize the module path for import
                            pre_module = current_directory.replace(root_path, "")\
                                                          .replace(os.sep, ".")\
                                                          .lstrip(".")

                            # Remove virtual environment paths
                            pre_module = re.sub(
                                r"[^.]*\.(?:Lib|lib)\.(?:python[^.]*\.)?site-packages\.?",
                                "",
                                pre_module,
                            )
                            pre_module = re.sub(r"\.?v?env\.?", "", pre_module)
                            pre_module = re.sub(r"\.+", ".", pre_module).strip(".")

                            # Skip if module name is empty after cleaning
                            if not pre_module:
                                continue

                            # Create the reflection module path
                            module_name = f"{pre_module}.{file[:-3]}"

                            try:

                                # Import the module natively using importlib
                                importlib.import_module(module_name)

                            except Exception as e:

                                # Raise a runtime error if module import fails
                                error_msg = (
                                    f"Failed to import module '{module_name}' from file "
                                    f"'{file_path}': {e}"
                                )
                                raise CLIOrionisRuntimeError(error_msg) from e

                    except Exception as e:

                        # Raise a runtime error if file reading fails
                        error_msg = (
                            f"Failed to read file '{file_path}' for fluent command loading: {e}"
                        )
                        raise CLIOrionisRuntimeError(error_msg) from e

        # Import Command entity here to avoid circular imports
        from orionis.console.entities.command import Command as CommandEntity

        # Iterate through all fluent command definitions
        for f_command in self.__fluent_commands:

            # If the fluent command has a get method, retrieve its signature and command entity
            if hasattr(f_command, "get") and callable(f_command.get):

                # Get the signature and command entity from the fluent command
                values = f_command.get()
                signature: str = values[0]
                command_entity: CommandEntity = values[1]

                # Build the arguments dictionary from the CLIArgument instances
                required_args: list[CLIArgument] = command_entity.args

                # Create an ArgumentParser instance to handle the command arguments
                arg_parser = argparse.ArgumentParser(
                    usage=f"python -B reactor {signature} [options]",
                    description=f"Command [{signature}] : {command_entity.description}",
                    formatter_class=argparse.RawTextHelpFormatter,
                    add_help=True,
                    allow_abbrev=False,
                    exit_on_error=True,
                    prog=signature,
                )

                # Iterate through each CLIArgument and add it to the ArgumentParser
                for arg in required_args:
                    arg.addToParser(arg_parser)

                # Register the command in the internal registry with all its metadata
                self.__commands[signature] = Command(
                    obj=command_entity.obj,
                    method=command_entity.method,
                    timestamps=command_entity.timestamps,
                    signature=signature,
                    description=command_entity.description,
                    args=arg_parser,
                )

    def __loadCoreCommands(self) -> None:
        """
        Load and register core command classes provided by the Orionis framework.

        Discover and register core command classes bundled with the Orionis framework.
        Validate required attributes for each command and add them to the internal
        registry.

        Returns
        -------
        None
            Registers core commands internally for later lookup and execution.
        """
        # Import core command classes required by the framework
        from orionis.console.commands.__publisher__ import PublisherCommand
        from orionis.console.commands.cache_clear import CacheClearCommand
        from orionis.console.commands.help import HelpCommand
        from orionis.console.commands.make_command import MakeCommand
        from orionis.console.commands.scheduler_list import ScheduleListCommand
        from orionis.console.commands.scheduler_work import ScheduleWorkCommand
        from orionis.console.commands.test import TestCommand
        from orionis.console.commands.version import VersionCommand
        from orionis.console.commands.make_scheduler_listener import (
            MakeSchedulerListenerCommand,
        )
        from orionis.console.commands.server import ServerCommand

        # List of core command classes to load

        core_commands = [
            PublisherCommand,
            CacheClearCommand,
            HelpCommand,
            MakeCommand,
            ScheduleListCommand,
            ScheduleWorkCommand,
            TestCommand,
            VersionCommand,
            MakeSchedulerListenerCommand,
            ServerCommand,
        ]

        # Iterate and register each core command
        for obj in core_commands:

            # Get the signature attribute from the command class
            signature = ReflectionConcrete(obj).getAttribute("signature")

            # Skip if signature is not defined
            if signature is None:
                continue

            # Validate and extract required command attributes
            timestamp = self.__ensureTimestamps(obj)
            description = self.__ensureDescription(obj)
            args = self.__ensureArguments(obj)

            # Register the command in the internal registry
            self.__commands[signature] = Command(
                obj=obj,
                method="handle",
                timestamps=timestamp,
                signature=signature,
                description=description,
                args=args,
            )

    def __loadCustomCommands(self) -> None:  # NOSONAR
        """
        Load command classes from Python files in the commands directory.

        Walk through the commands directory, import Python modules, and register
        command classes that inherit from BaseCommand. Sanitize module paths and
        validate command structure before registration.

        Returns
        -------
        None
            Registers command classes internally in the reactor's command registry.
        """
        # Ensure the provided commands_path is a valid directory
        commands_path = (Path(self.__app.path("console")) / "commands").resolve()
        root_path = str(self.__app.path("root"))

        # Iterate through the command path and load command modules
        for current_directory, _, files in os.walk(commands_path):

            # Iterate through each file in the current directory
            for file in files:

                # Only process Python files
                if file.endswith(".py"):

                    # Sanitize the module path by converting filesystem path to Python module notation
                    pre_module = current_directory.replace(root_path, "")\
                        .replace(os.sep, ".")\
                        .lstrip(".")

                    # Remove virtual environment paths using regex
                    pre_module = re.sub(
                        r"[^.]*\.(?:Lib|lib)\.(?:python[^.]*\.)?site-packages\.?",
                        "",
                        pre_module,
                    )

                    # Remove any remaining .venv or venv patterns from the module path
                    pre_module = re.sub(r"\.?v?env\.?", "", pre_module)

                    # Clean up any double dots or leading/trailing dots
                    pre_module = re.sub(r"\.+", ".", pre_module).strip(".")

                    # Skip if module name is empty after cleaning
                    if not pre_module:
                        continue

                    # Create the reflection module path by combining sanitized path with filename
                    rf_module = ReflectionModule(f"{pre_module}.{file[:-3]}")

                    # Iterate through all classes found in the current module
                    for obj in rf_module.getClasses().values():

                        # Check if the class is a valid command class
                        if issubclass(obj, BaseCommand) and obj is not BaseCommand \
                                and obj is not IBaseCommand:

                            # Validate the command class structure and register it
                            timestamp = self.__ensureTimestamps(obj)
                            signature = self.__ensureSignature(obj)
                            description = self.__ensureDescription(obj)
                            args = self.__ensureArguments(obj)

                            # Add the command to the internal registry
                            self.__commands[signature] = Command(
                                obj=obj,
                                method="handle",
                                timestamps=timestamp,
                                signature=signature,
                                description=description,
                                args=args,
                            )

    def __ensureTimestamps(self, obj: IBaseCommand) -> bool:
        """
        Validate the 'timestamps' attribute of a command class.

        Check if the command class has a 'timestamps' attribute and ensure it is
        a boolean. If not present, return False. If present but not boolean, raise
        CLIOrionisTypeError.

        Parameters
        ----------
        obj : IBaseCommand
            Command class instance to validate.

        Returns
        -------
        bool
            True if 'timestamps' is present and boolean, otherwise False.

        Raises
        ------
        CLIOrionisTypeError
            If the 'timestamps' attribute exists but is not a boolean.
        """

        # Check if the command class has a timestamps attribute
        if not hasattr(obj, "timestamps"):
            return False

        # Ensure the timestamps attribute is a boolean type
        if not isinstance(obj.timestamps, bool):
            error_msg = (
                f"Command class {obj.__name__} 'timestamps' must be a boolean."
            )
            raise CLIOrionisTypeError(error_msg)

        # Return timestamps value
        return obj.timestamps

    def __ensureSignature(self, obj: IBaseCommand) -> str:
        """
        Validate the 'signature' attribute of a command class.

        Check that the command class has a 'signature' attribute, that it is a
        non-empty string, and that it matches the required pattern for command
        identification. Raise an exception if validation fails.

        Parameters
        ----------
        obj : IBaseCommand
            Command class instance to validate.

        Returns
        -------
        str
            The validated signature string.

        Raises
        ------
        CLIOrionisValueError
            If the class lacks a 'signature' attribute, if the signature is empty,
            or if the signature does not match the required pattern.
        CLIOrionisTypeError
            If the 'signature' attribute is not a string.
        """
        # Check if the command class has a signature attribute
        if not hasattr(obj, "signature"):
            error_msg = (
                f"Command class {obj.__name__} must have a 'signature' attribute."
            )
            raise CLIOrionisValueError(error_msg)

        # Ensure the signature attribute is a string type
        if not isinstance(obj.signature, str):
            error_msg = (
                f"Command class {obj.__name__} 'signature' must be a string."
            )
            raise CLIOrionisTypeError(error_msg)

        # Validate that the signature is not empty after stripping whitespace
        if obj.signature.strip() == "":
            error_msg = (
                f"Command class {obj.__name__} 'signature' cannot be an empty string."
            )
            raise CLIOrionisValueError(error_msg)

        # Define the regex pattern for valid signature format
        pattern = r"^[a-zA-Z][a-zA-Z0-9_:]*[a-zA-Z0-9]$|^[a-zA-Z]$"

        # Validate the signature against the required pattern
        if not re.match(pattern, obj.signature):
            error_msg = (
                f"Command class {obj.__name__} 'signature' must contain only "
                "alphanumeric characters, underscores (_) and colons (:), cannot "
                "start or end with underscore or colon, and cannot start with a "
                "number."
            )
            raise CLIOrionisValueError(error_msg)

        # Return the validated signature
        return obj.signature.strip()

    def __ensureDescription(self, obj: IBaseCommand) -> str:
        """
        Validate that the command class has a non-empty string description.

        Ensures the command class provides a 'description' attribute that is a
        non-empty string. Raises an exception if the attribute is missing, not a
        string, or empty after stripping whitespace.

        Parameters
        ----------
        obj : IBaseCommand
            Command class instance to validate.

        Returns
        -------
        str
            The stripped description string.

        Raises
        ------
        CLIOrionisValueError
            If the class lacks a 'description' attribute or if it is empty.
        CLIOrionisTypeError
            If the 'description' attribute is not a string.
        """
        # Check if the command class has a description attribute
        if not hasattr(obj, "description"):
            error_msg = (
                f"Command class {obj.__name__} must have a 'description' attribute."
            )
            raise CLIOrionisValueError(error_msg)

        # Ensure the description attribute is a string type
        if not isinstance(obj.description, str):
            error_msg = (
                f"Command class {obj.__name__} 'description' must be a string."
            )
            raise CLIOrionisTypeError(error_msg)

        # Validate that the description is not empty after stripping whitespace
        if obj.description.strip() == "":
            error_msg = (
                f"Command class {obj.__name__} 'description' cannot be an empty string."
            )
            raise CLIOrionisValueError(error_msg)

        # Return the stripped description string
        return obj.description.strip()

    def __ensureArguments(self, obj: IBaseCommand) -> argparse.ArgumentParser | None:
        """
        Validate and process command arguments for a command class.

        Ensure the command class provides a valid list of CLIArgument instances via
        its 'options' method. Construct and return an ArgumentParser if arguments
        exist, otherwise return None.

        Parameters
        ----------
        obj : IBaseCommand
            Command class instance to validate.

        Returns
        -------
        argparse.ArgumentParser | None
            ArgumentParser instance configured with the command's arguments, or None
            if no arguments are present.

        Raises
        ------
        CLIOrionisTypeError
            If the 'options' method does not return a list or contains non-CLIArgument
            instances.
        CLIOrionisRuntimeError
            If any exception occurs during argument processing.
        """
        # Instantiate the command and retrieve its options
        instance = self.__app.build(obj)

        # Call the 'options' method to get argument definitions
        options: list[CLIArgument] = self.__app.call(instance, "options")

        # Validate that options is a list
        if not isinstance(options, list):
            error_msg = (
                f"Command class {obj.__name__} 'options' must return a list."
            )
            raise CLIOrionisTypeError(error_msg)

        # Return None if there are no arguments
        if not options:
            return None

        # Validate all items are CLIArgument instances
        for idx, arg in enumerate(options):
            if not isinstance(arg, CLIArgument):
                error_msg = (
                    f"Command class {obj.__name__} 'options' must contain only "
                    f"CLIArgument instances, found '{type(arg).__name__}' at index "
                    f"{idx}."
                )
                raise CLIOrionisTypeError(error_msg)

        # Get the signature and description attributes from the command class
        rf_concrete = ReflectionConcrete(obj)
        signature = rf_concrete.getAttribute("signature", "<unknown>")
        description = rf_concrete.getAttribute("description", "")

        # Build the ArgumentParser for the command
        arg_parser = argparse.ArgumentParser(
            usage=f"python -B reactor {signature} [options]",
            description=f"Command [{signature}] : {description}",
            formatter_class=argparse.RawTextHelpFormatter,
            add_help=True,
            allow_abbrev=False,
            exit_on_error=True,
            prog=signature,
        )

        # Add each CLIArgument to the ArgumentParser
        for arg in options:
            arg.addToParser(arg_parser)

        # Return the constructed ArgumentParser
        return arg_parser

    def __parseArgs(
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
        Define a new command using the fluent interface.

        Create a command with the specified signature and handler. The handler must
        be a list containing the class and optionally the method name. Return an
        ICommand instance for further configuration.

        Parameters
        ----------
        signature : str
            Unique identifier for the command. Must follow naming conventions.
        handler : list of Any
            List containing the class and optionally the method name.

        Returns
        -------
        ICommand
            Instance for further configuration of the command.

        Raises
        ------
        CLIOrionisTypeError
            If the signature is not a string or the handler is not a valid list.
        CLIOrionisValueError
            If the signature does not meet naming conventions.
        """
        # Validate that handler is a list with at least one element
        if len(handler) < 1 or not isinstance(handler, list):
            error_msg = (
                "Handler must be a list with at least one element (the callable)."
            )
            raise CLIOrionisValueError(error_msg)

        # Ensure the first element is a class
        if not callable(handler[0]) or not hasattr(handler[0], "__name__"):
            error_msg = "The first element of handler must be a class."
            raise CLIOrionisTypeError(error_msg)

        # Create a new FluentCommand instance
        f_command = FluentCommand(
            signature=signature,
            concrete=handler[0],
            method=handler[1] if len(handler) > 1 else "handle",
        )

        # Add the new command to the internal list
        self.__fluent_commands.append(f_command)

        # Return the newly created command for further configuration
        return self.__fluent_commands[-1]

    def info(
        self
    ) -> list[dict]:
        """
        Return a list of registered commands with their metadata.

        Retrieves all commands loaded in the internal registry, skipping internal
        commands (those with double underscores). Each command is represented as a
        dictionary containing its signature and description.

        Returns
        -------
        list of dict
            List of dictionaries with 'signature' and 'description' for each command.
        """
        # Ensure commands are loaded before retrieving information
        self.__loadCommands()

        # Prepare a list to hold command information
        commands_info = []

        # Iterate through all registered commands in the internal registry
        for command in self.__commands.values():

            # Extract command metadata
            signature: str = command.signature
            description: str = command.description

            # Skip internal commands (those with double underscores)
            if signature.startswith("__") and signature.endswith("__"):
                continue

            # Append command information to the list
            commands_info.append({
                "signature": signature,
                "description": description,
            })

        # Return the sorted list of command information by signature
        return sorted(commands_info, key=lambda x: x["signature"])

    def call(
        self,
        signature: str,
        args: list[str] | None = None,
    ) -> object | None:
        """
        Execute a registered command synchronously by its signature.

        Retrieve a command from the registry using its signature, parse arguments,
        and execute the command's `handle` method. Manage execution timing, logging,
        and error handling. Return the output produced by the command or None.

        Parameters
        ----------
        signature : str
            Unique signature identifier of the command to execute.
        args : list of str or None, optional
            Command-line arguments to pass to the command.

        Returns
        -------
        object or None
            Output produced by the command's `handle` method, or None if no result.

        Raises
        ------
        CLIOrionisValueError
            If the command with the specified signature is not found.
        SystemExit
            If argument parsing fails due to invalid arguments.
        Exception
            Propagates any exception raised during command execution.
        """
        # Scope Request instances to this command execution context
        with self.__app.createScope():

            # Ensure commands are loaded before attempting to execute
            self.__loadCommands()

            # Retrieve the command from the registry by its signature
            command: Command = self.__commands.get(signature)
            if command is None:
                error_msg = f"Command '{signature}' not found."
                raise CLIOrionisValueError(error_msg)

            # Start execution timer for performance measurement
            self.__performance_counter.start()

            # Log the command execution start with RUNNING
            # state if timestamps are enabled
            if command.timestamps:
                self.__executer.running(program=signature)

            try:

                # Instantiate the command class using the application container
                command_instance: IBaseCommand = self.__app.build(command.obj)

                # Inject parsed arguments into the command instance
                dict_args = self.__parseArgs(command, args)

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
                self.__logger.error(error_msg) # noqa: TRY400

                # Calculate elapsed time and log failure with ERROR state if enabled
                self.__performance_counter.stop()
                elapsed_time = round(self.__performance_counter.getSeconds(), 2)
                if command.timestamps:
                    self.__executer.fail(program=signature, time=f"{elapsed_time}s")

                # Propagate the exception after logging
                raise
