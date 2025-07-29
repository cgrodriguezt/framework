from app import app
from orionis.test.contracts.kernel import ITestKernel

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

    # Execute the test suite using the kernel's handle method
    kernel.handle()