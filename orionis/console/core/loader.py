from __future__ import annotations
import argparse
from dataclasses import asdict
import importlib
import re
from typing import TYPE_CHECKING, Any
from orionis.console.args.argument import CLIArgument
from orionis.console.args.types import TYPE_CONVERTERS
from orionis.console.base.command import BaseCommand
from orionis.console.contracts.base_command import IBaseCommand
from orionis.console.contracts.loader import ILoader
from orionis.console.entities.command import Command
from orionis.console.fluent.command import Command as FluentCommand
from orionis.services.cache.file_based_cache import FileBasedCache
from orionis.services.introspection.modules.engine import ModuleEngine
from orionis.services.introspection.modules.reflection import ReflectionModule

if TYPE_CHECKING:
    from pathlib import Path
    from orionis.console.contracts.command import ICommand
    from orionis.foundation.contracts.application import IApplication
    from orionis.services.cache.contracts.file_based_cache import IFileBasedCache

class Loader(ILoader):

    # ruff: noqa: PLC0415

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
            Initializes internal state and sets up command caching.
        """
        # Initialize internal lists and dictionaries for commands and metadata.
        self.__fluent_commands: list[ICommand] = []
        self.__commands: dict[str, Command] = {}
        self.__metadata: dict[str, Any] = {}
        self.__imported_modules: dict[str, Any] = {}
        self.__app: IApplication = app

        # Set up persistence for command caching.
        self.__use_cache: bool = False
        self.__persistence: IFileBasedCache | None = self.__getCachePersistence()

    def __getCachePersistence(self) -> IFileBasedCache | None:
        """
        Get the persistence mechanism for command caching.

        Returns
        -------
        FileBasedCache | None
            FileBasedCache instance for command caching, or None if no cache
            configuration is available.
        """
        # Extract cache configuration from application
        cache_config_app = self.__app.cacheConfiguration

        # Return None if no cache configuration is available
        if not cache_config_app:
            return None

        # Extract cache settings from configuration
        path = cache_config_app.get("folder")
        monitored_dirs = cache_config_app.get("monitored_dirs", [])
        monitored_files = cache_config_app.get("monitored_files", [])

        # Enable caching
        self.__use_cache = True

        # Create and return FileBasedCache instance
        return FileBasedCache(
            path=path,
            filename="commands",
            monitored_dirs=monitored_dirs,
            monitored_files=monitored_files,
        )

    def get(self, signature: str) -> Command | None:
        """
        Retrieve a command instance by its signature.

        Parameters
        ----------
        signature : str
            The unique signature identifying the command.

        Returns
        -------
        Command | None
            The Command instance if found, otherwise None.
        """
        # Load the command corresponding to the given signature
        self.__load(signature)
        return self.__commands.get(signature)

    def all(self) -> dict[str, Command]:
        """
        Return all loaded commands.

        Returns
        -------
        dict[str, Command]
            A dictionary mapping command signatures to Command instances.
        """
        # Load all commands into the internal dictionary if not already loaded
        self.__load()
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
        # Lazy import
        from orionis.console.core.commands import CORE_COMMANDS

        # Iterate and register each core command
        for obj in CORE_COMMANDS:
            sign = obj.signature
            self.__metadata[sign] = {
                "module_path": obj.__module__,
                "class": obj.__name__,
                "method": "handle",
                "signature": sign,
                "description": self.__getDescription(obj),
                "timestamps": self.__getTimestamps(obj),
                "options": self.__getOptions(obj),
            }

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
        # Scan the commands directory for Python modules
        modules = ModuleEngine.scan(
            app_root=self.__app.path("root"),
            tarjet_path=self.__app.path("console") / "commands",
        )

        # Iterate through all module names discovered in the commands directory
        for module_name in modules:

            # Reflect the module to access its classes
            rf_module = ReflectionModule(module_name)
            classes = rf_module.getClasses()

            # Iterate through all classes found in the current module
            for obj in classes.values():

                # Check if the class is a valid command class
                if issubclass(obj, BaseCommand) and obj is not BaseCommand \
                        and obj is not IBaseCommand:
                    sign = self.__getSignature(obj)
                    self.__metadata[sign] = {
                        "module_path": obj.__module__,
                        "class": obj.__name__,
                        "method": "handle",
                        "signature": sign,
                        "description": self.__getDescription(obj),
                        "timestamps": self.__getTimestamps(obj),
                        "options": self.__getOptions(obj),
                    }

    def __importFluentCommandRoutes(self) -> None:
        """
        Import fluent command route modules from application routing paths.

        Load and import all route modules defined in the application's console
        routing configuration. Convert file paths to module names and import
        them to register fluent commands.

        Returns
        -------
        None
            Imports route modules without returning a value.
        """
        # Retrieve the routes file paths from application configuration
        routes_path: list[Path] | Path = self.__app.routingPaths("console")
        routes_path = routes_path if isinstance(routes_path, list) else [routes_path]

        # Get the application root directory
        app_root: Path = self.__app.path("root")

        # Iterate through each route file path
        for route_file in routes_path:
            # Convert file path to relative path from application root
            relative_path = route_file.relative_to(app_root)

            # Convert relative path to module name format
            full_module_name = ".".join(relative_path.with_suffix("").parts)

            # Import the module to register fluent commands
            importlib.import_module(full_module_name)

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
        self.__importFluentCommandRoutes()

        # Iterate through all fluent command definitions
        for f_command in self.__fluent_commands:

            # Check if the fluent command provides a 'get' method
            if hasattr(f_command, "get") and callable(f_command.get):

                # Retrieve signature and command entity
                signature, command = f_command.get()

                # Register command metadata
                self.__metadata[signature] = {
                    "module_path": command.obj.__module__,
                    "class": command.obj.__name__,
                    "method": command.method,
                    "signature": signature,
                    "description": command.description,
                    "timestamps": command.timestamps,
                    "options": (
                        self.__serializeOptions(command.args)
                        if command.args else None
                    ),
                }

    def __getSignature(self, obj: IBaseCommand) -> str:
        """
        Validate and return the 'signature' attribute of a command class.

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
        # Ensure the command class has a 'signature' attribute
        if not hasattr(obj, "signature"):
            error_msg = (
                f"Command class {obj.__name__} must have a 'signature' attribute."
            )
            raise ValueError(error_msg)

        # Ensure the signature attribute is a string
        if not isinstance(obj.signature, str):
            error_msg = (
                f"Command class {obj.__name__} 'signature' must be a string."
            )
            raise TypeError(error_msg)

        # Ensure the signature is not empty after stripping whitespace
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

    def __getTimestamps(
        self,
        obj: IBaseCommand,
    ) -> bool:
        """
        Retrieve the 'timestamps' attribute from a command class.

        Parameters
        ----------
        obj : IBaseCommand
            Command class instance to inspect.

        Returns
        -------
        bool
            True if the 'timestamps' attribute exists and is a boolean, otherwise
            False.

        Raises
        ------
        TypeError
            If the 'timestamps' attribute exists but is not a boolean.
        """
        # Check if the command class has a 'timestamps' attribute
        if not hasattr(obj, "timestamps"):
            return False

        # Ensure the 'timestamps' attribute is a boolean
        if not isinstance(obj.timestamps, bool):
            error_msg = (
                f"Command class {obj.__name__} 'timestamps' must be a boolean."
            )
            raise TypeError(error_msg)

        # Return the value of the 'timestamps' attribute
        return obj.timestamps

    def __getDescription(
        self,
        obj: IBaseCommand,
    ) -> str:
        """
        Retrieve and validate the 'description' attribute of a command class.

        Ensure the command class has a non-empty string 'description' attribute.
        If missing, set a default description. Raise an error if the attribute
        is not a string or is empty.

        Parameters
        ----------
        obj : IBaseCommand
            Command class instance to validate.

        Returns
        -------
        str
            The validated and stripped description string.

        Raises
        ------
        ValueError
            If the 'description' attribute is empty.
        TypeError
            If the 'description' attribute is not a string.
        """
        # Set a default description if not present
        if not hasattr(obj, "description"):
            obj.description = "No description provided."

        # Ensure the description is a string
        if not isinstance(obj.description, str):
            error_msg = (
                f"Command class {obj.__name__} 'description' must be a string."
            )
            raise TypeError(error_msg)

        # Ensure the description is not empty
        if obj.description.strip() == "":
            error_msg = (
                f"Command class {obj.__name__} 'description' cannot be an empty string."
            )
            raise ValueError(error_msg)

        # Return the validated description
        return obj.description.strip()

    def __getOptions(
        self,
        obj: IBaseCommand,
    ) -> list[dict]:
        """
        Retrieve and validate CLIArgument options for a command class.

        Parameters
        ----------
        obj : IBaseCommand
            The command class instance to validate.

        Returns
        -------
        list of dict
            A list of CLIArgument instances as dictionaries. Returns an empty list
            if no options are present.

        Raises
        ------
        TypeError
            If the 'options' method does not return a list or contains non-
            CLIArgument instances.
        """
        # Instantiate the command and retrieve its options
        instance = self.__app.build(obj)

        # Call the 'options' method to get argument definitions
        options: list[CLIArgument] = self.__app.call(instance, "options")

        # Ensure options is a list
        if not isinstance(options, list):
            error_msg = (
                f"Command class {obj.__name__} 'options' must return a list."
            )
            raise TypeError(error_msg)

        # Return an empty list if there are no arguments
        if not options:
            return []

        # Validate all items are CLIArgument instances
        for idx, arg in enumerate(options):
            if not isinstance(arg, CLIArgument):
                error_msg = (
                    f"Command class {obj.__name__} 'options' must contain only "
                    f"CLIArgument instances, found '{type(arg).__name__}' at index "
                    f"{idx}."
                )
                raise TypeError(error_msg)

        # Return serialized options as list of dictionaries
        return self.__serializeOptions(options)

    def __serializeOptions(
        self, cli_arguments: list[CLIArgument],
    ) -> list[dict]:
        """
        Serialize CLIArgument options to dictionaries.

        Parameters
        ----------
        cli_arguments : list[CLIArgument]
            List of CLIArgument instances to serialize.

        Returns
        -------
        list of dict
            List of dictionaries representing the CLIArgument instances.
        """
        # Initialize list to hold serialized options
        serialized_options = []

        # Iterate through each CLIArgument and convert to dictionary
        for cli_arg in cli_arguments:

            # Convert CLIArgument to dictionary
            arg_dict = asdict(cli_arg)

            # Convert type to its name if it is a type object
            if "type" in arg_dict and isinstance(arg_dict["type"], type):
                arg_dict["type"] = (
                    f"{arg_dict['type'].__module__}.{arg_dict['type'].__name__}"
                )

                # If name is set, clear flags to avoid redundancy
                if arg_dict["name"] is not None:
                    arg_dict["flags"] = None

            # Append the serialized argument dictionary to the list
            serialized_options.append(arg_dict)

        # Return the list of serialized options
        return serialized_options

    def __buildArgumentParser(
        self,
        options: list[dict],
        signature: str,
        description: str,
    ) -> argparse.ArgumentParser | None:
        """
        Construct and configure an ArgumentParser for a command class.

        Build an ArgumentParser using the provided CLIArgument options. Returns
        the parser if arguments exist, otherwise returns None.

        Parameters
        ----------
        options : list[dict]
            List of CLIArgument option dictionaries.
        signature : str
            Command signature.
        description : str
            Command description.

        Returns
        -------
        argparse.ArgumentParser | None
            ArgumentParser instance configured with the command's arguments, or None
            if no arguments are present.
        """
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
            type_callable = TYPE_CONVERTERS.get(arg["type"]) if arg["type"] else bool
            arg["type"] = type_callable
            CLIArgument(**arg).addToParser(arg_parser)

        # Return the constructed ArgumentParser
        return arg_parser

    def __buildCommand(self, meta: dict) -> Command:
        """
        Build a Command instance from metadata.

        Parameters
        ----------
        meta : dict
            Metadata dictionary containing command information.

        Returns
        -------
        Command
            The constructed Command instance.
        """
        # Import the module and retrieve the command class, caching imports
        module_path: str = meta["module_path"]
        if module_path in self.__imported_modules:
            module = self.__imported_modules[module_path]
        else:
            module = importlib.import_module(module_path)
            self.__imported_modules[module_path] = module
        cls = getattr(module, meta["class"])

        # Build and return the Command instance using metadata
        return Command(
            obj=cls,
            method=meta["method"],
            signature=meta["signature"],
            description=meta["description"],
            timestamps=meta["timestamps"],
            args=self.__buildArgumentParser(
                meta["options"],
                meta["signature"],
                meta["description"],
            ),
        )

    def __loadMetadata(self) -> None:
        """
        Load command metadata from cache or discover commands.

        Loads metadata from cache if available and caching is enabled. If no cached
        metadata exists, discovers all command types and optionally saves to cache.

        Returns
        -------
        None
            Populates the internal metadata dictionary.
        """
        # Skip if metadata already loaded
        if self.__metadata:
            return

        # Load from cache if enabled
        if self.__use_cache and self.__persistence:
            self.__metadata = self.__persistence.get() or {}

        # Discover commands if no metadata available
        if not self.__metadata:
            self.__loadCoreCommands()
            self.__loadCustomCommands()
            self.__loadFluentCommands()

            # Save to cache if enabled
            if self.__use_cache and self.__persistence:
                self.__persistence.save(self.__metadata)

    def __load(self, signature: str | None = None) -> None:
        """
        Load command classes from metadata and populate the commands dictionary.

        Parameters
        ----------
        signature : str | None
            The unique signature of the command to load, or None to load all.

        Returns
        -------
        None
            This method populates the internal commands dictionary and does not
            return a value.
        """
        # Load metadata if not already loaded
        self.__loadMetadata()

        # Load specific command or all commands based on the signature parameter
        if signature:
            meta = self.__metadata.get(signature)
            if not meta:
                return
            if meta["signature"] not in self.__commands:
                self.__commands[meta["signature"]] = self.__buildCommand(meta)
        else:
            # Load all commands from metadata
            for meta in self.__metadata.values():
                sig = meta["signature"]
                if sig not in self.__commands:
                    self.__commands[sig] = self.__buildCommand(meta)
