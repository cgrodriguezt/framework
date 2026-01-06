from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.testing.entities.testing import Testing
from orionis.foundation.config.testing.enums import (
    ExecutionMode,
    PersistentDrivers,
    VerbosityMode,
)

@dataclass(frozen=True, kw_only=True)
class BootstrapTesting(Testing):

    # --------------------------------------------------------------------------
    # verbosity : int | VerbosityMode, optional
    # --- Verbosity level for test output.
    # --- 0 = silent, 1 = minimal, 2 = detailed.
    # --------------------------------------------------------------------------
    verbosity: int | VerbosityMode = field(
        default=VerbosityMode.DETAILED.value,
    )

    # --------------------------------------------------------------------------
    # execution_mode : str | ExecutionMode, optional
    # --- Mode for test execution: 'sequential' or 'parallel'.
    # --- Controls how tests are run.
    # --------------------------------------------------------------------------
    execution_mode: str | ExecutionMode = field(
        default=ExecutionMode.SEQUENTIAL.value,
    )

    # --------------------------------------------------------------------------
    # max_workers : int, optional
    # --- Maximum number of workers for parallel execution.
    # --- Used only if execution_mode is 'parallel'.
    # --------------------------------------------------------------------------
    max_workers: int = field(
        default=1,
    )

    # --------------------------------------------------------------------------
    # fail_fast : bool, optional
    # --- If True, stops after the first test failure.
    # --- Useful for quick feedback.
    # --------------------------------------------------------------------------
    fail_fast: bool = field(
        default=False,
    )

    # --------------------------------------------------------------------------
    # throw_exception : bool, optional
    # --- If True, raises exception on test failure.
    # --- Otherwise, continues running tests.
    # --------------------------------------------------------------------------
    throw_exception: bool = field(
        default=False,
    )

    # --------------------------------------------------------------------------
    # folder_path : str | list, optional
    # --- Folder path pattern(s) to search for tests.
    # --- Accepts a string or a list of strings.
    # --------------------------------------------------------------------------
    folder_path: str | list = field(
        default="*",
    )

    # --------------------------------------------------------------------------
    # pattern : str, optional
    # --- Filename pattern to identify test files.
    # --- Example: 'test_*.py'.
    # --------------------------------------------------------------------------
    pattern: str = field(
        default="test_*.py",
    )

    # --------------------------------------------------------------------------
    # test_name_pattern : str | None, optional
    # --- Pattern to match specific test names.
    # --- If None, all tests are included.
    # --------------------------------------------------------------------------
    test_name_pattern: str | None = field(
        default=None,
    )

    # --------------------------------------------------------------------------
    # persistent : bool, optional
    # --- If True, test results are persisted.
    # --- Enables storing results for later use.
    # --------------------------------------------------------------------------
    persistent: bool = field(
        default=False,
    )

    # --------------------------------------------------------------------------
    # persistent_driver : str | PersistentDrivers, optional
    # --- Driver for persisting test results.
    # --- Supported: 'sqlite', 'json'.
    # --------------------------------------------------------------------------
    persistent_driver: str | PersistentDrivers = field(
        default=PersistentDrivers.JSON.value,
    )

    # --------------------------------------------------------------------------
    # web_report : bool, optional
    # --- If True, generates a web report for test results.
    # --- Useful for visualizing outcomes.
    # --------------------------------------------------------------------------
    web_report: bool = field(
        default=False,
    )
