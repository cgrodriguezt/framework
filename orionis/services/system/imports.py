from __future__ import annotations
from typing import Any
from orionis.services.system.contracts.imports import IImports

class Imports(IImports):

    # ruff: noqa: PLC0415

    def __init__(self) -> None:
        """
        Initialize the Imports instance.

        Sets up an empty list to store information about user-defined Python modules.
        The list contains dictionaries for each module, including its name, file path,
        and defined symbols.

        Returns
        -------
        None
            This method does not return any value.
        """
        # List to hold information about imported modules
        self.imports: list[dict[str, Any]] = []

    def collect(self) -> Imports: # NOSONAR
        """
        Collect information about user-defined Python modules currently loaded.

        Iterates through all modules in `sys.modules` and gathers details for each
        qualifying module: module name, relative file path, and list of symbols
        (functions, classes, or submodules) defined in the module.

        Parameters
        ----------
        None

        Returns
        -------
        Imports
            The current instance of `Imports` with the `imports` attribute updated
            to include information about the collected modules.
        """
        import sys
        import os
        import types
        from pathlib import Path

        # Clear any previously collected imports
        self.imports.clear()

        # Get standard library paths to exclude standard modules
        stdlib_paths: list[str] = [str(Path(os.__file__).parent)]

        # Get virtual environment path if active
        venv_path: str | None = os.environ.get("VIRTUAL_ENV")
        if venv_path:
            venv_path = str(Path(venv_path).resolve())

        # Iterate over all loaded modules
        for name, module in sys.modules.items():
            file: str | None = getattr(module, "__file__", None)

            # Filter out unwanted modules based on path, type, and name
            if (
                file
                and not any(
                    file.startswith(stdlib_path)
                    for stdlib_path in stdlib_paths
                )
                and (not venv_path or not file.startswith(venv_path))
                and not file.lower().endswith((".pyd", ".dll", ".so"))
                and name not in ("__main__", "__mp_main__")
                and not name.startswith("_distutils")
            ):
                # Get relative file path from current working directory
                # Handle case where file and cwd are on different drives (Windows)
                try:
                    rel_file: str = os.path.relpath(file, Path.cwd())
                except ValueError:
                    # Use absolute path if relative path cannot be calculated
                    rel_file = file
                symbols: list[str] = []

                # Collect symbols defined in the module (functions, classes, submodules)
                try:
                    for attr in dir(module):
                        value = getattr(module, attr)
                        if (
                            isinstance(
                                value,
                                (types.FunctionType, type, types.ModuleType),
                            )
                            and getattr(value, "__module__", None) == name
                        ):
                            symbols.append(attr)
                except (AttributeError, ImportError, KeyError, TypeError):
                    # Ignore known errors during symbol collection
                    pass

                # Only add modules that are not __init__.py and have symbols
                if not rel_file.endswith("__init__.py") and symbols:
                    self.imports.append({
                        "name": name,
                        "file": rel_file,
                        "symbols": symbols,
                    })

        # Return the current instance with updated imports
        return self

    def display(self) -> None:
        """
        Display a formatted table of collected import statements.

        Shows a summary of all collected user-defined Python modules. If imports
        are not yet collected, calls `self.collect()` automatically. The output
        is rendered as a table inside a styled panel in the console, listing each
        module's name, relative file path, and defined symbols.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method outputs the formatted table to the console and does not
            return any value.
        """
        # Collect imports if not already done
        if not self.imports:
            self.collect()

        # Import Rich components for console output
        from rich.console import Console
        from rich.table import Table
        from rich.box import MINIMAL
        from rich.panel import Panel

        # Create a console instance for output
        console = Console()

        # Set table width to 75% of console width
        width = int(console.size.width * 0.75)

        # Create a table with minimal box style and custom formatting
        table = Table(
            box=MINIMAL,
            show_header=True,
            show_edge=False,
            pad_edge=False,
            min_width=width,
            padding=(0, 1),
            collapse_padding=True,
        )

        # Add columns for module name, file path, and symbols
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("File", style="white")
        table.add_column("Symbols", style="magenta")

        # Populate the table with sorted import data
        for imp in sorted(self.imports, key=lambda x: x["name"].lower()):
            symbols_str = ", ".join(imp["symbols"])
            table.add_row(imp["name"], imp["file"], symbols_str)

        # Render the table inside a styled panel in the console
        console.print(
            Panel(
                table,
                title=(
                    "[bold blue]🔎 Loaded Python Modules "
                    "(Orionis Imports Trace)[/bold blue]"
                ),
                border_style="blue",
                width=width,
            ),
        )

    def clear(self) -> None:
        """
        Clear all entries from the collected imports list.

        Removes all items from the `imports` attribute, resetting its state.

        Returns
        -------
        None
            This method does not return any value. The `imports` list is emptied.
        """
        # Reset the imports list to an empty state
        self.imports.clear()
