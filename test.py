from orionis.luminate.config.entities.testing import Testing
from orionis.luminate.console.output.console import Console
from orionis.luminate.test import TestSuite
from orionis.luminate.test.enums.test_mode import ExecutionMode

if __name__ == "__main__":
    """
    Entry point for executing Orionis tests.

    Runs the test suite, checks results, and exits with:
    - 0 if all tests pass.
    - 1 if any test fails or errors.

    Usage:
        $ python -B test.py
    """

    try:
        TestSuite.config(Testing(
            verbosity = 2,
            execution_mode = ExecutionMode.PARALLEL,
            max_workers = 1,
            fail_fast = False,
            print_result = True,
            throw_exception = True,
            base_path = 'tests',
            folder_path = [
                'config'
            ],
            pattern = 'test_*.py'
        )).run()
        Console.exitSuccess()
    except Exception as e:
        Console.exitError(message=str(e))