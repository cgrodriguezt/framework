import os
import signal
import subprocess
import sys
from pathlib import Path
from threading import RLock
from typing import Self
from orionis.console.base.command import BaseCommand
from orionis.foundation.contracts.application import IApplication

class ServerCommand(BaseCommand):

    # ruff: noqa: S603, S606, S104, PLR0913, ARG001

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

        Sets the shutting down flag to False and initializes a reentrant lock
        for thread safety.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Solo inicializar una vez
        if not hasattr(self, "_initialized"):
            self.__shutting_down = False
            self.__lock = RLock()
            self._initialized = True

    def __buildCMD( # NOSONAR
        self,
        app: IApplication,
        host: str,
        port: int,
        public_disk: dict,
        app_config: dict,
        *,
        has_websockets: bool,
    ) -> list[str]:
        """
        Build the command to start the Granian server.

        Parameters
        ----------
        app : IApplication
            The application instance.
        has_websockets : bool
            Indicates if the application supports WebSockets.
        host : str
            The host address to bind the server.
        port : int
            The port number to bind the server.
        public_disk : dict
            The public disk configuration.
        app_config : dict
            The application configuration.

        Returns
        -------
        list of str
            The command as a list of arguments to execute Granian.
        """
        # Ensure thread safety during command construction
        with self.__lock:

            # Resolve the static mount path
            static_mount: Path = Path(public_disk.get("path", "storage/app/public"))
            if not static_mount.is_absolute():
                static_mount = Path(app.path("root")) / static_mount
            static_mount = static_mount.resolve()

            # Prepare static URL and worker count
            static_url: str = public_disk.get("url", "/static").lstrip("/")
            is_production: bool = app.isProduction()
            workers: int = max(1, app_config.get("workers") or (os.cpu_count() or 1))

            # Build the base command
            cmd: list[str] = [
                sys.executable,
            ]

            # Add debug flag for non-production environments
            if not is_production:
                cmd.append("-B")

            # Add Granian server options
            cmd.extend([
                "-m",
                "granian",
                "--host", str(host),
                "--port", str(port),
                "--interface", "asgi" if has_websockets else "rsgi",
                "--workers", str(workers),
                "--loop", "uvloop" if os.name != "nt" else "auto",
                "--http", "auto",
            ])

            # Add WebSocket support flag
            cmd.append("--ws" if has_websockets else "--no-ws")

            if is_production:

                # Production logging options
                cmd.extend([
                    "--log-level", "error",
                ])

            else:

                # Development logging and reload options
                cmd.append("--no-log")

                watch_dirs = app.cacheConfiguration
                if watch_dirs and "monitored_dirs" in watch_dirs:
                    reload_paths = [
                        p.resolve() for p in watch_dirs["monitored_dirs"]
                        if isinstance(p, Path) and p.exists()
                    ]
                    if reload_paths:
                        cmd.append("--reload")
                        # Add --reload-paths for each monitored directory
                        for path in reload_paths:
                            cmd.extend(["--reload-paths", str(path)])

            # Add static path mount and route, and entry point
            cmd.extend([
                "--static-path-mount", str(static_mount),
                "--static-path-route", static_url,
                str(app.entryPoint),
            ])

            return cmd

    def handle( # NOSONAR
        self,
        app: IApplication,
    ) -> None:
        """
        Start the Orionis server with Granian and manage shutdown.

        Parameters
        ----------
        app : IApplication
            The application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Ensure thread safety during server startup
        with self.__lock:

            # Retrieve application and filesystem configuration
            app_config: dict = app.config("app")
            filesystems_config: dict = app.config("filesystems")
            public_disk: dict = filesystems_config.get("disks", {}).get("public", {})
            has_websockets: bool = app.hasWebSockets()
            is_production: bool = app.isProduction()

            # Determine host and port based on environment
            host: str = app_config.get("host") or (
                "0.0.0.0" if is_production else "127.0.0.1"
            )
            port: int = app_config.get("port", 8000)

            # Build the command to launch the server
            cmd: list[str] = self.__buildCMD(
                app, host, port, public_disk, app_config, has_websockets=has_websockets,
            )

            # Prepare environment variables for the subprocess
            env = os.environ.copy()
            env["PYTHONUTF8"] = "1"
            env["PYTHONIOENCODING"] = "utf-8"

            # Launch the Granian server as a subprocess
            sys.stdout.flush()

            # Use execvpe on Unix-like systems to replace the current process
            if os.name != "nt":
                os.execvpe(cmd[0], cmd, env)
            else:

                # On Windows, use Popen to start a new process
                process = subprocess.Popen(cmd, env=env)

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
                    # Ignore shutdown in production mode
                    if is_production:
                        return

                    # Ensure thread safety during shutdown
                    with self.__lock:

                        # Avoid multiple shutdown attempts
                        if not self.__shutting_down:
                            self.__shutting_down = True
                            shotdown_method_name: str = "_Application__onShutdown"
                            if hasattr(app, shotdown_method_name):
                                getattr(app, shotdown_method_name)()
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
