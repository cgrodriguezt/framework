from main import app
from orionis.test.contracts.kernel import ITestKernel

if __name__ == "__main__":
    """
    Runs the Orionis test suite from the command line.

    Initializes the test kernel using the application container, executes all registered tests,
    and manages process exit based on the test results.

    Returns
    -------
    None

    Raises
    ------
    OrionisTestFailureException
        If one or more tests fail during execution.
    Exception
        If an unexpected error occurs during test execution.
    """

    # Resolve the test kernel instance from the application container
    kernel: ITestKernel = app.make(ITestKernel)

    # Execute the test suite using the kernel's handle method
    kernel.handle()