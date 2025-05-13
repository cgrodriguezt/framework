from dataclasses import dataclass
from typing import Any, Optional
from orionis.luminate.test.enums.test_status import TestStatus

@dataclass(frozen=True, kw_only=True)
class TestResult:
    """
    Represents the result of a test execution.

    Attributes:
        id (Any): Unique identifier for the test result.
        name (str): Name of the test.
        status (TestStatus): Status of the test execution (e.g., passed, failed).
        execution_time (float): Time taken to execute the test, in seconds.
        error_message (Optional[str]): Error message if the test failed, otherwise None.
        traceback (Optional[str]): Traceback information if an error occurred, otherwise None.
        class_name (Optional[str]): Name of the class containing the test, if applicable.
        method (Optional[str]): Name of the method representing the test, if applicable.
        module (Optional[str]): Name of the module containing the test, if applicable.
        file_path (Optional[str]): Path to the file containing the test, if applicable.
    """
    id: Any
    name: str
    status: TestStatus
    execution_time: float
    error_message: Optional[str] = None
    traceback: Optional[str] = None
    class_name : Optional[str] = None
    method : Optional[str] = None
    module : Optional[str] = None
    file_path: Optional[str] = None
