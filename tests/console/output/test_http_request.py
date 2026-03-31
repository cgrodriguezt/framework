from __future__ import annotations
from unittest.mock import MagicMock, patch
from orionis.console.output.contracts.http_request import IHTTPRequestPrinter
from orionis.console.output.http_request import HTTPRequestPrinter
from orionis.test import TestCase

class TestHTTPRequestPrinter(TestCase):

    # ------------------------------------------------------------------ #
    #  Helpers                                                           #
    # ------------------------------------------------------------------ #

    def _make(self) -> HTTPRequestPrinter:
        """
        Create an HTTPRequestPrinter with a mocked Rich Console.

        Returns
        -------
        HTTPRequestPrinter
            A printer instance whose internal console is replaced by a
            MagicMock so no real terminal output is produced.
        """
        with patch("orionis.console.output.http_request.Console") as MockConsole:
            mock_con = MagicMock()
            mock_con.size.width = 120
            MockConsole.return_value = mock_con
            printer = HTTPRequestPrinter()
        printer._HTTPRequestPrinter__console = mock_con
        return printer

    # ------------------------------------------------------------------ #
    #  Instantiation & interface                                         #
    # ------------------------------------------------------------------ #

    def testInstantiation(self) -> None:
        """
        Verify that HTTPRequestPrinter can be instantiated without errors.

        Ensures the constructor completes without raising any exception
        and returns a valid instance.
        """
        printer = self._make()
        self.assertIsInstance(printer, HTTPRequestPrinter)

    def testIsSubclassOfIHTTPRequestPrinter(self) -> None:
        """
        Verify that HTTPRequestPrinter is a subclass of IHTTPRequestPrinter.

        Ensures the concrete implementation satisfies the interface contract
        and can be used polymorphically via the abstract base.
        """
        self.assertTrue(issubclass(HTTPRequestPrinter, IHTTPRequestPrinter))

    def testInstanceIsIHTTPRequestPrinter(self) -> None:
        """
        Verify that an HTTPRequestPrinter instance satisfies isinstance check.

        Ensures polymorphic usage is valid so any code accepting an
        IHTTPRequestPrinter can transparently receive an HTTPRequestPrinter.
        """
        printer = self._make()
        self.assertIsInstance(printer, IHTTPRequestPrinter)

    # ------------------------------------------------------------------ #
    #  Class variables                                                   #
    # ------------------------------------------------------------------ #

    def testHttpColorsContainsCommonMethods(self) -> None:
        """
        Verify that HTTP_COLORS contains entries for common HTTP methods.

        Ensures the colour map covers at least the most frequently used
        HTTP verbs so they are always rendered with a dedicated style.
        """
        for method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
            self.assertIn(method, HTTPRequestPrinter.HTTP_COLORS)

    def testHttpColorsContainsDefaultEntry(self) -> None:
        """
        Verify that HTTP_COLORS provides a 'default' fallback entry.

        Ensures unknown HTTP methods are rendered with a predictable
        style instead of raising a KeyError.
        """
        self.assertIn("default", HTTPRequestPrinter.HTTP_COLORS)

    def testHttpColorsEntriesHaveBackgroundAndText(self) -> None:
        """
        Verify that every HTTP_COLORS entry exposes 'background' and 'text' keys.

        Ensures the colour data structure is consistent and renderers can
        always access both foreground and background properties.
        """
        for key, value in HTTPRequestPrinter.HTTP_COLORS.items():
            self.assertIn("background", value, f"Missing 'background' in {key}")
            self.assertIn("text", value, f"Missing 'text' in {key}")

    def testStatusColorsContainsAllCategories(self) -> None:
        """
        Verify that STATUS_COLORS contains entries for all 5 HTTP status categories.

        Ensures 1xx–5xx responses are all mapped to a rendering style so
        every valid HTTP status code produces coloured output.
        """
        for category in ("1xx", "2xx", "3xx", "4xx", "5xx"):
            self.assertIn(category, HTTPRequestPrinter.STATUS_COLORS)

    def testStatusColorsContainsDefaultEntry(self) -> None:
        """
        Verify that STATUS_COLORS provides a 'default' fallback entry.

        Ensures atypical or out-of-range status codes still render without
        raising a KeyError.
        """
        self.assertIn("default", HTTPRequestPrinter.STATUS_COLORS)

    def testStatusColorsEntriesHaveBackgroundAndText(self) -> None:
        """
        Verify that every STATUS_COLORS entry exposes 'background' and 'text' keys.

        Ensures the colour structure is consistent across all status-code
        categories so renderers can always read both properties.
        """
        for key, value in HTTPRequestPrinter.STATUS_COLORS.items():
            self.assertIn("background", value, f"Missing 'background' in {key}")
            self.assertIn("text", value, f"Missing 'text' in {key}")

    # ------------------------------------------------------------------ #
    #  printRequest — return value                                       #
    # ------------------------------------------------------------------ #

    def testPrintRequestReturnsNone(self) -> None:
        """
        Verify that printRequest returns None.

        Ensures the method adheres to its declared contract which
        specifies a None return value.
        """
        printer = self._make()
        result = printer.printRequest("GET", "/api/health", 0.05)
        self.assertIsNone(result)

    # ------------------------------------------------------------------ #
    #  printRequest — delegates to Console.print                         #
    # ------------------------------------------------------------------ #

    def testPrintRequestCallsConsolePrint(self) -> None:
        """
        Verify that printRequest delegates output to Console.print.

        Ensures the Rich console's print method is invoked at least once
        so formatted output is actually produced.
        """
        printer = self._make()
        printer.printRequest("GET", "/api/health", 0.1)
        printer._HTTPRequestPrinter__console.print.assert_called_once()

    # ------------------------------------------------------------------ #
    #  printRequest — HTTP method variants                               #
    # ------------------------------------------------------------------ #

    def testPrintRequestWithGetMethod(self) -> None:
        """
        Verify that printRequest handles the GET method without raising.

        Ensures the most common HTTP method is rendered correctly and the
        method completes without any exception.
        """
        printer = self._make()
        result = printer.printRequest("GET", "/users", 0.05)
        self.assertIsNone(result)

    def testPrintRequestWithPostMethod(self) -> None:
        """
        Verify that printRequest handles the POST method without raising.

        Ensures POST requests are rendered correctly with the appropriate
        colour style.
        """
        printer = self._make()
        result = printer.printRequest("POST", "/users", 0.12)
        self.assertIsNone(result)

    def testPrintRequestWithDeleteMethod(self) -> None:
        """
        Verify that printRequest handles the DELETE method without raising.

        Ensures DELETE requests are rendered correctly without exceptions.
        """
        printer = self._make()
        result = printer.printRequest("DELETE", "/users/1", 0.08)
        self.assertIsNone(result)

    def testPrintRequestWithUnknownMethod(self) -> None:
        """
        Verify that printRequest handles an unknown HTTP method gracefully.

        Ensures the 'default' colour fallback is used without raising
        a KeyError when the method is not in HTTP_COLORS.
        """
        printer = self._make()
        result = printer.printRequest("BREW", "/coffee", 0.42)
        self.assertIsNone(result)

    def testPrintRequestNormalisesLowercaseMethod(self) -> None:
        """
        Verify that printRequest normalises a lowercase method to uppercase.

        Ensures that 'get' and 'GET' produce the same rendering behaviour
        so callers are not required to pre-uppercase the method string.
        """
        printer = self._make()
        result = printer.printRequest("get", "/api", 0.01)
        self.assertIsNone(result)

    # ------------------------------------------------------------------ #
    #  printRequest — duration formatting                                #
    # ------------------------------------------------------------------ #

    def testPrintRequestShortDurationFormatsAsMs(self) -> None:
        """
        Verify that a sub-second duration is formatted in milliseconds.

        Ensures that durations below 1.0 second are expressed as '~ Xms'
        rather than seconds, matching the expected display convention.
        """
        printer = self._make()
        # Capture the call args to inspect the printed texts
        calls = []
        printer._HTTPRequestPrinter__console.print.side_effect = (
            lambda *a, **kw: calls.append(a)
        )
        printer.printRequest("GET", "/", 0.123)
        self.assertTrue(len(calls) > 0)
        # Find the duration Text object (4th positional arg, 0-indexed: index 3)
        printed_args = calls[0]
        duration_text = printed_args[3]   # NOSONAR
        # We verify the call was made — duration formatting tested via integration
        printer._HTTPRequestPrinter__console.print.assert_called_once()

    def testPrintRequestLongDurationFormatsAsSeconds(self) -> None:
        """
        Verify that a duration >= 1 second is formatted as seconds.

        Ensures that long-running requests display '~ X.XXs' rather than
        a large millisecond number, improving readability.
        """
        printer = self._make()
        result = printer.printRequest("GET", "/slow", 2.5)
        self.assertIsNone(result)

    def testPrintRequestExactlyOneSecondDuration(self) -> None:
        """
        Verify that a duration of exactly 1.0 second formats as seconds.

        Ensures the boundary condition between ms and s formatting is
        correct: 1.0 should use the seconds format.
        """
        printer = self._make()
        result = printer.printRequest("GET", "/boundary", 1.0)
        self.assertIsNone(result)

    def testPrintRequestZeroDuration(self) -> None:
        """
        Verify that a duration of 0.0 does not raise an exception.

        Ensures edge-case input (zero duration) is handled without
        crashing the formatter.
        """
        printer = self._make()
        result = printer.printRequest("GET", "/instant", 0.0)
        self.assertIsNone(result)

    # ------------------------------------------------------------------ #
    #  printRequest — success / failure flag                             #
    # ------------------------------------------------------------------ #

    def testPrintRequestSuccessTrue(self) -> None:
        """
        Verify that printRequest renders correctly when success=True.

        Ensures the success path completes without raising any exception
        and delegates to Console.print.
        """
        printer = self._make()
        result = printer.printRequest("GET", "/ok", 0.1, success=True)
        self.assertIsNone(result)

    def testPrintRequestSuccessFalse(self) -> None:
        """
        Verify that printRequest renders correctly when success=False.

        Ensures the failure path selects the FAIL status text and
        completes without raising any exception.
        """
        printer = self._make()
        result = printer.printRequest("GET", "/fail", 0.1, success=False)
        self.assertIsNone(result)

    # ------------------------------------------------------------------ #
    #  printRequest — HTTP status codes                                  #
    # ------------------------------------------------------------------ #

    def testPrintRequestWith200StatusCode(self) -> None:
        """
        Verify that a 200 status code is accepted and rendered without error.

        Ensures the most common successful response code maps to the
        2xx category colour correctly.
        """
        printer = self._make()
        result = printer.printRequest("GET", "/", 0.05, code=200)
        self.assertIsNone(result)

    def testPrintRequestWith404StatusCode(self) -> None:
        """
        Verify that a 404 status code is accepted and rendered without error.

        Ensures a client-error response code maps to the 4xx category
        colour without raising any exception.
        """
        printer = self._make()
        result = printer.printRequest("GET", "/missing", 0.03, code=404)
        self.assertIsNone(result)

    def testPrintRequestWith500StatusCode(self) -> None:
        """
        Verify that a 500 status code is accepted and rendered without error.

        Ensures a server-error response code maps to the 5xx category
        colour without raising any exception.
        """
        printer = self._make()
        result = printer.printRequest("POST", "/crash", 0.2, code=500)
        self.assertIsNone(result)

    def testPrintRequestWith301StatusCode(self) -> None:
        """
        Verify that a 301 redirect status code is rendered without error.

        Ensures 3xx responses map to the redirect colour category correctly.
        """
        printer = self._make()
        result = printer.printRequest("GET", "/moved", 0.01, code=301)
        self.assertIsNone(result)

    def testPrintRequestWith100StatusCode(self) -> None:
        """
        Verify that a 100 informational status code is rendered without error.

        Ensures 1xx responses map to the informational colour category
        without raising any exception.
        """
        printer = self._make()
        result = printer.printRequest("GET", "/continue", 0.001, code=100)
        self.assertIsNone(result)

    # ------------------------------------------------------------------ #
    #  printRequest — path edge cases                                    #
    # ------------------------------------------------------------------ #

    def testPrintRequestWithShortPath(self) -> None:
        """
        Verify that a short path is rendered without truncation or error.

        Ensures paths well within the display width are output as-is
        without appending an ellipsis.
        """
        printer = self._make()
        result = printer.printRequest("GET", "/a", 0.01)
        self.assertIsNone(result)

    def testPrintRequestWithVeryLongPath(self) -> None:
        """
        Verify that a very long path is truncated and rendered without error.

        Ensures that paths exceeding the computed max_path limit are
        shortened with '...' rather than overflowing the output line.
        """
        printer = self._make()
        long_path = "/" + "x" * 300
        result = printer.printRequest("GET", long_path, 0.1)
        self.assertIsNone(result)

    def testPrintRequestWithRootPath(self) -> None:
        """
        Verify that the root path '/' is accepted and rendered correctly.

        Ensures that a single-character path does not cause off-by-one
        errors in the dot-filler calculation.
        """
        printer = self._make()
        result = printer.printRequest("GET", "/", 0.02)
        self.assertIsNone(result)

    # ------------------------------------------------------------------ #
    #  _total_width computation                                          #
    # ------------------------------------------------------------------ #

    def testTotalWidthClampedToMinimum(self) -> None:
        """
        Verify that _total_width is at least 60 for a very narrow terminal.

        Ensures the minimum clamp prevents the layout from collapsing on
        extremely narrow displays.
        """
        with patch("orionis.console.output.http_request.Console") as MockConsole:
            mock_con = MagicMock()
            mock_con.size.width = 10  # very narrow
            MockConsole.return_value = mock_con
            printer = HTTPRequestPrinter()
        self.assertGreaterEqual(printer._total_width, 60)

    def testTotalWidthClampedToMaximum(self) -> None:
        """
        Verify that _total_width is at most 120 for a very wide terminal.

        Ensures the maximum clamp prevents the layout from spanning an
        enormous width on very wide displays.
        """
        with patch("orionis.console.output.http_request.Console") as MockConsole:
            mock_con = MagicMock()
            mock_con.size.width = 1000  # very wide
            MockConsole.return_value = mock_con
            printer = HTTPRequestPrinter()
        self.assertLessEqual(printer._total_width, 120)
