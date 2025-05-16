from orionis import Orionis
from orionis.luminate.console.dumper.dump_die import Debug
from orionis.luminate.console.output.console import Console
from orionis.luminate.config.testing.entities.testing import Testing
from orionis.luminate.services.system.workers import Workers
from orionis.luminate.test.enums.test_mode import ExecutionMode
from orionis.luminate.test.exceptions.test_exception import OrionisTestFailureException
from orionis.luminate.test.suites.test_suite import TestSuite

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
            max_workers = Workers(ram_per_worker=1).calculate(),
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
    except (OrionisTestFailureException, Exception) as e:
        Console.exitError(message=str(e))