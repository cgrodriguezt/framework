from __future__ import annotations
import inspect
from unittest.mock import MagicMock, patch
from orionis.console.output.contracts.http_request import IHTTPRequestPrinter
from orionis.console.output.http_request import HTTPRequestPrinter
from orionis.test import TestCase

class TestIHTTPRequestPrinterContract(TestCase):

    # ------------------------------------------------------------------ #
    #  Abstract class characteristics                                    #
    # ------------------------------------------------------------------ #

    def testIsAbstractClass(self) -> None:
        """
        Verify that IHTTPRequestPrinter is recognised as an abstract class.

        Ensures the interface defines at least one abstract method so it
        cannot be instantiated directly.
        """
        self.assertTrue(inspect.isabstract(IHTTPRequestPrinter))

    def testCannotBeInstantiatedDirectly(self) -> None:
        """
        Ensure that IHTTPRequestPrinter cannot be instantiated directly.

        Verifies that attempting to create an instance raises TypeError
        due to unimplemented abstract methods.
        """
        with self.assertRaises(TypeError):
            IHTTPRequestPrinter()  # type: ignore[abstract]

    # ------------------------------------------------------------------ #
    #  Abstract methods presence                                         #
    # ------------------------------------------------------------------ #

    def testAbstractMethodsAreDefined(self) -> None:
        """
        Verify that IHTTPRequestPrinter declares printRequest as abstract.

        Ensures the single public capability is listed in
        __abstractmethods__ so every concrete subclass is forced to
        provide an implementation.
        """
        self.assertIn("printRequest", IHTTPRequestPrinter.__abstractmethods__)

    def testHasExactlyOneAbstractMethod(self) -> None:
        """
        Verify that IHTTPRequestPrinter declares exactly one abstract method.

        Ensures the interface surface area is stable and no undocumented
        abstract methods have been added or removed silently.
        """
        self.assertEqual(len(IHTTPRequestPrinter.__abstractmethods__), 1)

    # ------------------------------------------------------------------ #
    #  printRequest signature                                            #
    # ------------------------------------------------------------------ #

    def testPrintRequestSignatureHasMethodParam(self) -> None:
        """
        Verify that printRequest declares a method parameter.

        Ensures the interface mandates the HTTP method as a required
        positional argument for all concrete implementations.
        """
        sig = inspect.signature(IHTTPRequestPrinter.printRequest)
        self.assertIn("method", sig.parameters)

    def testPrintRequestSignatureHasPathParam(self) -> None:
        """
        Verify that printRequest declares a path parameter.

        Ensures the interface mandates the request path as a required
        positional argument for all concrete implementations.
        """
        sig = inspect.signature(IHTTPRequestPrinter.printRequest)
        self.assertIn("path", sig.parameters)

    def testPrintRequestSignatureHasDurationParam(self) -> None:
        """
        Verify that printRequest declares a duration parameter.

        Ensures the interface mandates the request duration as a required
        positional argument for all concrete implementations.
        """
        sig = inspect.signature(IHTTPRequestPrinter.printRequest)
        self.assertIn("duration", sig.parameters)

    def testPrintRequestSignatureHasSuccessParam(self) -> None:
        """
        Verify that printRequest declares a success parameter.

        Ensures the interface allows callers to indicate whether the
        request succeeded or failed.
        """
        sig = inspect.signature(IHTTPRequestPrinter.printRequest)
        self.assertIn("success", sig.parameters)

    def testPrintRequestSuccessDefaultIsTrue(self) -> None:
        """
        Verify that the success parameter defaults to True.

        Ensures callers do not need to pass success explicitly for the
        common case of a successful request.
        """
        sig = inspect.signature(IHTTPRequestPrinter.printRequest)
        self.assertEqual(sig.parameters["success"].default, True)

    def testPrintRequestSignatureHasCodeParam(self) -> None:
        """
        Verify that printRequest declares a code parameter.

        Ensures the interface allows callers to supply the HTTP status
        code alongside the basic request information.
        """
        sig = inspect.signature(IHTTPRequestPrinter.printRequest)
        self.assertIn("code", sig.parameters)

    def testPrintRequestCodeDefaultIs200(self) -> None:
        """
        Verify that the code parameter defaults to 200.

        Ensures callers are not required to provide a status code for
        the most common successful HTTP response.
        """
        sig = inspect.signature(IHTTPRequestPrinter.printRequest)
        self.assertEqual(sig.parameters["code"].default, 200)

    # ------------------------------------------------------------------ #
    #  Concrete class conformance                                        #
    # ------------------------------------------------------------------ #

    def testHTTPRequestPrinterIsSubclassOfInterface(self) -> None:
        """
        Verify that HTTPRequestPrinter is a subclass of IHTTPRequestPrinter.

        Ensures the concrete implementation declares the interface as its
        base class, satisfying the Liskov Substitution Principle.
        """
        self.assertTrue(issubclass(HTTPRequestPrinter, IHTTPRequestPrinter))

    def testHTTPRequestPrinterCanBeInstantiated(self) -> None:
        """
        Verify that HTTPRequestPrinter can be instantiated without raising.

        Ensures the concrete class fully satisfies the abstract interface
        contract so object creation succeeds unconditionally.
        """
        with patch("orionis.console.output.http_request.Console") as MockConsole:
            mock_con = MagicMock()
            mock_con.size.width = 120
            MockConsole.return_value = mock_con
            try:
                printer = HTTPRequestPrinter()
            except TypeError as exc:
                self.fail(f"HTTPRequestPrinter() raised TypeError: {exc}")
        self.assertIsInstance(printer, HTTPRequestPrinter)

    def testHTTPRequestPrinterIsInstanceOfInterface(self) -> None:
        """
        Verify that an HTTPRequestPrinter instance satisfies isinstance check.

        Ensures polymorphic usage is valid: code that accepts an
        IHTTPRequestPrinter can transparently receive an HTTPRequestPrinter.
        """
        with patch("orionis.console.output.http_request.Console") as MockConsole:
            mock_con = MagicMock()
            mock_con.size.width = 120
            MockConsole.return_value = mock_con
            printer = HTTPRequestPrinter()
        self.assertIsInstance(printer, IHTTPRequestPrinter)

    def testHTTPRequestPrinterImplementsPrintRequest(self) -> None:
        """
        Verify that HTTPRequestPrinter provides a concrete printRequest method.

        Ensures the method is callable on the class and is no longer
        abstract, allowing it to be used without further subclassing.
        """
        self.assertTrue(callable(HTTPRequestPrinter.printRequest))
        self.assertNotIn("printRequest", HTTPRequestPrinter.__dict__.get(
            "__abstractmethods__", set(),
        ))
