from orionis.console.output.console import Console
from orionis.services.system.workers import Workers
from orionis.unittesting import Configuration, ExecutionMode, OrionisTestFailureException,TestSuite

if __name__ == "__main__":
    """
    Entry point for executing Orionis tests.

    Runs the test suite, checks results, and exits with:
    - 0 if all tests pass.
    - 1 if any test fails or errors.

    Usage:
        python -B test.py
    """

    try:

        # Exceuting the test suite
        suite = TestSuite(
            Configuration(
                verbosity = 2,
                execution_mode = ExecutionMode.PARALLEL,
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
                persistent=True,
                persistent_driver='json'
            )
        ).run()

        # Exiting with success
        Console.exitSuccess()

    except (OrionisTestFailureException, Exception) as e:

        # Exiting with error
        Console.exitError(message=str(e))