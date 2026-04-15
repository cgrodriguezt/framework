from __future__ import annotations
import asyncio
import os
import time
from typing import TYPE_CHECKING
from orionis.support.time.datetime import DateTime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

if TYPE_CHECKING:
    from collections.abc import Generator
    from orionis.foundation.contracts.application import IApplication

def before_startup_orionis_generator() -> None:
    """
    Render a brief startup panel before the server begins accepting requests.

    Returns
    -------
    None
        Displays the panel for 0.5 s using a fullscreen context, then returns.
    """
    console = Console()

    # Build and show the startup splash panel
    panel: Panel = Panel(
        Text("⚡ Starting the Orionis server...", style="bold green"),
        title="Orionis Startup",
        border_style="green",
        padding=(1, 1),
    )

    with console.screen():
        console.print(panel)
        time.sleep(0.5)

def after_startup_orionis_generator(host: str, port: int) -> None:
    """
    Render the server status panel after a successful startup.

    Parameters
    ----------
    host : str
        Hostname used to bind the server.
    port : int
        Port number used to bind the server.

    Returns
    -------
    None
        Prints the status panel to stdout and returns nothing.
    """
    console = Console()

    # Clear the terminal and print a blank line for spacing
    console.clear()
    console.line()
    now: str = DateTime.now().strftime("%Y-%m-%d %H:%M:%S")
    pid: int = os.getpid()

    # Environment variables take precedence over config values
    host: str = os.environ.get("GRANIAN_HOST", host)
    port: int = os.environ.get("GRANIAN_PORT", port)

    # Normalize loopback addresses to a human-readable label
    if host in ("127.0.0.1", "0.0.0.0"):
        host = "localhost"

    # Resolve the active event loop name and server interface label
    loop = asyncio.get_running_loop()
    loop_name = f"{loop.__class__.__module__}.{loop.__class__.__name__}"
    interface_maps = {
        "rsgi": "🦀 RSGI: Rust Network Protocol Servers",
        "asgi": "⚡ ASGI: Asynchronous Server Gateway Interface",
    }
    interface = interface_maps.get(
        os.environ.get("GRANIAN_INTERFACE"), "Auto-detected"
    )

    # Assemble the rich panel content
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

    console.print(
        Panel(
            panel_content,
            border_style="green",
            padding=(1, 2),
        ),
    )
    console.line()

def startup_orionis_generator(app: IApplication) -> Generator[None, None, None]:
    """
    Yield control between the pre- and post-startup display steps.

    Parameters
    ----------
    app : IApplication
        Application instance used to read config values and mode flags.

    Returns
    -------
    Generator[None, None, None]
        Yields once; pre-startup runs before the yield, post-startup after.
    """
    # Only show panels in debug mode outside of production
    print_panel: bool = app.isDebug() and not app.isProduction()

    if print_panel:
        before_startup_orionis_generator()

    yield

    if print_panel:
        after_startup_orionis_generator(
            host=app.config("app.host"),
            port=app.config("app.port"),
        )
