from dataclasses import dataclass
from typing import Any, List

@dataclass(frozen=True, kw_only=True)
class Testing:
    """
    Testing is a dataclass that holds configuration options for running tests.

    Attributes:
        verbosity (int): The verbosity level of the test output. Default is 2.
            - 0: Silent
            - 1: Minimal output
            - 2: Detailed output (default)
        execution_mode (ExecutionMode): The mode of test execution. Default is ExecutionMode.SEQUENTIAL.
            - ExecutionMode.SEQUENTIAL: Tests are executed one after another.
            - ExecutionMode.PARALLEL: Tests are executed in parallel.
        max_workers (int): The maximum number of worker threads/processes to use when running tests in parallel. Default is 4.
        fail_fast (bool): Whether to stop execution after the first test failure. Default is False.
        print_result (bool): Whether to print the test results to the console. Default is True.
        throw_exception (bool): Whether to throw an exception if a test fails. Default is False.
        base_path (str): The base directory where tests are located. Default is 'tests'.
        folder_path (str): The folder path pattern to search for tests. Default is '*'.
        pattern (str): The filename pattern to identify test files. Default is 'test_*.py'.
        test_name_pattern (str | None): A pattern to match specific test names. Default is None.
        tags (List[str] | None): A list of tags to filter tests. Default is None.
    """
    verbosity: int = 2
    execution_mode : Any = None
    max_workers: int = 4
    fail_fast: bool = False
    print_result: bool = True
    throw_exception: bool = False
    base_path: str = 'tests'
    folder_path: str = '*'
    pattern: str = 'test_*.py'
    test_name_pattern: str | None = None
    tags: List[str] | None = None

    def __post_init__(self):
        from orionis.luminate.test.enums.test_mode import ExecutionMode
        if not isinstance(self.execution_mode, ExecutionMode):
            object.__setattr__(self, 'execution_mode', ExecutionMode.SEQUENTIAL)
        if self.tags is None:
            object.__setattr__(self, 'tags', [])