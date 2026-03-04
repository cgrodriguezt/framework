from rich.console import Console
from rich.panel import Panel
from orionis.console.base.command import BaseCommand
from orionis.console.core.contracts.reactor import IReactor

class HelpCommand(BaseCommand):

    # ruff: noqa: TC001, TC002 (DI)

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "list"

    # Command description
    description: str = "Show available commands and usage."

    async def handle(
        self,
        reactor: IReactor,
        console: Console,
    ) -> None:
        """
        Display usage information and available commands for the Orionis CLI.

        Parameters
        ----------
        reactor : IReactor
            Reactor instance providing command metadata via `info()` method.
        console : Console
            Rich console instance for output.

        Returns
        -------
        None
            This method outputs help information to the console and returns None.
        """
        # Retrieve the list of available commands from the reactor
        commands = await reactor.info()

        # Build the usage and commands help text
        template_command = "python reactor <command> <params/flags>\n"

        # Add usage section
        usage = f"[bold cyan]Usage:[/]\n  {template_command}\n"

        # Add example usage section
        template_example = "python reactor app:command --flag\n"

        usage += f"[bold cyan]Example:[/]\n  {template_example}\n"

        # Add section for available commands
        usage += "[bold cyan]Available Commands:[/]\n"

        # Determine the maximum signature length for alignment
        max_sig_len = max((len(cmd["signature"]) for cmd in commands), default=0)

        # Append each command's signature and description to the usage string
        for cmd in commands:
            usage += (
                f"  [bold yellow]{cmd['signature']:<{max_sig_len}}[/]  "
                f"{cmd['description']}\n"
            )

        # Add options section
        usage += (
            "\n[bold cyan]Options:[/]\n"
            "  -h, --help    Show this help message and exit"
        )

        # Create a rich panel to display the help information
        panel = Panel(
            usage,
            title="[bold green]Orionis Framework | Reactor CLI[/]",
            expand=False,
            border_style="bright_blue",
            padding=(1, 2),
        )

        # Print the panel to the console
        console.print()
        console.print(panel)
        console.print()
