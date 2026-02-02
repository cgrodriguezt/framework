import os
import signal
import subprocess
import sys
from pathlib import Path
from threading import RLock
from typing import Self, TYPE_CHECKING
from orionis.console.base.command import BaseCommand
from orionis.foundation.contracts.application import IApplication
from orionis.metadata.framework import PYTHON_REQUIRES, VERSION
from orionis.services.environment.env import Env

if TYPE_CHECKING:
    from collections.abc import Callable

class ServerCommand(BaseCommand):

    # ruff: noqa: S603, S606, S104, ARG001

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
        Env.reload()
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

        # Use port from config or default to 8000
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
        # Check if the application supports WebSockets
        has_websockets: bool = app.hasWebSockets()

        # Determine the interface type based on WebSocket support
        interface_type: str = "asgi" if has_websockets else "rsgi"

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
        event_loop: str = "uvloop" if os.name != "nt" else "winloop"

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
        # Determine if the application is in production mode
        is_production: bool = app.isProduction()

        # Append logging options based on the environment
        if is_production:

            # Production logging options
            self.__cmd.extend([
                "--log"
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

    def __windowsServe(
        self,
    ) -> None:
        """
        Serve the application on Windows systems.

        Launches the Granian server as a subprocess and handles graceful shutdown
        on SIGINT (Ctrl+C).

        Returns
        -------
        None
            This method does not return a value.
        """
        # Launch the Granian server as a subprocess
        process = subprocess.Popen(self.__cmd, env=self.__env)

        # Define signal handler for graceful shutdown
        def handle_interrupt(signum: int, frame: object) -> None:
            """
            Handle SIGINT for graceful shutdown in development mode.

            Parameters
            ----------
            signum : int
                The signal number received.
            frame : object
                The current stack frame.

            Returns
            -------
            None
                This function does not return a value.
            """
            # Ensure thread safety during shutdown
            with self.__lock:

                # Ignore if reload is not enabled
                if not self.__app_reload:
                    return

                # Avoid multiple shutdown attempts
                if not self.__shutting_down:

                    # Mark as shutting down and terminate the process
                    self.__shutting_down = True

                    # Call the application's shutdown handler
                    if self.__call_in_showdown:
                        self.__call_in_showdown()

                    # Terminate the server subprocess
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()

        # Register signal handler for SIGINT (Ctrl+C)
        original_handler = signal.signal(signal.SIGINT, handle_interrupt)

        try:
            # Wait for the server process to complete
            process.wait()
        finally:
            # Restore the original signal handler
            signal.signal(signal.SIGINT, original_handler)

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

    def handle(
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
                app.config("app.name") or "orionis-app"
            )

            # Set additional environment variables
            root_path: str = str(Path(app.path("root")).resolve())
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
                self.__windowsServe()
