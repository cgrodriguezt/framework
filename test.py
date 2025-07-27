# Clear the storage directory before running tests
import shutil
shutil.rmtree("./storage", ignore_errors=True)

# Import necessary modules and classes
import os
from app import app
from orionis.support.facades.console import Console
from orionis.test.contracts.kernel import ITestKernel
from orionis.test.exceptions import OrionisTestFailureException

if __name__ == "__main__":
    """
    Orionis Test Runner

    Entry point for executing the Orionis test suite via the command line interface.
    This function initializes the test kernel from the application container, executes the test suite,
    and handles the outcome by displaying appropriate messages and exiting the process.

    Parameters
    ----------
    None

    Returns
    -------
    None
        This function does not return any value. The process exits with a success or error code
        depending on the test results.

    Raises
    ------
    OrionisTestFailureException
        Raised when one or more tests fail during execution.
    Exception
        Raised for any unexpected errors encountered during test execution.
    """

    # Resolve the test kernel instance from the application container
    kernel: ITestKernel = app.make(ITestKernel)

    try:

        # Execute the test suite using the kernel's handle method
        kernel.handle()

        # Delete .env files after tests.
        os.remove(".env")

        # Exit with a success message if all tests pass
        Console.exitSuccess()

    except OrionisTestFailureException as e:

        # Handle test failures and exit with an error message
        Console.exitError(f"Test execution failed: {e}")

    except Exception as e:

        # Handle unexpected errors and exit with a generic error message
        Console.exitError(f"An unexpected error occurred: {e}")