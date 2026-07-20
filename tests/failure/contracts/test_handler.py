from __future__ import annotations
import inspect
from orionis.failure.contracts.handler import IBaseExceptionHandler
from orionis.test import TestCase

class TestIBaseExceptionHandlerStructure(TestCase):

    def testToThrowableIsPresent(self) -> None:
        """
        Confirm that toThrowable is declared on IBaseExceptionHandler.

        Validates that the method exists in the class namespace so that
        subclasses are statically required to provide an implementation.
        """
        self.assertTrue(hasattr(IBaseExceptionHandler, "toThrowable"))

    def testIsExceptionIgnoredIsPresent(self) -> None:
        """
        Confirm that isExceptionIgnored is declared on IBaseExceptionHandler.

        Validates that the method exists in the class namespace so that
        subclasses are statically required to provide an implementation.
        """
        self.assertTrue(hasattr(IBaseExceptionHandler, "isExceptionIgnored"))

    def testReportIsPresent(self) -> None:
        """
        Confirm that report is declared on IBaseExceptionHandler.

        Validates that the method exists in the class namespace so that
        subclasses are statically required to provide an implementation.
        """
        self.assertTrue(hasattr(IBaseExceptionHandler, "report"))

    def testHandleCLIIsPresent(self) -> None:
        """
        Confirm that handleCLI is declared on IBaseExceptionHandler.

        Validates that the method exists in the class namespace so that
        subclasses are statically required to provide an implementation.
        """
        self.assertTrue(hasattr(IBaseExceptionHandler, "handleCLI"))

    def testHandleHTTPIsPresent(self) -> None:
        """
        Confirm that handleHTTP is declared on IBaseExceptionHandler.

        Validates that the method exists in the class namespace so that
        subclasses are statically required to provide an implementation.
        """
        self.assertTrue(hasattr(IBaseExceptionHandler, "handleHTTP"))

    def testToThrowableIsAbstract(self) -> None:
        """
        Verify that toThrowable is marked as an abstract method.

        Validates that the ABC infrastructure will force any concrete
        subclass to implement toThrowable before it can be instantiated.
        """
        method = getattr(IBaseExceptionHandler, "toThrowable", None)
        self.assertIsNotNone(method)
        self.assertTrue(getattr(method, "__isabstractmethod__", False))

    def testIsExceptionIgnoredIsAbstract(self) -> None:
        """
        Verify that isExceptionIgnored is marked as an abstract method.

        Validates that the ABC infrastructure will force any concrete
        subclass to implement isExceptionIgnored before instantiation.
        """
        method = getattr(IBaseExceptionHandler, "isExceptionIgnored", None)
        self.assertIsNotNone(method)
        self.assertTrue(getattr(method, "__isabstractmethod__", False))

    def testReportIsAbstract(self) -> None:
        """
        Verify that report is marked as an abstract method.

        Validates that the ABC infrastructure will force any concrete
        subclass to implement report before it can be instantiated.
        """
        method = getattr(IBaseExceptionHandler, "report", None)
        self.assertIsNotNone(method)
        self.assertTrue(getattr(method, "__isabstractmethod__", False))

    def testHandleCLIIsAbstract(self) -> None:
        """
        Verify that handleCLI is marked as an abstract method.

        Validates that the ABC infrastructure will force any concrete
        subclass to implement handleCLI before it can be instantiated.
        """
        method = getattr(IBaseExceptionHandler, "handleCLI", None)
        self.assertIsNotNone(method)
        self.assertTrue(getattr(method, "__isabstractmethod__", False))

    def testHandleHTTPIsAbstract(self) -> None:
        """
        Verify that handleHTTP is marked as an abstract method.

        Validates that the ABC infrastructure will force any concrete
        subclass to implement handleHTTP before it can be instantiated.
        """
        method = getattr(IBaseExceptionHandler, "handleHTTP", None)
        self.assertIsNotNone(method)
        self.assertTrue(getattr(method, "__isabstractmethod__", False))

    def testExactlyFiveAbstractMethods(self) -> None:
        """
        Verify that IBaseExceptionHandler declares exactly five abstract methods.

        Validates that the interface surface area is stable and that no
        methods have been silently added or removed without updating
        consumers.
        """
        abstract_count = len(IBaseExceptionHandler.__abstractmethods__)
        self.assertEqual(abstract_count, 5)

class TestIBaseExceptionHandlerSubclassing(TestCase):

    def testConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Instantiate a minimal concrete subclass without error.

        Validates that a class providing all five required methods
        satisfies the interface and can be created normally.
        """

        class _Concrete(IBaseExceptionHandler):
            def toThrowable(self, _exception):
                return None

            def isExceptionIgnored(self, _exception):
                return False

            async def report(self, _exception, _log):
                return None

            async def handleCLI(self, _exception, _console):
                return None

            async def handleHTTP(self, _exception, _request):
                return None

        instance = _Concrete()
        self.assertIsInstance(instance, IBaseExceptionHandler)

    def testIncompleteSubclassRaisesTypeError(self) -> None:
        """
        Raise TypeError when a subclass omits required abstract methods.

        Validates that the ABC machinery prevents instantiation of any
        class that does not implement every declared abstract method.
        """

        class _Incomplete(IBaseExceptionHandler):
            def toThrowable(self, _exception):
                return None

        with self.assertRaises(TypeError):
            _Incomplete()  # type: ignore[abstract]

    def testIsCoroutineReport(self) -> None:
        """
        Confirm that report is declared as a coroutine function.

        Validates that callers can safely await report without wrapping
        it in an additional async shim.
        """
        self.assertTrue(inspect.iscoroutinefunction(IBaseExceptionHandler.report))

    def testIsCoroutineHandleCLI(self) -> None:
        """
        Confirm that handleCLI is declared as a coroutine function.

        Validates that callers can safely await handleCLI without
        wrapping it in an additional async shim.
        """
        self.assertTrue(inspect.iscoroutinefunction(IBaseExceptionHandler.handleCLI))

    def testIsCoroutineHandleHTTP(self) -> None:
        """
        Confirm that handleHTTP is declared as a coroutine function.

        Validates that callers can safely await handleHTTP without
        wrapping it in an additional async shim.
        """
        self.assertTrue(
            inspect.iscoroutinefunction(IBaseExceptionHandler.handleHTTP),
        )
