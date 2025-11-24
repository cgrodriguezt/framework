from dataclasses import dataclass
from orionis.foundation.config.testing.entities.testing import Testing
from orionis.foundation.config.testing.enums import ExecutionMode, PersistentDrivers, VerbosityMode

@dataclass
class BootstrapTesting(Testing):

    # -------------------------------------------------------------------------
    # verbosity : int | VerbosityMode
    #    - Verbosity level for test output.
    #    - 0 = silent, 1 = minimal, 2 = detailed.
    #    - Defaults to 2 (detailed output).
    # -------------------------------------------------------------------------
    verbosity = VerbosityMode.DETAILED

    # -------------------------------------------------------------------------
    # execution_mode : str | ExecutionMode
    #    - Mode of test execution: 'sequential' or 'parallel'.
    #    - Defaults to 'sequential'.
    # -------------------------------------------------------------------------
    execution_mode = ExecutionMode.SEQUENTIAL

    # -------------------------------------------------------------------------
    # max_workers : int
    #    - Maximum number of worker threads/processes for parallel execution.
    #    - Defaults to 1.
    # -------------------------------------------------------------------------
    max_workers = 1

    # -------------------------------------------------------------------------
    # fail_fast : bool
    #    - If True, stops execution after the first test failure.
    #    - Defaults to False.
    # -------------------------------------------------------------------------
    fail_fast = False

    # -------------------------------------------------------------------------
    # throw_exception : bool
    #    - If True, raises an exception if a test fails.
    #    - Defaults to False.
    # -------------------------------------------------------------------------
    throw_exception = True

    # -------------------------------------------------------------------------
    # folder_path : str | list
    #    - The folder path pattern to search for tests.
    #    - Can be a single path or a list of paths.
    #    - Defaults to '*', meaning all folders in the base path.
    # -------------------------------------------------------------------------
    folder_path = '*'

    # -------------------------------------------------------------------------
    # test_pattern : str
    #    - The filename pattern to identify test files.
    #    - Defaults to 'test_*.py'.
    # -------------------------------------------------------------------------
    pattern = 'test_*.py'

    # -------------------------------------------------------------------------
    # test_name_pattern : str | None
    #    - A pattern to match specific test names.
    #    - If None, all tests are considered.
    #    - Defaults to None.
    # -------------------------------------------------------------------------
    test_name_pattern = None

    # -------------------------------------------------------------------------
    # persistent : bool
    #    - If True, keeps the test results persistent.
    #    - Defaults to False.
    # -------------------------------------------------------------------------
    persistent = False

    # -------------------------------------------------------------------------
    # persistent_driver : str | PersistentDrivers
    #    - Specifies the driver to use for persisting test results.
    #    - Supported values: 'sqlite', 'json'.
    #    - Defaults to 'json'.
    # -------------------------------------------------------------------------
    persistent_driver = PersistentDrivers.JSON

    # -------------------------------------------------------------------------
    # web_report : bool
    #    - If True, generates a web report for the test results.
    #    - Defaults to False.
    # -------------------------------------------------------------------------
    web_report = False
