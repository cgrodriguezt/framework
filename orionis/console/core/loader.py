from __future__ import annotations
import argparse
import importlib
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any
from orionis.console.args.argument import CLIArgument
from orionis.console.base.command import BaseCommand
from orionis.console.contracts.base_command import IBaseCommand
from orionis.console.contracts.loader import ILoader
from orionis.console.entities.command import Command
from orionis.console.entities.command import Command as CommandEntity
from orionis.console.fluent.command import Command as FluentCommand
from orionis.services.encrypter.persistence import Persistence
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.services.introspection.modules.reflection import ReflectionModule

if TYPE_CHECKING:
    from orionis.console.contracts.command import ICommand
    from orionis.foundation.contracts.application import IApplication

class Loader(ILoader):

    def __init__(self, app: IApplication) -> None:
        """
        Initialize the Loader instance.

        Parameters
        ----------
        app : IApplication
            The application instance providing configuration and paths.

        Returns
        -------
        None
            This method initializes internal state and does not return a value.
        """
        # Initialize the list for fluent commands and the command cache.
        self.__fluent_commands: list[ICommand] = []
        self.__commands: dict[str, Command] | None = None
        self.__app = app

        # Set up persistence for command caching.
        self.__persistence = Persistence(
            path=self.__app.path("storage") / "framework" / "cache" / "console",
            filename="commands",
            cipher=self.__app.config("app.cipher"),
            key=self.__app.config("app.key"),
            magic=b"REACTOR",
            salt=b"reactor.cache",
            info=b"cmd",
        )

    def get(self, signature: str) -> Command | None:
        """
        Retrieve a command by its signature.

        Parameters
        ----------
        signature : str
            The unique signature of the command.

        Returns
        -------
        Command | None
            The Command instance if found, otherwise None.
        """
        return self.all().get(signature)

    def all(self) -> dict[str, Command]:
        """
        Return all loaded commands, loading and caching if necessary.

        Returns
        -------
        dict[str, Command]
            Dictionary mapping command signatures to Command instances.
        """
        # Fast path: return cached commands if already loaded
        if self.__commands:
            return self.__commands

        # Attempt to load commands from cache
        self.__commands = self.__persistence.get() or {}

        # If cache is empty, load core, custom, and fluent commands
        if not self.__commands:
            self.__loadCoreCommands()
            self.__loadCustomCommands()
            self.__loadFluentCommands()

            # Save loaded commands to cache
            self.__persistence.data(self.__commands).save()

        # Return the loaded commands
        return self.__commands

    def addFluentCommand(
        self,
        signature: str,
        handler: list[type[Any], str | None],
    ) -> ICommand:
        """
        Define a new command using the fluent interface.

        Create a command with the given signature and handler. The handler must be
        a list containing the class and optionally the method name. Validate input
        types and conventions. Return the created ICommand instance.

        Parameters
        ----------
        signature : str
            Unique identifier for the command.
        handler : list of Any
            List containing the class and optionally the method name.

        Returns
        -------
        ICommand
            The created FluentCommand instance.

        Raises
        ------
        TypeError
            If the signature is not a string or the handler is not a valid list.
        ValueError
            If the signature does not meet naming conventions.
        """
        # Validate that handler is a list with at least one element
        if len(handler) < 1 or not isinstance(handler, list):

            # Handler must be a list with at least one element (the callable)
            error_msg = (
                "Handler must be a list with at least one element (the callable)."
            )
            raise ValueError(error_msg)

        # Ensure the first element is a class
        if not callable(handler[0]) or not hasattr(handler[0], "__name__"):

            # The first element of handler must be a class
            error_msg = "The first element of handler must be a class."
            raise TypeError(error_msg)

        # Create a new FluentCommand instance
        f_command = FluentCommand(
            signature=signature,
            concrete=handler[0],
            method=handler[1] if len(handler) > 1 else "__call__",
        )

        # Add the new command to the internal list
        self.__fluent_commands.append(f_command)

        # Return the newly created command for further configuration
        return self.__fluent_commands[-1]

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
        # Lazy import to avoid circular dependencies
        # ruff: noqa: PLC0415
        from orionis.console.commands.cache.clear_command import CacheClearCommand
        from orionis.console.commands.experimental.__publisher__ import PublisherCommand
        from orionis.console.commands.experimental.server import ServerCommand
        from orionis.console.commands.help.help_command import HelpCommand
        from orionis.console.commands.help.version_command import VersionCommand
        from orionis.console.commands.make.command import MakeCommand
        from orionis.console.commands.make.scheduler_event_listener_command import (
            MakeSchedulerListenerCommand,
        )
        from orionis.console.commands.schedule.list_command import ScheduleListCommand
        from orionis.console.commands.schedule.work_command import ScheduleWorkCommand
        from orionis.console.commands.test.test_command import TestCommand

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
            args = self.__ensureArguments(obj, signature, description)

            # Register the command in the internal registry
            self.__commands[signature] = Command(
                obj=obj,
                method="handle",
                timestamps=timestamp,
                signature=signature,
                description=description,
                args=args,
            )

    def __discoverCommandModuleNames(self) -> list[str]:
        """
        Discover Python module names for command classes in the commands directory.

        Walk through the commands directory, sanitize module paths, and collect
        Python module names for further processing. Does not import or register
        classes, only builds a list of module names.

        Returns
        -------
        list[str]
            List of sanitized Python module names found in the commands directory.
        """
        # Ensure the provided commands_path is a valid directory
        commands_path = (Path(self.__app.path("console")) / "commands").resolve()
        root_path = str(self.__app.path("root"))

        # Initialize list to hold module names
        modules = []

        # Iterate through the command path and load command modules
        for current_directory, _, files in os.walk(commands_path):

            # Iterate through each file in the current directory
            for file in files:

                # Only process Python files
                if file.endswith(".py"):

                    # Sanitize the module path by converting filesystem
                    # path to Python module notation
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

                    # Append the full module name to the modules list
                    modules.append(f"{pre_module}.{file[:-3]}")

        # Return the list of discovered module names
        return modules

    def __loadCustomCommands(self) -> None:
        """
        Load custom command classes from the commands directory.

        Walk through the commands directory, import Python modules, and register
        command classes that inherit from BaseCommand. Sanitize module paths and
        validate command structure before registration.

        Returns
        -------
        None
            Registers command classes internally in the reactor's command registry.
        """
        # Iterate through all module names discovered in the commands directory
        for module_name in self.__discoverCommandModuleNames():

            # Reflect the module to access its classes
            rf_module = ReflectionModule(module_name)
            classes = rf_module.getClasses()

            # Iterate through all classes found in the current module
            for obj in classes.values():

                # Check if the class is a valid command class
                if issubclass(obj, BaseCommand) and obj is not BaseCommand \
                        and obj is not IBaseCommand:

                    # Validate the command class structure and register it
                    timestamp = self.__ensureTimestamps(obj)
                    signature = self.__ensureSignature(obj)
                    description = self.__ensureDescription(obj)
                    args = self.__ensureArguments(obj, signature, description)

                    # Add the command to the internal registry
                    self.__commands[signature] = Command(
                        obj=obj,
                        method="handle",
                        timestamps=timestamp,
                        signature=signature,
                        description=description,
                        args=args,
                    )

    def __discoverFluentCommands(self) -> None:
        """
        Discover and import Python modules that define fluent commands.

        Walk the routes directory and import Python modules that use
        Reactor.command. Raise RuntimeError if file reading or import fails.

        Returns
        -------
        None
            Returns None after attempting to import all relevant modules.
        """
        # Get the routes directory path from the application instance
        routes_path = self.__app.path("routes")

        # Check if routes directory exists
        if not routes_path.exists():
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
                    file_path = Path(current_directory) / file

                    # Read file content to check for Reactor.command usage
                    try:

                        # Attempt to import the module if it defines fluent commands
                        self.__importFluentCommandModule(
                            file_path,
                            file,
                            current_directory,
                            root_path,
                        )

                    except Exception as e:

                        # Raise a runtime error if file reading fails
                        error_msg = (
                            f"Failed to read file '{file_path}' "
                            f"for fluent command loading: {e}"
                        )
                        raise RuntimeError(error_msg) from e

    def __importFluentCommandModule(
        self,
        file_path: str,
        file: str,
        current_directory: str,
        root_path: str,
    ) -> None:
        """
        Import a Python module that defines fluent commands if detected.

        Open the specified file, check for fluent command definitions, and import
        the corresponding module if found. This registers any fluent commands
        defined in the file.

        Parameters
        ----------
        file_path : str
            Path to the Python file to read.
        file : str
            Name of the Python file.
        current_directory : str
            Directory containing the file.
        root_path : str
            Project root directory for module path resolution.

        Returns
        -------
        None
            Returns None after attempting to import the module if a fluent
            command is found.
        """
        # Open and read the file content
        with Path.open(file_path, encoding="utf-8") as f:
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
                return

            # Import the module to register fluent commands
            importlib.import_module(f"{pre_module}.{file[:-3]}")

    def __loadFluentCommands(self) -> None:
        """
        Register commands defined via the fluent interface.

        Discover and register all commands created using the fluent API. Validate
        their structure and metadata before adding them to the internal registry.

        Returns
        -------
        None
            Registers fluent commands internally for later lookup and execution.
        """
        # Discover fluent commands defined in the routes directory
        self.__discoverFluentCommands()

        # Iterate through all fluent command definitions
        for f_command in self.__fluent_commands:

            # Check if the fluent command provides a 'get' method
            if hasattr(f_command, "get") and callable(f_command.get):

                # Retrieve signature and command entity
                values = f_command.get()
                signature: str = values[0]
                command_entity: CommandEntity = values[1]

                # Extract required CLI arguments
                required_args: list[CLIArgument] = command_entity.args

                # Create an ArgumentParser for the command
                arg_parser = argparse.ArgumentParser(
                    usage=f"python -B reactor {signature} [options]",
                    description=f"Command [{signature}] : "
                                f"{command_entity.description}",
                    formatter_class=argparse.RawTextHelpFormatter,
                    add_help=True,
                    allow_abbrev=False,
                    exit_on_error=True,
                    prog=signature,
                )

                # Add each CLIArgument to the parser
                for arg in required_args:
                    arg.addToParser(arg_parser)

                # Register the command in the internal registry
                self.__commands[signature] = Command(
                    obj=command_entity.obj,
                    method=command_entity.method,
                    timestamps=command_entity.timestamps,
                    signature=signature,
                    description=command_entity.description,
                    args=arg_parser,
                )

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
        ValueError
            If the class lacks a 'signature' attribute, if the signature is empty,
            or if the signature does not match the required pattern.
        TypeError
            If the 'signature' attribute is not a string.
        """
        # Check if the command class has a signature attribute
        if not hasattr(obj, "signature"):
            error_msg = (
                f"Command class {obj.__name__} must have a 'signature' attribute."
            )
            raise ValueError(error_msg)

        # Ensure the signature attribute is a string type
        if not isinstance(obj.signature, str):
            error_msg = (
                f"Command class {obj.__name__} 'signature' must be a string."
            )
            raise TypeError(error_msg)

        # Validate that the signature is not empty after stripping whitespace
        if obj.signature.strip() == "":
            error_msg = (
                f"Command class {obj.__name__} 'signature' cannot be an empty string."
            )
            raise ValueError(error_msg)

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
            raise ValueError(error_msg)

        # Return the validated signature
        return obj.signature.strip()

    def __ensureTimestamps(
        self,
        obj: IBaseCommand,
    ) -> bool:
        """
        Validate that the 'timestamps' attribute exists and is a boolean.

        Checks if the command class has a 'timestamps' attribute. If present,
        verifies it is of type bool.

        Parameters
        ----------
        obj : IBaseCommand
            Command class instance to validate.

        Returns
        -------
        bool
            True if 'timestamps' exists and is boolean, otherwise False.

        Raises
        ------
        TypeError
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
            raise TypeError(error_msg)

        # Return timestamps value
        return obj.timestamps

    def __ensureDescription(
        self,
        obj: IBaseCommand,
    ) -> str:
        """
        Validate that the command class has a non-empty string description.

        Checks if the command class has a 'description' attribute and ensures it is
        a non-empty string. Raises ValueError or TypeError if validation fails.

        Parameters
        ----------
        obj : IBaseCommand
            Command class instance to validate.

        Returns
        -------
        str
            Stripped description string if valid.

        Raises
        ------
        ValueError
            If the 'description' attribute is missing or empty.
        TypeError
            If the 'description' attribute is not a string.
        """
        # Check if the command class has a description attribute
        if not hasattr(obj, "description"):
            error_msg = (
                f"Command class {obj.__name__} must have a 'description' attribute."
            )
            raise ValueError(error_msg)

        # Ensure the description attribute is a string type
        if not isinstance(obj.description, str):
            error_msg = (
                f"Command class {obj.__name__} 'description' must be a string."
            )
            raise TypeError(error_msg)

        # Validate that the description is not empty after stripping whitespace
        if obj.description.strip() == "":
            error_msg = (
                f"Command class {obj.__name__} 'description' cannot be an empty string."
            )
            raise ValueError(error_msg)

        # Return the stripped description string
        return obj.description.strip()

    def __ensureArguments(
        self,
        obj: IBaseCommand,
        signature: str,
        description: str,
    ) -> argparse.ArgumentParser | None:
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
        TypeError
            If the 'options' method does not return a list or contains non-CLIArgument
            instances.
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
            raise TypeError(error_msg)

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
                raise TypeError(error_msg)

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
