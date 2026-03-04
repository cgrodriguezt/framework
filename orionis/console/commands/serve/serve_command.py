import asyncio
import os
import signal
import sys
from contextlib import suppress
from granian.constants import Interfaces, Loops
from pathlib import Path
from threading import RLock
from typing import Self, TYPE_CHECKING
from orionis.console.args.argument import CLIArgument
from orionis.console.base.command import BaseCommand
from orionis.foundation.contracts.application import IApplication
from orionis.foundation.enums.runtimes import Runtime
from orionis.metadata.framework import PYTHON_REQUIRES, VERSION

if TYPE_CHECKING:
    from collections.abc import Callable

class ServerCommand(BaseCommand):

    # ruff: noqa: S606, S104, TC001 (DI)

    _instance = None
    _instance_lock = RLock()

    # Disable timestamps in command output
    timestamps = False

    # Command signature and description
    signature = "serve"

    # Command
    description = "Initializes the Orionis server with Granian."

    def __new__(cls) -> Self:
        """
        Create or return the singleton instance of ServerCommand.

        Ensures only one instance of ServerCommand exists using a thread-safe
        singleton pattern.

        Parameters
        ----------
        cls : type
            The class being instantiated.

        Returns
        -------
        ServerCommand
            The singleton instance of ServerCommand.
        """
        # Ensure thread-safe singleton instantiation
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initialize the ServerCommand instance.

        Initializes thread safety mechanisms, environment variables, and command
        configuration for the server. Ensures singleton initialization.

        Returns
        -------
        None
            This method does not return a value. The instance is initialized.
        """
        # Only initialize once per instance
        if not hasattr(self, "_initialized"):
            # Lock for thread-safe operations
            self.__lock = RLock()
            # Flag indicating if server is shutting down
            self.__shutting_down = False
            # Controlled copy of environment variables
            self.__env = self.__initNewEnvironment()
            # Command list for launching server via CLI
            self.__cmd: list[str] = [
                sys.executable,
            ]
            # Indicates if server should reload on code changes
            self.__app_reload: bool = False
            # Placeholder for showdown callable
            self.__call_in_showdown: Callable | None = None
            # Mark instance as initialized
            self._initialized = True

    def __initNewEnvironment(
        self,
    ) -> dict[str, str]:
        """
        Initialize and return a new environment dictionary.

        Copies the current environment, sets UTF-8 encoding variables, and updates
        with values from the application's environment service.

        Returns
        -------
        dict[str, str]
            A dictionary containing the updated environment variables.
        """
        # Copy the current environment and set UTF-8 encoding variables
        env: dict[str, str] = os.environ.copy()

        # Ensure Python uses UTF-8 encoding
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        env["ORIONIS_FRAMEWORK_VERSION"] = VERSION
        env["ORIONIS_PYTHON_VERSION_REQUIRED"] = PYTHON_REQUIRES

        # Return the configured environment dictionary
        return env

    def __configureBytecodeWriting(
        self,
        app: IApplication,
    ) -> None:
        """
        Configure Python bytecode writing based on the environment.

        Parameters
        ----------
        app : IApplication
            The application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        is_production: bool = app.isProduction()

        # Set environment variable to control bytecode file writing
        self.__env["PYTHONDONTWRITEBYTECODE"] = "0" if is_production else "1"

        # Add debug flag for non-production environments
        if not is_production:
            self.__cmd.append("-B")

    def __appendHostAndPortToCommand(
        self,
        app: IApplication,
    ) -> None:
        """
        Append the host and port configuration to the server command.

        Parameters
        ----------
        app : IApplication
            The application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Determine if the application is in production mode
        is_production: bool = app.isProduction()

        # Select host based on environment
        host: str = app.config("app.host") or (
            "0.0.0.0" if is_production else "127.0.0.1"
        )

        # Check for port argument from command line and use it if provided
        cmd_port = self.argument("port")
        if cmd_port is not None:
            port = cmd_port
        else:
            port: int = app.config("app.port") or 8000

        # Append host and port to the command
        self.__cmd.extend([
            "-m",
            "granian",
            "--host", str(host),
            "--port", str(port),
        ])

        # Update environment variables for host and port
        self.__env["GRANIAN_HOST"] = str(host)
        self.__env["GRANIAN_PORT"] = str(port)

    def __appendStaticMountAndRouteToCommand(
        self,
        app: IApplication,
    ) -> None:
        """
        Append the static mount path and URL route to the server command.

        Parameters
        ----------
        app : IApplication
            The application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Retrieve public disk configuration from the application's filesystem config
        filesystems_config: dict = app.config("filesystems")
        public_disk: dict = filesystems_config.get("disks", {}).get("public", {})

        # Resolve the static mount path, making it absolute if necessary
        static_mount: Path = Path(public_disk.get("path", "storage/app/public"))
        if not static_mount.is_absolute():
            static_mount = Path(app.path("root")) / static_mount
        static_mount = static_mount.resolve()

        # Prepare the static URL, removing any leading slash
        static_url: str = public_disk.get("url", "/static").lstrip("/")

        # Add static path mount and route to the command
        self.__cmd.extend([
            "--static-path-mount", str(static_mount),
            "--static-path-route", static_url,
        ])

        # Update environment variables for static paths
        self.__env["GRANIAN_STATIC_PATH_MOUNT"] = str(static_mount)
        self.__env["GRANIAN_STATIC_PATH_ROUTE"] = static_url

    def __appendInterfaceToCommand(
        self,
        app: IApplication,
    ) -> None:
        """
        Append the interface type (ASGI or RSGI) to the server command.

        Parameters
        ----------
        app : IApplication
            The application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        cmd_interface = self.argument("interface")
        if cmd_interface is not None:
            self.__cmd.extend(["--interface", cmd_interface])
            self.__env["GRANIAN_INTERFACE"] = cmd_interface
            return

        # Check if the application supports WebSockets
        has_websockets: bool = app.hasWebSockets()

        # Determine the interface type based on WebSocket support
        interface_type = (
            Interfaces.ASGI.value if has_websockets else Interfaces.RSGI.value
        )

        # Append the appropriate interface flag to the command
        self.__cmd.extend(["--interface", interface_type])

        # Update environment variable for interface type
        self.__env["GRANIAN_INTERFACE"] = interface_type

    def __appendWorkersToCommand(
        self,
        app: IApplication,
    ) -> None:
        """
        Append the number of worker processes to the server command.

        Parameters
        ----------
        app : IApplication
            The application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Determine the number of worker processes
        workers: int = max(1, app.config("app.workers") or (os.cpu_count() or 1))

        # Append the workers option to the command
        self.__cmd.extend([
            "--workers", str(workers),
        ])

        # Update environment variable for number of workers
        self.__env["GRANIAN_WORKERS"] = str(workers)

    def __appendLoopToCommand(
        self,
    ) -> None:
        """
        Append the event loop configuration to the server command.

        Parameters
        ----------
        app : IApplication
            The application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Determine the appropriate event loop based on the operating system
        windows_loop = Loops.auto.value
        unix_loop = Loops.uvloop.value
        event_loop= unix_loop if os.name != "nt" else windows_loop

        # Append the loop option to the command
        self.__cmd.extend([
            "--loop", event_loop,
        ])

        # Update environment variable for event loop
        self.__env["GRANIAN_LOOP"] = event_loop

    def __appendWebsocketSupportToCommand(
        self,
        app: IApplication,
    ) -> None:
        """
        Append WebSocket support flag to the server command.

        Parameters
        ----------
        app : IApplication
            The application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Check if the application supports WebSockets
        has_websockets: bool = app.hasWebSockets()

        # Append the appropriate WebSocket support flag to the command
        self.__cmd.append("--ws" if has_websockets else "--no-ws")

        # Update environment variable for WebSocket support
        self.__env["GRANIAN_WEBSOCKETS"] = "1" if has_websockets else "0"

    def __appendLoggingConfigurationToCommand(
        self,
        app: IApplication,
    ) -> None:
        """
        Append logging configuration to the server command.

        Parameters
        ----------
        app : IApplication
            The application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        cmd_log_enabled = self.argument("log_enabled")
        if cmd_log_enabled:
            self.__cmd.extend([
                "--log-level", "info",
            ])
            self.__env["GRANIAN_LOG_ENABLED"] = "1"
            self.__env["GRANIAN_LOG_LEVEL"] = "info"
            return

        # Determine if the application is in production mode
        is_production: bool = app.isProduction()

        # Append logging options based on the environment
        if is_production:

            # Production logging options
            self.__cmd.extend([
                "--log-level", "error",
            ])

            # Set environment variables for production logging
            self.__env["GRANIAN_LOG_ENABLED"] = "1"
            self.__env["GRANIAN_LOG_LEVEL"] = "error"

        else:

            # Development logging options
            self.__cmd.append("--no-log")

            # Set environment variables for development logging
            self.__env["GRANIAN_LOG_ENABLED"] = "0"

    def __appendReloadOptionsToCommand(
        self,
        app: IApplication,
    ) -> None:
        """
        Append reload options to the server command if enabled.

        Parameters
        ----------
        app : IApplication
            The application instance.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Adds reload flags and monitored directories to the command if reload is
        enabled and not in production.
        """
        # Determine reload option from configuration
        self.__app_reload: bool | None = app.config("app.reload")

        # Only enable reload in non-production environments
        if self.__app_reload and not app.isProduction():
            watch_dirs: dict | None = app.cacheConfiguration

            # Add reload paths if monitored directories exist
            if watch_dirs and "monitored_dirs" in watch_dirs:

                # Collect valid monitored directories for reload
                reload_paths: list[Path] = [
                    p.resolve() for p in watch_dirs["monitored_dirs"]
                    if isinstance(p, Path) and p.exists()
                ]

                # Append reload options to the command if paths are available
                if reload_paths:
                    self.__cmd.append("--reload")
                    self.__env["GRANIAN_RELOAD"] = "1"
                    reload_paths_to_str: str = ",".join(
                        [str(path) for path in reload_paths],
                    )
                    self.__env["GRANIAN_RELOAD_PATHS"] = reload_paths_to_str

                    # Add each reload path to the command
                    for path in reload_paths:
                        self.__cmd.extend(["--reload-paths", str(path)])
        else:

            # Disable reload options
            self.__app_reload = False
            self.__env["GRANIAN_RELOAD"] = "0"

    def __appendProcessNameToCommand(
        self,
        name: str,
    ) -> None:
        """
        Append the process name to the server command.

        Parameters
        ----------
        name : str
            The name to assign to the process.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Add process name to command and environment for identification
        self.__cmd.extend([
            "--process-name", name,
        ])

        # Update environment variable for process name
        self.__env["GRANIAN_PROCESS_NAME"] = name

    def __unixServe(self) -> None:
        """
        Serve the application on Unix-like systems.

        Flushes standard output and error streams, then replaces the current
        process with the Granian server using execvpe.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Flush output streams before replacing the process
        sys.stdout.flush()
        sys.stderr.flush()

        # Replace the current process with the Granian server
        os.execvpe(self.__cmd[0], self.__cmd, self.__env)

    async def __windowsServe(self) -> None:
        """
        Serve the application on Windows systems asynchronously.

        Launches the server process using asyncio, sets up signal handling for
        graceful shutdown, and ensures proper process termination.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Start the server process asynchronously
        process = await asyncio.create_subprocess_exec(
            *self.__cmd,
            env=self.__env,
        )

        # Get the current event loop
        loop = asyncio.get_running_loop()

        # Event to signal shutdown
        shutdown_event = asyncio.Event()

        def handle_interrupt() -> None:
            """
            Handle interrupt signal for graceful shutdown.

            Returns
            -------
            None
                This method does not return a value.
            """
            # Only handle shutdown if reload is enabled and not already shutting down
            if not self.__app_reload:
                return
            if not self.__shutting_down:
                self.__shutting_down = True
                shutdown_event.set()

        try:
            # Try to add a signal handler for SIGINT
            loop.add_signal_handler(signal.SIGINT, handle_interrupt)
        except NotImplementedError:
            # Fallback for Windows where add_signal_handler may not be implemented
            signal.signal(signal.SIGINT, lambda _s, _f: handle_interrupt())

        try:
            # Wait until shutdown is triggered
            await shutdown_event.wait()

            # Call shutdown handler if defined
            if self.__call_in_showdown:
                await self.__call_in_showdown(
                    runtime=Runtime.HTTP,
                )

            # Terminate the server process
            process.terminate()

            try:
                # Wait for process to exit, with timeout
                await asyncio.wait_for(process.wait(), timeout=5)
            except TimeoutError:
                # Force kill if process does not exit in time
                process.kill()
                await process.wait()

        finally:
            # Remove the signal handler if possible
            with suppress(NotImplementedError, ValueError, OSError):
                loop.remove_signal_handler(signal.SIGINT)

    def __setShutdownHandler(
        self,
        app: IApplication,
    ) -> None:
        """
        Set the application's shutdown handler for graceful termination.

        Parameters
        ----------
        app : IApplication
            The application instance.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Assigns the shutdown handler if the application defines it.
        """
        # Assign the shutdown handler if present in the application
        method_name: str = "_Application__onShutdown"
        if hasattr(app, method_name):
            self.__call_in_showdown = getattr(app, method_name)

    def argumentDefinitions(self) -> list[CLIArgument]:
        """
        Define command-line arguments and options for the command.

        Returns
        -------
        list of CLIArgument
            List of argument and option definitions for the command.
        """
        # Return CLI arguments for interface type, port, and logging
        return [
            CLIArgument(
                flags=["--interface", "-i"],
                type=str,
                help="Interface type to use (ASGI or RSGI).",
                choices=["rsgi", "asgi"],
                dest="interface",
                default=None,
                required=False,
            ),
            CLIArgument(
                flags=["--port", "-p"],
                type=int,
                help="Port number to bind the server to.",
                dest="port",
                default=None,
                required=False,
            ),
            CLIArgument(
                flags=["--log"],
                type=bool,
                help="Enable logging in production mode.",
                action="store_true",
                dest="log_enabled",
                default=False,
                required=False,
            ),
        ]

    async def handle(
        self,
        app: IApplication,
    ) -> None:
        """
        Execute the server command to start the Orionis server.

        Parameters
        ----------
        app : IApplication
            The application instance.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Configures server options and launches the server process depending on
        the operating system.
        """
        # Acquire lock for thread safety during server startup
        with self.__lock:

            # Configure server command options
            self.__configureBytecodeWriting(app)
            self.__appendHostAndPortToCommand(app)
            self.__appendInterfaceToCommand(app)
            self.__appendWorkersToCommand(app)
            self.__appendLoopToCommand()
            self.__appendWebsocketSupportToCommand(app)
            self.__appendLoggingConfigurationToCommand(app)
            self.__appendReloadOptionsToCommand(app)
            self.__appendStaticMountAndRouteToCommand(app)
            self.__setShutdownHandler(app)
            self.__appendProcessNameToCommand(
                app.config("app.name") or "orionis-app",
            )

            # Set additional environment variables
            root_path: str = str(app.path("root"))
            self.__env["ORIONIS_BUILD_TIMESTAMP_NS"] = str(app.startAt)
            self.__env["ORIONIS_APP_ROOT_PATH"] = root_path

            # Set the current working directory to the application root
            self.__env["PWD"] = root_path

            # Append the application entrypoint to the command
            self.__cmd.append(app.entryPoint)

            # Launch server using appropriate method for OS
            if os.name != "nt":
                self.__unixServe()
            else:
                await self.__windowsServe()
