import subprocess
import sys
from orionis.console.base.command import BaseCommand
from orionis.console.exceptions import CLIOrionisRuntimeError

class CacheClearCommand(BaseCommand):

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "cache:clear"

    # Command description
    description: str = "Clears the cache for the Orionis application."

    def handle(self) -> bool:
        """
        Clear `.pyc` files and `__pycache__` folders in the current directory.

        Execute `pyclean .` to remove Python bytecode caches.

        Returns
        -------
        bool
            Returns True if cache is cleared successfully. Raises an exception
            otherwise.

        Raises
        ------
        CLIOrionisRuntimeError
            Raised if an error occurs during cache clearing.
        """
        try:

            # Run the 'pyclean' command to clear cache files in the current directory
            process = subprocess.run(  # noqa: S603
                [sys.executable, "-m", "pyclean", "."],
                check=False,
                capture_output=True,
                text=True,
                shell=False,
            )

            # Check if the command executed successfully
            if process.returncode != 0:

                # Extract the error message if the command failed
                error_msg = process.stderr.strip() or "Unknown error occurred."
                final_error_msg = (
                    f"Cache clearing failed with exit code {process.returncode}: "
                    f"{error_msg}"
                )
                error_msg = final_error_msg
                raise CLIOrionisRuntimeError(error_msg)

            # Return True if the command was successful
            return True

        except Exception as e:

            # Assign the error message before raising the exception
            error_msg = (
                f"An unexpected error occurred during cache clearing: {e!s}"
            )
            raise CLIOrionisRuntimeError(error_msg) from e
