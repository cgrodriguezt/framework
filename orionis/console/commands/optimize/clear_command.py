import shutil
from orionis.console.base.command import BaseCommand
from orionis.console.output.console import Console
from orionis.foundation.contracts.application import IApplication
import contextlib

class OptimizeClearCommand(BaseCommand):

    # ruff: noqa: TC001 (DI)

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "optimize:clear"

    # Command description
    description: str = "Clears the cache for the Orionis application."

    def handle(
        self,
        app: IApplication,
        console: Console,
    ) -> None:
        """
        Clear Python bytecode, framework cache directories, and build artifacts.

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
                with contextlib.suppress(OSError):
                    path.unlink()

        # Remove build artifact directories if they exist
        for artifact_dir in ["build", "dist", "orionis.egg-info"]:
            artifact_path = app.path("root") / artifact_dir
            if artifact_path.exists() and artifact_path.is_dir():
                shutil.rmtree(artifact_path, ignore_errors=True)

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
