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

def before_shutdown_orionis_generator() -> None:
    """
    Render a brief shutdown panel before the server stops accepting requests.

    Returns
    -------
    None
        Displays the panel for 0.1 s using a fullscreen context, then returns.
    """
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
    start_at: int,
) -> None:
    """
    Render the server uptime summary panel after a successful shutdown.

    Parameters
    ----------
    start_at : int
        Timestamp in nanoseconds (from ``time.time_ns()``) recorded when the
        application started, used to calculate total uptime.

    Returns
    -------
    None
        Prints the uptime summary table to stdout and returns nothing.
    """
    # Initialize Rich console for output
    console = Console()

    # Print line separator and rule for visual clarity
    console.line()
    console.rule()
    console.line()

    # Calculate elapsed time in nanoseconds since app start
    elapsed_ns = max(0, time.time_ns() - start_at)
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
    Yield control between the pre- and post-shutdown display steps.

    Parameters
    ----------
    app : IApplication
        Application instance used to read mode flags and the startup timestamp.

    Returns
    -------
    Generator[None]
        Yields once; pre-shutdown runs before the yield, post-shutdown after.
    """
    print_panel: bool = app.isDebug() and not app.isProduction()

    if print_panel:
        before_shutdown_orionis_generator()

    yield

    if print_panel:
        after_shutdown_orionis_generator(
            start_at=app.startAt
        )
