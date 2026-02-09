import os
import shutil
import subprocess
import sys
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
        Clear Python bytecode cache files and framework cache directories.

        This method removes `.pyc` files and `__pycache__` directories in the
        current directory using the `pyclean` module. It also deletes the
        application framework cache and logs directories if they exist.

        Parameters
        ----------
        app : IApplication
            The application instance providing access to application paths.
        console : IConsole
            The console instance used for output.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Run the 'pyclean' command to clear Python bytecode cache files
        process = subprocess.run(
            [sys.executable, "-m", "pyclean", "."],
            check=False,
            capture_output=True,
            text=True,
            shell=False,
            env=os.environ,
        )

        # Raise an error if the pyclean command fails
        if process.returncode != 0:
            error_msg = process.stderr.strip() or "Unknown error occurred."
            final_error_msg = (
                f"Cache clearing failed with exit code {process.returncode}: "
                f"{error_msg}"
            )
            error_msg = final_error_msg
            raise RuntimeError(error_msg)

        # Remove the framework cache directory if it exists
        cache_path = app.path("storage") / "framework"
        if cache_path.exists():
            shutil.rmtree(cache_path)

        # Remove the logs directory if it exists
        cache_path = app.path("storage") / "logs"
        if cache_path.exists():
            shutil.rmtree(cache_path)

        # Notify the user of successful cache clearing
        console.success("Cache cleared successfully.")
