from rich.console import Console
from rich.panel import Panel
from orionis.console.base.command import BaseCommand
from orionis.console.contracts.reactor import IReactor
from orionis.console.exceptions import CLIOrionisRuntimeError

class HelpCommand(BaseCommand):

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "help"

    # Command description
    description: str = (
        "Displays usage information, examples, and a list of available "
        "commands in the Orionis CLI."
    )

    def handle(self, reactor: IReactor, console: Console) -> dict:
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
        dict
            List of available commands with their signature and description.

        Raises
        ------
        CLIOrionisRuntimeError
            If help information generation or display fails.
        """
        try:

            # Retrieve the list of available commands from the reactor
            commands = reactor.info()

            # Build the usage and commands help text
            template_command = "python -B reactor <command> <params/flags>\n"
            usage = f"[bold cyan]Usage:[/]\n  {template_command}\n"

            # Add example usage
            template_example = "python -B reactor app:command --flag\n"
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
                title="[bold green]Orionis CLI | Reactor[/]",
                expand=False,
                border_style="bright_blue",
                padding=(1, 2),
            )

            # Print the panel to the console
            console.print()
            console.print(panel)
            console.print()

            # Return the list of commands for potential further use
            return commands

        except Exception as e:

            # Assign error message before raising the exception
            error_msg = f"An unexpected error occurred: {e}"
            raise CLIOrionisRuntimeError(error_msg) from e
