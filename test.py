from orionis.console.output.console import Console
from orionis.services.system.workers import Workers
from orionis.unittesting import Configuration, ExecutionMode, OrionisTestFailureException,TestSuite
import argparse

if __name__ == "__main__":
    """
    Entry point for executing Orionis tests.

    Runs the test suite, checks results, and exits with:
    - 0 if all tests pass.
    - 1 if any test fails or errors.

    Usage:
        python -B test.py
    """
    parser = argparse.ArgumentParser(description="Run Orionis tests.")
    parser.add_argument('--mode', choices=['parallel', 'sequential'], default='parallel', help='Execution mode for tests')
    args = parser.parse_args()

    execution_mode = ExecutionMode.PARALLEL if args.mode == 'parallel' else ExecutionMode.SEQUENTIAL

    try:

        # Exceuting the test suite
        suite = TestSuite(
            Configuration(
                verbosity = 2,
                execution_mode = ExecutionMode.PARALLEL if args.mode == 'parallel' else ExecutionMode.SEQUENTIAL,
                max_workers = Workers(ram_per_worker=1).calculate(),
                fail_fast = False,
                print_result = True,
                throw_exception = False,
                base_path = 'tests',
                folder_path = [
                    'example',
                    'foundation',
                    'metadata',
                    'patterns',
                    'services',
                    'testing',
                ],
                pattern = 'test_*.py',
                persistent=False,
                persistent_driver=None,
                web_report=False
            )
        ).run()

        # Exiting with success
        Console.exitSuccess()

    except (OrionisTestFailureException, Exception) as e:

        # Exiting with error
        Console.exitError(message=str(e))