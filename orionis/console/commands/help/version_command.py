from __future__ import annotations
from typing import TYPE_CHECKING
from rich.panel import Panel
from orionis.console.args.argument import CLIArgument
from orionis.console.base.command import BaseCommand
from orionis.console.exceptions import CLIOrionisException
from orionis.metadata import framework

if TYPE_CHECKING:
    from rich.console import Console
    from orionis.support.time.contracts.datetime import IDateTime

class VersionCommand(BaseCommand):

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "version"

    # Command description
    description: str = (
        "Displays the current Orionis framework version and metadata, "
        "including author, Python requirements, documentation, and repository links."
    )

    def options(self) -> list[CLIArgument]:
        """
        Define the command-line options for the `version` command.

        Specifies the arguments that can be passed to the command from the CLI.
        Each argument is represented as a `CLIArgument` instance.

        Returns
        -------
        list[CLIArgument]
            List containing CLIArgument objects for available options.
        """
        return [
            CLIArgument(
                flags=["--without-console"],
                type=bool,
                help="Return only the version string, without console output.",
                required=False,
            ),
        ]

    def handle(self, console: Console, datetime: IDateTime) -> str | None:
        """
        Display Orionis framework version and metadata.

        Retrieves the version and metadata from the framework module, and prints it in a
        formatted panel to the console. If the '--without-console' flag is set, returns
        only the version string.

        Parameters
        ----------
        console : Console
            Rich console instance for output.
        datetime : IDateTime
            DateTime contract for timestamp.

        Returns
        -------
        str
            The current version string of the Orionis framework.

        Raises
        ------
        CLIOrionisException
            Raised if an unexpected error occurs during execution.
        """
        try:

            # Get the current framework version
            version = framework.VERSION

            # If the --without-console flag is set, return just the version string
            if self.argument("without_console") is True:
                return version

            # Compose author and contact information
            author = (
                f"👤 [bold]Author:[/bold] {framework.AUTHOR}  |  "
                f"✉️ [bold]Email:[/bold] {framework.AUTHOR_EMAIL}"
            )

            # Compose description string
            desc = f"📝 [italic]{framework.DESCRIPTION}[/italic]"

            # Compose Python requirements string
            python_req = f"🐍 [bold]Python Requires:[/bold] {framework.PYTHON_REQUIRES}"

            # Compose documentation link string
            docs = (
                f"📖 [bold]Docs:[/bold]"
                f"[underline blue]{framework.DOCS}[/underline blue]"
            )

            # Compose repository link string
            repo = (
                f"💻 [bold]Repo:[/bold]"
                f"[underline blue]{framework.FRAMEWORK}[/underline blue]"
            )

            # Combine all information into the panel body
            body = (
                f"{desc}\n\n"
                f"{author}\n"
                f"{python_req}\n"
                f"{docs}\n"
                f"{repo}\n"
            )

            # Create a styled panel with the collected information
            name = framework.NAME.capitalize()
            dt_strftime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            panel = Panel(
                body,
                title=f"[bold green]{name} Framework | v{version}[/]",
                border_style="bright_blue",
                padding=(1, 2),
                expand=False,
                subtitle=f"[grey50]{dt_strftime}[/grey50]",
                subtitle_align="right",
            )

            # Print a blank line, the panel, and another blank line for spacing
            console.line()
            console.print(panel)
            console.line()

        except Exception as e:

            # Raise a custom runtime error if any exception occurs
            error_msg = f"An unexpected error occurred: {e}"
            raise CLIOrionisException(error_msg) from e
