from app import app
from orionis.test.arguments.parser import cli_test_args
from orionis.test.contracts.kernel import ITestKernel
from orionis.test.enums import ExecutionMode
from orionis.test.exceptions import OrionisTestFailureException

if __name__ == "__main__":
    """
    Orionis Test Runner

    This script serves as the entry point for executing the Orionis test suite. It provides
    a command-line interface to configure and run tests with various options for verbosity,
    execution mode, reporting, and more.
    """

    # Parse command line arguments using the dedicated parser module
    args = cli_test_args()

    # Resolve the test kernel and execute the tests with the provided configuration
    kernel:ITestKernel = app.make(ITestKernel)

    # Try to execute the test suite with the provided arguments
    try:

        # Create a configuration object with the parsed arguments
        test = kernel.handle(
            verbosity = int(args.verbosity),
            execution_mode = ExecutionMode.PARALLEL if args.mode == 'parallel' else ExecutionMode.SEQUENTIAL,
            fail_fast = bool(args.fail_fast),
            print_result = bool(args.print_result),
            throw_exception = bool(args.throw_exception),
            base_path = 'tests',
            folder_path = [
                'example'
            ],
            pattern = 'test_*.py',
            persistent = bool(args.persistent),
            persistent_driver = str(args.persistent_driver) if args.persistent_driver else None,
            web_report = bool(args.web_report)
        )

        # If requested, print the output buffer
        if args.print_output_buffer:
            test.printOutputBuffer()

        # Exiting with success
        kernel.exit(0)

    except (OrionisTestFailureException, Exception) as e:

        # Handle test failures or other exceptions with proper error reporting
        error_message = f"Test execution failed: {str(e)}"
        print(f"\n\033[91mERROR: {error_message}\033[0m")
        if hasattr(e, 'traceback') and e.traceback:
            print(e.traceback)

        # Exit with an error code
        kernel.exit(1)