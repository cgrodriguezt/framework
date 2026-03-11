import argparse
from typing import Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from orionis.console.output.contracts.help_command import IHelpCommand

class HelpCommand(IHelpCommand):

    # ruff: noqa: SLF001

    @staticmethod
    def parseActions(
        actions: list[argparse.Action],
    ) -> dict[str, Any]:
        """
        Parse argparse actions and categorize them.

        Parameters
        ----------
        actions : list of argparse.Action
            List of argparse actions to parse.

        Returns
        -------
        dict[str, Any]
            Dictionary containing categorized actions: help, positionals,
            optionals, and subcommands.
        """
        result = {
            "help": None,
            "positionals": [],
            "optionals": [],
            "subcommands": {},
        }

        for action in actions:
            # Collect action metadata for later categorization
            action_data = {
                "action_class": action.__class__.__name__,
                "dest": action.dest,
                "flags": action.option_strings,
                "nargs": action.nargs,
                "const": action.const,
                "default": action.default,
                "type": (
                    getattr(action.type, "__name__", str(action.type))
                    if action.type else "str"
                ),
                "choices": action.choices,
                "required": action.required,
                "help": action.help,
                "metavar": action.metavar,
            }

            # Identify help action and store its metadata
            if isinstance(action, argparse._HelpAction):
                result["help"] = action_data
                continue

            # Identify subcommands and recursively parse their actions
            if isinstance(action, argparse._SubParsersAction):
                for name, subparser in action.choices.items():
                    result["subcommands"][name] = {
                        "help": subparser.description,
                        "arguments": HelpCommand.parseActions(subparser._actions),
                    }
                continue

            # Categorize optionals and positionals
            if action.option_strings:
                result["optionals"].append(action_data)
            else:
                result["positionals"].append(action_data)

        return result

    @staticmethod
    def printActions(
        command_name: str,
        actions: list[argparse.Action],
        is_error: bool = False,
    ) -> None:
        """
        Render CLI help information for a command or show error if parsing failed.

        Parameters
        ----------
        command_name : str
            Name of the command to display help for.
        actions : list of argparse.Action
            List of argparse actions to render in the help output.
        is_error : bool, optional
            If True, indicates this is an error output (default: False).

        Returns
        -------
        None
            This method does not return a value; it outputs to the console and exits.
        """
        console = Console()

        # Print a blank line for spacing
        console.print()
        if is_error:
            # Show error panel if command usage is invalid
            error_msg = (
                f"[bold red]Error:[/bold red] Invalid usage of "
                f"[bold white]{command_name}[/bold white] command."
            )
            console.print(
                Panel(
                    error_msg,
                    border_style="red",
                    padding=(0, 2),
                    expand=False,
                )
            )
            console.print(
                "[bold red]Failed to parse command arguments.[/bold red]\n"
                "[yellow]Use the help below to see the correct usage.[/yellow]"
            )
        else:
            # Show command help panel
            panel_title = (
                "[bold green]python reactor[/bold green] "
                f"[bold white]{command_name}[/bold white]"
            )
            console.print(
                Panel(
                    panel_title,
                    border_style="cyan",
                    padding=(0, 2),
                    expand=False,
                ),
            )

        # Print a blank line before showing the tables
        console.print()

        # Parse the actions to extract structured command information
        parsed_data = HelpCommand.parseActions(actions)

        # Display positional arguments if present
        if parsed_data["positionals"]:
            table = Table(
                title="Arguments (Positional)",
                box=box.SIMPLE_HEAVY,
                show_lines=True,
            )
            table.add_column("Name", style="bold yellow")
            table.add_column("Type", style="magenta")
            table.add_column("Required", justify="center")
            table.add_column("Description", style="white")

            for arg in parsed_data["positionals"]:
                required = "[red]Yes[/red]" if arg["required"] else "No"
                table.add_row(
                    arg["dest"],
                    arg["type"],
                    required,
                    arg["help"] or "-",
                )

            console.print(table)

        # Display optional arguments if present
        if parsed_data["optionals"]:
            table = Table(
                title="Options",
                box=box.SIMPLE_HEAVY,
                show_lines=False,
                padding=(0, 1),
                collapse_padding=True,
            )
            table.add_column("Flags", style="bold cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Required", justify="center")
            table.add_column("Default", style="green")
            table.add_column("Description", style="white")

            for opt in parsed_data["optionals"]:
                flags = ", ".join(opt["flags"])
                required = "[red]Yes[/red]" if opt["required"] else "No"
                default = (
                    str(opt["default"])
                    if opt["default"] not in (None, argparse.SUPPRESS)
                    else "-"
                )
                table.add_row(
                    flags,
                    opt["type"],
                    required,
                    default,
                    opt["help"] or "-",
                )

            console.print(table)

        # Display subcommands if present
        if parsed_data["subcommands"]:
            table = Table(
                title="Subcommands",
                box=box.SIMPLE_HEAVY,
            )
            table.add_column("Command", style="bold green")
            table.add_column("Description")

            for name, sub in parsed_data["subcommands"].items():
                table.add_row(name, sub.get("help") or "-")

            console.print(table)