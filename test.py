import sys
from orionis.luminate.console.output.console import Console
from orionis.luminate.test.test_suite import Tests

def orionis_tests(print_result:bool=True, throw_exception:bool=False):
    """
    Execute the tests in the specified folders with the given pattern
    and print the results. If an exception occurs, it will not be thrown.
    """

    # Define the test folders and their configurations
    # Each dictionary must contain:
    # - folder_path : str : Path to the folder containing test files
    # - base_path : str : Base path for the tests
    # - pattern : str : File pattern to match test files
    paths = [
        {'base_path': 'tests', 'folder_path': 'example', 'pattern': 'test_*.py'},
        {'base_path': 'tests', 'folder_path': 'support/inspection', 'pattern': 'test_*.py'},
        {'base_path': 'tests', 'folder_path': 'support/parsers', 'pattern': 'test_*.py'},
        {'base_path': 'tests', 'folder_path': 'support/standard', 'pattern': 'test_*.py'},
        {'base_path': 'tests', 'folder_path': 'support/adapters', 'pattern': 'test_*.py'},
        {'base_path': 'tests', 'folder_path': 'support/async_io', 'pattern': 'test_*.py'},
        {'base_path': 'tests', 'folder_path': 'support/patterns', 'pattern': 'test_*.py'},
        {'base_path': 'tests', 'folder_path': 'support/path', 'pattern': 'test_*.py'},
        {'base_path': 'tests', 'folder_path': 'support/environment', 'pattern': 'test_*.py'},
    ]

    # Execute the tests and return the results
    return Tests.execute(paths, print_result, throw_exception)

if __name__ == "__main__":
    """
    Main script entry point for executing Orionis tests.

    This block runs the `orionis_tests` function and evaluates the results to
    determine whether to exit with a success or failure code. It is intended to be
    used when the script is executed directly.

    Execution flow:
    - Runs the Orionis test suite using `orionis_tests`.
    - Checks if any tests failed or encountered errors.
    - Exits with status code 1 if there are failed or errored tests, or 0 otherwise.

    Examples
    --------
    Run the test suite from the command line:

        $ python -B test.py

    Returns
    -------
    None
        The function does not return any value, but the process exits with
        a status code:
            - 0 : all tests passed
            - 1 : at least one test failed or had errors
    """

    # Print the header for the test suite
    Console.newLine()
    Console.textSuccessBold("Orionis Framework - Test Suite")

    # Execute the tests and get the results
    # The print_result parameter controls whether to print the results
    results = orionis_tests()

    # Check if any tests failed or encountered errors
    if results["failed"] > 0 or results["errors"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)