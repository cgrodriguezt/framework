from app import app
from orionis.support.facades.console import Console
from orionis.test.contracts.kernel import ITestKernel
from orionis.test.exceptions import OrionisTestFailureException

if __name__ == "__main__":
    """
    Orionis Test Runner

    Entry point for executing the Orionis test suite.
    Provides a command-line interface to configure and run tests.
    """

    # Resolve the test kernel instance from the application container
    kernel: ITestKernel = app.make(ITestKernel)

    try:

        # Execute the test suite using the kernel's handle method
        kernel.handle()

        # Exit with a success message if all tests pass
        Console.exitSuccess("All tests passed successfully.")

    except OrionisTestFailureException as e:

        # Handle test failures and exit with an error message
        Console.exitError(f"Test execution failed: {e}")

    except Exception as e:

        # Handle unexpected errors and exit with a generic error message
        Console.exitError(f"An unexpected error occurred: {e}")