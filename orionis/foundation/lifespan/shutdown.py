from __future__ import annotations
from typing import Generator
from orionis.foundation.contracts.application import IApplication

def shutdown_orionis_generator(app: IApplication) -> Generator[None, None, None]:
    """
    Shut down the Orionis application and display the elapsed runtime.

    Parameters
    ----------
    app : IApplication
        Orionis application instance.

    Returns
    -------
    Generator[None, None, None]
        Generator that yields once after displaying the shutdown panel and
        prints the server uptime summary.
    """
    # Only show shutdown panel in debug mode
    if app.isDebug():

        # Lazy imports for debug mode only
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        from rich.table import Table
        import time

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
            time.sleep(0.5)

    # Inyield to allow shutdown process to continue
    yield

    # After yielding, display the server uptime summary in debug mode
    if app.isDebug():

        # Print line separator
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
