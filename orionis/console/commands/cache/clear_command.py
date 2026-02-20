import shutil
from pathlib import Path
from orionis.console.base.command import BaseCommand
from orionis.console.output.contracts.console import IConsole
from orionis.foundation.contracts.application import IApplication

class CacheClearCommand(BaseCommand):

    # ruff: noqa: S603

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "cache:clear"

    # Command description
    description: str = "Clears the cache for the Orionis application."

    def handle(
        self,
        app: IApplication,
        console: IConsole,
    ) -> None:
        """
        Clear Python bytecode and framework cache directories.

        Parameters
        ----------
        app : IApplication
            The application instance providing path resolution.
        console : IConsole
            The console instance for output.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Remove all __pycache__ directories and .pyc/.pyo files
        # in the current directory tree
        for path in app.path("root").rglob("*"):
            if path.is_dir() and path.name == "__pycache__":
                shutil.rmtree(path, ignore_errors=True)
            elif path.is_file() and path.suffix in {".pyc", ".pyo"}:
                try:
                    path.unlink()
                except OSError:
                    # Ignore errors when deleting files
                    pass

        # Remove the framework cache directory if it exists
        cache_path = app.path("storage") / "framework"
        if cache_path.exists():
            shutil.rmtree(cache_path)

        # Remove the logs directory if it exists
        cache_path = app.path("storage") / "logs"
        if cache_path.exists():
            shutil.rmtree(cache_path)

        # Recreate framework directory after clearing cache
        (app.path("storage") / "framework").mkdir(parents=True, exist_ok=True)

        # Notify the user of successful cache clearing
        console.success("Cache cleared successfully.")
