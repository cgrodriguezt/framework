from orionis.luminate.test.cases.test_async import AsyncTestCase
from orionis.luminate.test.cases.test_case import TestCase
from orionis.luminate.test.cases.test_sync import SyncTestCase
from orionis.luminate.test.core.test_suite import TestSuite
from orionis.luminate.test.core.test_unit import UnitTest

__all__ = [
    "TestSuite",
    "UnitTest",
    "AsyncTestCase",
    "TestCase",
    "SyncTestCase",
]
__author__ = "Raúl Mauricio Uñate Castro"
__description__ = (
    "Orionis Framework - Component Test Suites is a microframework "
    "for creating unit and integration tests. "
    "It allows you to write tests quickly and easily, "
    "using a clear and concise syntax. "
    "Supports both asynchronous and synchronous tests, "
    "as well as the creation of test suites and parallel test execution. "
    "It uses Python's native unittest module for test creation."
)