import os
import sys
import subprocess
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from orionis.console.base.command import BaseCommand
from orionis.console.exceptions import CLIOrionisRuntimeError
from orionis.support.facades.application import Application

class ServerCommand(BaseCommand):
    """
    Starts the Orionis HTTP server using Granian.

    This command initializes the Orionis server with the configuration
    specified in the application settings. It sets up the server interface,
    host, port, worker count, and reload options, then launches the server
    process. The command also displays a styled message in the console
    indicating the server status and handles graceful shutdown on interruption.

    Returns
    -------
    None
        This method does not return any value.
    """
    timestamps = False
    signature = "serve"
    description = "Initializes the Orionis server with Granian."

    def handle(self):
        """
        Handles the execution of the server command.

        Reads configuration from the application, constructs the command to
        start the Granian server, displays a status panel, and manages the
        server process lifecycle including graceful shutdown on interruption.

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

            # Ensure the static file directory exists
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)

            # Build the command to launch the Granian server
            # Do NOT wrap the path in quotes; Granian expects a raw path
            cmd = [
                sys.executable, "-B", "-m", "granian",
                "--interface", interface,
                "--host", host,
                "--port", str(port),
                "--workers", "1" if os.name == "nt" else str(workers),
                "--no-log",
                "--static-path-route", url,
                "--static-path-mount", path,
                app_path
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
                ("Ctrl+C", "bold yellow")
            )

            # Display the message in a styled panel
            rich_console.print(
                Panel(panel_content, border_style="green", padding=(1, 2))
            )

            # Add another blank line for better formatting
            rich_console.line()

            # Ensure the current working directory is in the import path
            sys.path.insert(0, os.getcwd())

            # Start the Granian server process
            # IMPORTANT: Do not use creationflags on Windows to allow child to share the console.
            process = subprocess.Popen(
                cmd,
                stdout=sys.stdout,
                stderr=sys.stderr,
                stdin=None,
                shell=False,
            )

            def shutdown():
                """
                Gracefully shuts down the server process.

                Terminates the server process if it is still running and waits
                for it to exit. If termination fails, forcibly kills the process.

                Returns
                -------
                None
                    This method does not return any value.
                """
                if process.poll() is None:
                    self.writeLine("Shutting down Orionis server...")
                    try:
                        process.terminate()
                        process.wait(timeout=5)
                    except Exception:
                        process.kill()
                    self.info("Orionis server stopped.")

            # Wait for the server process to exit, handling Ctrl+C for graceful shutdown
            try:
                process.wait()
            except KeyboardInterrupt:
                shutdown()

            # Report non-zero exit codes as errors
            if process.returncode not in (0, None):
                self.error(f"Orionis server exited with code {process.returncode}")

        except Exception as e:

            # Raise a CLI-specific runtime error if server startup fails
            raise CLIOrionisRuntimeError(f"Failed to start Orionis server: {e}") from e
