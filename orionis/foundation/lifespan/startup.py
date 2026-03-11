from __future__ import annotations
import asyncio
import os
import time
from typing import TYPE_CHECKING
from orionis.support.time.local import LocalDateTime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

if TYPE_CHECKING:
    from collections.abc import Generator
    from orionis.foundation.contracts.application import IApplication

def before_startup_orionis_generator(
    app: IApplication,
) -> None:
    """
    Display the Orionis server startup panel if in debug mode.

    Parameters
    ----------
    app : IApplication
        The application instance providing configuration and status.

    Returns
    -------
    None
        This function does not return a value.
    """
    # Determine if we should print the startup panel
    print_panel: bool = app.isDebug() and not app.isProduction()

    # Only show the startup panel in debug mode
    if not print_panel:
        return

    # Initialize Rich console
    console = Console()

    # Show startup panel to indicate server is starting
    panel: Panel = Panel(
        Text("⚡ Starting the Orionis server...", style="bold green"),
        title="Orionis Startup",
        border_style="green",
        padding=(1, 1),
    )
    # Use console.screen to temporarily show the panel
    with console.screen():
        console.print(panel)
        time.sleep(0.5)

    # Delete console reference
    del console

def after_startup_orionis_generator(
    app: IApplication,
) -> None:
    """
    Display the Orionis HTTP server status panel after startup.

    Parameters
    ----------
    app : IApplication
        The application instance providing configuration and status.

    Returns
    -------
    None
        This function does not return a value.
    """
    # Determine if we should print the startup panel
    print_panel: bool = app.isDebug() and not app.isProduction()

    # Only show the startup panel in debug mode
    if not print_panel:
        return

    # Initialize Rich console for output
    console = Console()

    # Clear previous output and add spacing
    console.clear()
    console.line()
    now: str = LocalDateTime.now().strftime("%Y-%m-%d %H:%M:%S")
    pid: int = os.getpid()

    # Retrieve host and port from application configuration
    host: str = os.environ.get("GRANIAN_HOST", app.config("app.host"))
    port: int = os.environ.get("GRANIAN_PORT", app.config("app.port"))

    # Adjust host display for localhost
    if host in ("127.0.0.1", "0.0.0.0"):
        host = "localhost"

    # Detect the current asyncio event loop policy and server interface
    loop_policy = asyncio.get_event_loop_policy()
    loop_name = loop_policy.__class__.__name__.replace("_", "")
    interface_maps = {
        "rsgi": "🦀 Rust Network Protocol Servers",
        "asgi": "⚡ Asynchronous Server Gateway Interface",
    }
    interface = interface_maps.get(os.environ.get("GRANIAN_INTERFACE"), "Auto-detected")

    # Build the panel content for server status
    panel_content: Text = Text.assemble(
        (" 🚀 Orionis HTTP Server \n", "bold white on green"),
        ("\n", ""),
        ("✅ The HTTP server has started successfully.\n", "bold green"),
        ("🔗 Service running at: ", "white"),
        (f"http://{host}:{port}\n", "bold cyan"),
        (f"🕒 Started at: {now}   ", "dim"),
        (f"🆔 PID: {pid}\n", "dim"),
        ("⚡ Orionis Loop Policy: ", "cyan"),
        (f"{loop_name}\n", "bold magenta"),
        ("🌐 Server Interface: ", "cyan"),
        (f"{interface}\n", "bold magenta"),
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
        ),
    )
    console.line()

    # Clean up console reference
    del console

def startup_orionis_generator(
    app: IApplication,
) -> Generator[None, None, None]:
    """
    Start the Orionis HTTP server and display status panels.

    Parameters
    ----------
    app : IApplication
        The application instance providing configuration and status.

    Yields
    ------
    None
        This generator yields once after displaying the startup panel.

    Returns
    -------
    Generator[None, None, None]
        A generator that manages the display of startup and status panels.
    """
    before_startup_orionis_generator(app)
    yield
    after_startup_orionis_generator(app)
