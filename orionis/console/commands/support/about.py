from rich.console import Console
from rich.panel import Panel
from orionis.console.base.command import BaseCommand
from orionis.metadata import framework
from orionis.support.time.datetime import DateTime

class VersionCommand(BaseCommand):

    # ruff: noqa: TC002 (DI)

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "about"

    # Command description
    description: str = "Displays the Orionis framework version and metadata."

    def handle(
        self,
        console: Console,
    ) -> None:
        """
        Display Orionis framework version and metadata.

        Retrieves the version and metadata from the framework module and prints it in a
        formatted panel to the console. If the '--without-console' flag is set, returns
        only the version string.

        Parameters
        ----------
        console : Console
            Rich console instance for output.

        Returns
        -------
        None
            This method does not return a value. Output is sent to the console.
        """
        # Retrieve the current framework version
        version = framework.VERSION

        # Compose author and contact information
        author = (
            f"[bold]Author:[/bold] {framework.AUTHOR}  |  "
            f"[bold]Email:[/bold] {framework.AUTHOR_EMAIL}"
        )

        # Compose description string
        desc = f"📝 [italic]{framework.DESCRIPTION}[/italic]"

        # Compose Python requirements string
        python_req = (
            "🐍 [bold]Python Requires:[/bold] >= "
            f"{framework.PYTHON_REQUIRES[0]}.{framework.PYTHON_REQUIRES[1]}"
        )

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
        dt_strftime = DateTime.now().strftime("%Y-%m-%d %H:%M:%S")
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

        # Since this command is primarily for console output,
        # it does not return any value.
