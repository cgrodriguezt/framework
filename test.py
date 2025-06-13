from orionis.console.output.console import Console
from orionis.services.system.workers import Workers
from orionis.unittesting import Configuration, ExecutionMode, OrionisTestFailureException, TestSuite
import argparse

if __name__ == "__main__":
    """
    Orionis Test Runner

    This script serves as the entry point for executing the Orionis test suite. It provides
    a command-line interface to configure and run tests with various options for verbosity,
    execution mode, reporting, and more.

    Parameters
    ----------
    --verbosity : int, optional
        Verbosity level of test output (default: 2).
    --mode : {'parallel', 'sequential'}, optional
        Execution mode for running tests (default: 'parallel').
    --fail_fast, --no_fail_fast : bool, optional
        Stop on first failure if set (default: False).
    --print_result, --no_print_result : bool, optional
        Print test results to console if set (default: True).
    --throw_exception, --no_throw_exception : bool, optional
        Throw exception on test failure if set (default: False).
    --persistent, --no_persistent : bool, optional
        Run tests in persistent mode if set (default: False).
    --persistent_driver : str, optional
        Persistent driver to use (default: None).
    --web_report, --no_web_report : bool, optional
        Generate web report if set (default: False).
    --github, --no_github : bool, optional
        Run tests in GitHub Actions mode if set (default: False).

    Returns
    -------
    None

    Exits
    -----
    0 : int
        If all tests pass.
    1 : int
        If any test fails or an error occurs.

    Examples
    --------
    Run all tests with default settings:

        $ python -B test.py

    Run tests sequentially with high verbosity:

        $ python -B test.py --mode sequential --verbosity 3

    Stop on first failure and generate a web report:

        $ python -B test.py --fail_fast --web_report

    Notes
    -----
    - Test discovery is performed in the 'tests' directory, searching for files matching 'test_*.py'
      within the specified subfolders.
    - Designed for use both locally and in CI environments (e.g., GitHub Actions).
    """
    parser = argparse.ArgumentParser(description="Run Orionis tests.")
    parser.add_argument('--verbosity', type=int, default=2, help='Verbosity level (default: 2)')
    parser.add_argument('--mode', choices=['parallel', 'sequential'], default='parallel', help='Execution mode for tests (default: parallel)')

    parser.add_argument('--fail_fast', dest='fail_fast', action='store_true', help='Stop on first failure')
    parser.add_argument('--no_fail_fast', dest='fail_fast', action='store_false', help='Do not stop on first failure (default)')
    parser.set_defaults(fail_fast=False)

    parser.add_argument('--print_result', dest='print_result', action='store_true', help='Print test results to console (default)')
    parser.add_argument('--no_print_result', dest='print_result', action='store_false', help='Do not print test results to console')
    parser.set_defaults(print_result=True)

    parser.add_argument('--throw_exception', dest='throw_exception', action='store_true', help='Throw exception on test failure')
    parser.add_argument('--no_throw_exception', dest='throw_exception', action='store_false', help='Do not throw exception on test failure (default)')
    parser.set_defaults(throw_exception=False)

    parser.add_argument('--persistent', dest='persistent', action='store_true', help='Run tests in persistent mode')
    parser.add_argument('--no_persistent', dest='persistent', action='store_false', help='Do not run tests in persistent mode (default)')
    parser.set_defaults(persistent=False)

    parser.add_argument('--persistent_driver', type=str, default=None, help='Persistent driver to use (default: None)')

    parser.add_argument('--web_report', dest='web_report', action='store_true', help='Generate web report')
    parser.add_argument('--no_web_report', dest='web_report', action='store_false', help='Do not generate web report (default)')
    parser.set_defaults(web_report=False)

    parser.add_argument('--print_output_buffer', dest='print_output_buffer', action='store_true', help='Print output buffer (for CI integrations)')
    parser.add_argument('--no_print_output_buffer', dest='print_output_buffer', action='store_false', help='Do not print output buffer (default)')
    parser.set_defaults(print_output_buffer=False)

    args = parser.parse_args()

    try:
        # Executing the test suite
        suite = TestSuite(
            Configuration(
                verbosity = int(args.verbosity),
                execution_mode = ExecutionMode.PARALLEL if args.mode == 'parallel' else ExecutionMode.SEQUENTIAL,
                max_workers = Workers(ram_per_worker=1).calculate(),
                fail_fast = bool(args.fail_fast),
                print_result = bool(args.print_result),
                throw_exception = bool(args.throw_exception),
                base_path = 'tests',
                folder_path = [
                    'example',
                    'foundation',
                    'metadata',
                    'patterns',
                    'services',
                    'support',
                    'testing',
                ],
                pattern = 'test_*.py',
                persistent = bool(args.persistent),
                persistent_driver = str(args.persistent_driver) if args.persistent_driver else None,
                web_report = bool(args.web_report)
            )
        ).run()

        # If requested, print the output buffer
        if args.print_output_buffer:
            suite.printOutputBuffer()

        # Exiting with success
        Console.exitSuccess()

    except (OrionisTestFailureException, Exception) as e:

        # Exiting with error
        Console.exitError(message=str(e))