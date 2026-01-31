from __future__ import annotations
from typing import Generator
from orionis.foundation.contracts.application import IApplication

def startup_orionis_generator(app: IApplication) -> Generator[None, None, None]:
    """
    Display the Orionis HTTP server status panel using Rich.

    Parameters
    ----------
    app : IApplication
        The application instance providing configuration and status.

    Returns
    -------
    None
        This function does not return a value.
    """
    # Only show startup panel in debug mode
    if app.isDebug():

        # Lazy imports for debug mode only
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        import time

        # Initialize Rich console for output
        console = Console()

        # Show startup panel to indicate server is starting
        panel = Panel(
            Text("⚡ Encendiendo el servidor Orionis...", style="bold green"),
            title="Orionis Startup",
            border_style="green",
            padding=(1, 1),
        )
        # Use console.screen to temporarily show the panel
        with console.screen():
            console.print(panel)
            time.sleep(0.5)

    # Inyield to allow startup process to continue
    yield

    # Only display the status panel in debug mode
    if app.isDebug():

        # Lazy imports for debug mode only
        import os

        # Prepare and display the status panel
        console = Console()
        console.clear()
        console.line()
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        pid = os.getpid()

        # Retrieve host and port from application configuration
        host = app.config("app.host", "127.0.0.1")
        port = app.config("app.port", 8000)

        # Adjust host display for localhost
        if host == "127.0.0.1":
            host = "localhost"

        # Build the panel content for server status
        panel_content = Text.assemble(
            ("🚀 Orionis HTTP Server\n", "bold white on green"),
            ("\n", ""),
            ("✅ The HTTP server has started successfully.\n", "bold green"),
            ("🔗 Service running at: ", "white"),
            (f"http://{host}:{port}\n", "bold cyan"),
            (f"🕒 Started at: {now}   ", "dim"),
            (f"🆔 PID: {pid}\n", "dim"),
            ("\n", ""),
            ("🛑 To stop the server, press ", "white"),
            ("Ctrl+C", "bold yellow"),
        )

        # Render the status panel to the console
        console.print(
            Panel(
                panel_content,
                border_style="green",
                padding=(1, 2),
                title="Orionis Status",
                title_align="left",
            ),
        )
        console.line()
