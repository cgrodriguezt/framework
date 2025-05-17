from orionis.luminate.test.cases.test_async import AsyncTestCase
from orionis.luminate.test.cases.test_case import TestCase
from orionis.luminate.test.cases.test_sync import SyncTestCase
from orionis.luminate.test.enums.test_mode import ExecutionMode
from orionis.luminate.test.exceptions.test_failure_exception import OrionisTestFailureException
from orionis.luminate.test.suites.test_suite import Configuration, TestSuite
from orionis.luminate.test.suites.test_unit import UnitTest

def trace_imports():
    """
    Logs the start of the Orionis Framework import tracking process.

    This function outputs a formatted header to the console indicating the beginning of import tracking,
    then imports the `orionis.luminate.test.importscan` module to initiate the import scanning process.

    Side Effects:
        - Writes formatted informational text to the console.
        - Imports the `orionis.luminate.test.importscan` module.

    Dependencies:
        - orionis.luminate.console.output.console.Console
        - orionis.luminate.test.importscan
    """
    from orionis.luminate.console.output.console import Console
    Console.newLine()
    Console.textInfoBold("---------- ⭐ Orionis Framework Import Tracker ----------")
    import orionis.luminate.test.importscan

__all__ = [
    "AsyncTestCase",
    "Configuration",
    "ExecutionMode",
    "OrionisTestFailureException",
    "SyncTestCase",
    "TestCase",
    "TestSuite",
    "UnitTest",
    "trace_imports"
]