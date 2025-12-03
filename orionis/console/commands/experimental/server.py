import os
import subprocess
import sys
import time

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from orionis.console.base.command import BaseCommand
from orionis.console.exceptions import CLIOrionisRuntimeError
from orionis.support.facades.application import Application


class ServerCommand(BaseCommand):

    # Disable timestamps in command output
    timestamps = False

    # The command signature used to invoke this command
    signature = "serve"

    # A brief description of the command
    description = "Initializes the Orionis server with Granian."

    def handle(self) -> None:
        """
        Execute the server command.

        Read configuration, construct the Granian server command, display
        status, and manage the server process lifecycle including shutdown.

        Returns
        -------
        None
            This method does not return any value.
        """
        try:

            # Retrieve application configuration for server settings
            app_config: dict = Application.config("app")
            host: str = app_config.get("host", "127.0.0.1")
            port: int = app_config.get("port", 8000)
            workers: int = app_config.get("workers", 1)
            reload: bool = app_config.get("reload", False)
            interface: str = app_config.get("interface", "asgi")
            app_path: str = "bootstrap.app:app"

            # Retrieve filesystem configuration for static file serving
            filesystems_config: dict = Application.config("filesystems")
            public_disk: dict = filesystems_config.get("disks", {}).get("public", {})
            path: str = public_disk.get("path", "storage/app/public")
            url: str = public_disk.get("url", "static")

            # Ensure the static file path is absolute
            if not os.path.isabs(path):
                path = os.path.abspath(os.path.join(os.getcwd(), path))

            # Create the static file directory if it does not exist
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)

            # Build the command to launch the Granian server
            cmd = [
                sys.executable, "-B", "-m", "granian",
                "--interface", interface,
                "--host", host,
                "--port", str(port),
                "--workers", "1" if os.name == "nt" else str(workers),
                "--no-log",
                "--static-path-route", url,
                "--static-path-mount", path,
                app_path,
            ]
            if reload:
                cmd.append("--reload")

            # Initialize Rich console for styled output
            rich_console = Console()
            rich_console.clear()
            rich_console.line()
            now = time.strftime("%Y-%m-%d %H:%M:%S")

            # Prepare the panel content with server status information
            panel_content = Text.assemble(
                ("🚀 Orionis HTTP Server ", "bold white on green"),
                ("\n\n", ""),
                ("✅ The HTTP server has started successfully.\n", "white"),
                (f"🔗 Service running at: http://{host}:{port}\n", "bold cyan"),
                (f"🕒 Started at: {now} | 🆔 PID: {os.getpid()}\n", "dim"),
                ("🛑 To stop the server, press ", "white"),
                ("Ctrl+C", "bold yellow"),
            )

            # Display the message in a styled panel
            rich_console.print(
                Panel(panel_content, border_style="green", padding=(1, 2)),
            )

            # Add another blank line for better formatting
            rich_console.line()

            # Ensure the current working directory is in the import path
            sys.path.insert(0, os.getcwd())

            # Ensure all elements in cmd are strings and trusted
            def raise_runtime_error(msg):
                raise CLIOrionisRuntimeError(msg)

            if not all(isinstance(arg, str) for arg in cmd):
                error_msg = "Invalid command arguments detected."
                raise_runtime_error(error_msg)

            # Start the Granian server process
            process = subprocess.Popen( # noqa: S603
                cmd,
                stdout=sys.stdout,
                stderr=sys.stderr,
                stdin=None,
                shell=False,
            )

            def shutdown() -> None:
                """
                Gracefully shut down the server process.

                Terminate the server process if running and wait for exit.
                If termination fails, forcibly kill the process.

                Returns
                -------
                None
                    This method does not return any value.
                """
                # Check if the process is still running
                if process.poll() is None:
                    self.writeLine("Shutting down Orionis server...")
                    try:
                        process.terminate()
                        process.wait(timeout=5)
                    except (subprocess.TimeoutExpired, OSError):
                        process.kill()
                    self.info("Orionis server stopped.")

            # Wait for the server process to exit, handling Ctrl+C for shutdown
            try:
                process.wait()
            except KeyboardInterrupt:
                shutdown()

            # Report non-zero exit codes as errors
            if process.returncode not in (0, None):
                self.error(f"Orionis server exited with code {process.returncode}")

        except Exception as e:

            # Raise a CLI-specific runtime error if server startup fails
            error_msg = (
                "An error occurred while starting the Orionis server: "
                f"{str(e)!r}"
            )
            raise CLIOrionisRuntimeError(error_msg) from e
