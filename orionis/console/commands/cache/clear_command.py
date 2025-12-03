import subprocess
import sys
from orionis.console.base.command import BaseCommand
from orionis.console.exceptions import CLIOrionisRuntimeError, CLIOrionisException

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

        Executes the `pyclean .` command to remove `.pyc` files and `__pycache__`
        directories. Returns True if the cache is cleared successfully. Raises
        CLIOrionisRuntimeError or CLIOrionisException if an error occurs.

        Returns
        -------
        bool
            True if cache is cleared successfully.

        Raises
        ------
        CLIOrionisRuntimeError
            If an error occurs during cache clearing.
        CLIOrionisException
            If an unexpected exception occurs.
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
                raise RuntimeError(error_msg)

            # Return True if the command was successful
            return True

        except RuntimeError as e:

            # Assign the error message before raising the exception

            error_msg = (
                f"An unexpected error occurred during cache clearing: {e!s}"
            )
            raise CLIOrionisRuntimeError(error_msg) from e

        except Exception as e:

            # Handle any other exceptions that may occur
            error_msg = f"An unexpected error occurred: {e!s}"
            raise CLIOrionisException(error_msg) from e
