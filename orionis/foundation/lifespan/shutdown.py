from __future__ import annotations
import time
from typing import TYPE_CHECKING
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from collections.abc import Generator
    from orionis.foundation.contracts.application import IApplication

def before_shutdown_orionis_generator(
    app: IApplication,
) -> None:
    """
    Display the shutdown panel if in debug and not production mode.

    Parameters
    ----------
    app : IApplication
        The Orionis application instance.

    Returns
    -------
    None
        This function does not return a value.
    """
    # Determine if the shutdown panel should be printed
    print_panel: bool = app.isDebug() and not app.isProduction()
    if not print_panel:
        return

    # Initialize Rich console for output
    console = Console()

    # Show shutdown panel to indicate server is stopping
    panel = Panel(
        Text("🛑 Stopping Orionis server...", style="bold red"),
        title="Orionis Shutdown",
        border_style="red",
        padding=(1, 1),
    )
    # Use console.screen to temporarily show the panel
    with console.screen():
        console.print(panel)
        # Brief pause to ensure panel is visible before shutdown
        time.sleep(0.1)

    # Delete console reference
    del console

def after_shutdown_orionis_generator(
    app: IApplication,
) -> None:
    """
    Display the server uptime summary panel after shutdown.

    Parameters
    ----------
    app : IApplication
        The Orionis application instance.

    Returns
    -------
    None
        This function does not return a value.
    """
    # Determine if the shutdown summary panel should be printed
    print_panel: bool = app.isDebug() and not app.isProduction()

    # Only show the summary panel in debug mode and not in production
    if not print_panel:
        return

    # Initialize Rich console for output
    console = Console()

    # Print line separator and rule for visual clarity
    console.line()
    console.rule()
    console.line()

    # Calculate elapsed time in nanoseconds since app start
    elapsed_ns = max(0, time.time_ns() - app.startAt)
    elapsed_s, ns_rem = divmod(elapsed_ns, 1_000_000_000)
    days, rem = divmod(elapsed_s, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, rem = divmod(rem, 60)
    seconds = rem
    milliseconds = ns_rem // 1_000_000

    # Display elapsed time in a formatted table
    table = Table(
        show_header=True,
        header_style="bold white on green",
        title="Summary: Orionis Server Uptime",
        border_style="green",
        min_width=console.width / 2,
    )
    table.add_column("Days", style="white", justify="center")
    table.add_column("Hours", style="white", justify="center")
    table.add_column("Minutes", style="white", justify="center")
    table.add_column("Seconds", style="white", justify="center")
    table.add_column("Milliseconds", style="white", justify="center")

    table.add_row(
        str(int(days)),
        str(int(hours)),
        str(int(minutes)),
        str(seconds),
        str(milliseconds),
    )

    console.print(table)
    console.line()

    # Clean up console reference
    del console

def shutdown_orionis_generator(
    app: IApplication,
) -> Generator[None]:
    """
    Shut down the Orionis application and display the elapsed runtime.

    Parameters
    ----------
    app : IApplication
        The Orionis application instance.

    Returns
    -------
    Generator[None, None, None]
        A generator that yields once after displaying the shutdown panel and
        prints the server uptime summary.
    """
    before_shutdown_orionis_generator(app)
    yield
    after_shutdown_orionis_generator(app)
