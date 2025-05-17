from orionis.luminate.console.output.console import Console
from orionis.luminate.services.system.workers import Workers
from orionis.unittesting import TestSuite, Configuration, ExecutionMode, OrionisTestFailureException, trace_imports

if __name__ == "__main__":
    """
    Entry point for executing Orionis tests.

    Runs the test suite, checks results, and exits with:
    - 0 if all tests pass.
    - 1 if any test fails or errors.

    Usage:
        python -B test.py
    """
    trace_imports()

    try:
        TestSuite(
            Configuration(
                verbosity = 2,
                execution_mode = ExecutionMode.PARALLEL,
                max_workers = Workers(ram_per_worker=1).calculate(),
                fail_fast = False,
                print_result = True,
                throw_exception = True,
                base_path = 'tests',
                folder_path = [
                    'config',
                    'example',
                    'patterns'
                ],
                pattern = 'test_*.py'
            )
        ).run()
        Console.exitSuccess()
    except (OrionisTestFailureException, Exception) as e:
        Console.exitError(message=str(e))