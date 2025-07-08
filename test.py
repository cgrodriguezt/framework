import sys
from app import app
from orionis.support.facades.console import Console
from orionis.test.contracts.kernel import ITestKernel
from orionis.test.exceptions import OrionisTestFailureException

if __name__ == "__main__":
    """
    Orionis Test Runner

    This script serves as the entry point for executing the Orionis test suite. It provides
    a command-line interface to configure and run tests with various options for verbosity,
    execution mode, reporting, and more.
    """

    # Resolve the test kernel and execute the tests with the provided configuration
    kernel:ITestKernel = app.make(ITestKernel)

    # Try to execute the test suite with the provided arguments
    try:

        # Create a configuration object with the parsed arguments
        kernel.handleCLI(sys.argv)

        # Exiting with success
        kernel.exit(0)

    except OrionisTestFailureException as e:

        # Handle specific test failures
        Console.exception(e)
        kernel.exit(1)

    except Exception as e:

        # Handle unexpected system errors
        Console.exception(e)
        kernel.exit(1)