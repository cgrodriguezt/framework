import subprocess
import sys
from orionis.console.base.command import BaseCommand

class CacheClearCommand(BaseCommand):

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "cache:clear"

    # Command description
    description: str = "Clears the cache for the Orionis application."

    def handle(self) -> bool:
        """
        Clear Python bytecode cache files and folders in the current directory.

        Run the `pyclean .` command to remove `.pyc` files and `__pycache__`
        directories. Raise RuntimeError if the command fails.

        Returns
        -------
        bool
            True if cache is cleared successfully, otherwise raises RuntimeError.
        """
        # Run the 'pyclean' command to clear cache files in the current directory
        process = subprocess.run(
            [sys.executable, "-m", "pyclean", "."],
            check=False,
            capture_output=True,
            text=True,
            shell=False,
        )

        # Check if the command executed successfully
        if process.returncode != 0:

            # Extract and format the error message if the command failed
            error_msg = process.stderr.strip() or "Unknown error occurred."
            final_error_msg = (
                f"Cache clearing failed with exit code {process.returncode}: "
                f"{error_msg}"
            )
            error_msg = final_error_msg
            raise RuntimeError(error_msg)

        # Return True if the command was successful
        return True