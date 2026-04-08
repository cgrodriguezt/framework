from __future__ import annotations

import asyncio
import io
import time
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
        Create an HTTPRequestPrinter with default terminal width.

        Returns
        -------
        HTTPRequestPrinter
            A printer instance ready for testing.
        """
        return HTTPRequestPrinter()

    def _make_with_width(self, columns: int) -> HTTPRequestPrinter:
        """
        Create an HTTPRequestPrinter forcing a specific terminal column count.

        Parameters
        ----------
        columns : int
            Simulated terminal column width.

        Returns
        -------
        HTTPRequestPrinter
            A printer whose _total_width reflects the given column count.
        """
        with patch("shutil.get_terminal_size") as mock_size:
            mock_size.return_value = MagicMock(columns=columns)
            return HTTPRequestPrinter()

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

    def testHttpColorsEntriesAreTuples(self) -> None:
        """
        Verify that every HTTP_COLORS entry is a (bg_ansi, fg_ansi) tuple.

        Ensures the colour data structure is consistent so renderers can
        always unpack both background and foreground ANSI codes.
        """
        for key, value in HTTPRequestPrinter.HTTP_COLORS.items():
            self.assertIsInstance(value, tuple, f"Entry '{key}' should be a tuple")
            self.assertEqual(len(value), 2, f"Entry '{key}' should have 2 elements (bg, fg)")

    def testStatusColorsContainsAllCategories(self) -> None:
        """
        Verify that STATUS_COLORS contains entries for all 5 HTTP status categories.

        Ensures 1xx-5xx responses are all mapped to a rendering style so
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

    def testStatusColorsEntriesAreTuples(self) -> None:
        """
        Verify that every STATUS_COLORS entry is a (bg_ansi, fg_ansi) tuple.

        Ensures the colour structure is consistent across all status-code
        categories so renderers can always unpack both ANSI codes.
        """
        for key, value in HTTPRequestPrinter.STATUS_COLORS.items():
            self.assertIsInstance(value, tuple, f"Entry '{key}' should be a tuple")
            self.assertEqual(len(value), 2, f"Entry '{key}' should have 2 elements (bg, fg)")

    # ------------------------------------------------------------------ #
    #  startTimer                                                        #
    # ------------------------------------------------------------------ #

    def testStartTimerReturnsFloat(self) -> None:
        """
        Verify that startTimer returns a float value.

        Ensures the returned timestamp is a valid high-resolution float
        compatible with time.perf_counter semantics.
        """
        result = HTTPRequestPrinter.startTimer()
        self.assertIsInstance(result, float)

    def testStartTimerIsMonotonic(self) -> None:
        """
        Verify that consecutive startTimer calls return non-decreasing values.

        Ensures the timer uses a monotonic source and cannot go backwards
        between two calls within the same execution context.
        """
        t1 = HTTPRequestPrinter.startTimer()
        t2 = HTTPRequestPrinter.startTimer()
        self.assertLessEqual(t1, t2)

    # ------------------------------------------------------------------ #
    #  printRequest -- return value                                      #
    # ------------------------------------------------------------------ #

    def testPrintRequestReturnsNone(self) -> None:
        """
        Verify that printRequest returns None.

        Ensures the method adheres to its declared contract which
        specifies a None return value.
        """
        printer = self._make()
        with patch("sys.stdout", new_callable=io.StringIO):
            result = printer.printRequest("GET", "/api/health", time.perf_counter() - 0.05)
        self.assertIsNone(result)

    # ------------------------------------------------------------------ #
    #  printRequest -- writes to stdout when queue not started           #
    # ------------------------------------------------------------------ #

    def testPrintRequestWritesToStdoutDirectly(self) -> None:
        """
        Verify that printRequest writes to stdout when start() has not been called.

        Ensures the direct-write fallback path produces non-empty output
        so requests are logged even outside an async lifecycle.
        """
        printer = self._make()
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            printer.printRequest("GET", "/api/health", time.perf_counter() - 0.05)
        self.assertGreater(len(buf.getvalue()), 0)

    # ------------------------------------------------------------------ #
    #  printRequest -- HTTP method variants                              #
    # ------------------------------------------------------------------ #

    def testPrintRequestWithGetMethod(self) -> None:
        """
        Verify that printRequest handles the GET method without raising.

        Ensures the most common HTTP method is rendered correctly and the
        method completes without any exception.
        """
        printer = self._make()
        with patch("sys.stdout", new_callable=io.StringIO):
            result = printer.printRequest("GET", "/users", time.perf_counter() - 0.05)
        self.assertIsNone(result)

    def testPrintRequestWithPostMethod(self) -> None:
        """
        Verify that printRequest handles the POST method without raising.

        Ensures POST requests are rendered correctly with the appropriate
        colour style.
        """
        printer = self._make()
        with patch("sys.stdout", new_callable=io.StringIO):
            result = printer.printRequest("POST", "/users", time.perf_counter() - 0.12)
        self.assertIsNone(result)

    def testPrintRequestWithDeleteMethod(self) -> None:
        """
        Verify that printRequest handles the DELETE method without raising.

        Ensures DELETE requests are rendered correctly without exceptions.
        """
        printer = self._make()
        with patch("sys.stdout", new_callable=io.StringIO):
            result = printer.printRequest("DELETE", "/users/1", time.perf_counter() - 0.08)
        self.assertIsNone(result)

    def testPrintRequestWithUnknownMethod(self) -> None:
        """
        Verify that printRequest handles an unknown HTTP method gracefully.

        Ensures the 'default' colour fallback is used without raising
        a KeyError when the method is not in HTTP_COLORS.
        """
        printer = self._make()
        with patch("sys.stdout", new_callable=io.StringIO):
            result = printer.printRequest("BREW", "/coffee", time.perf_counter() - 0.42)
        self.assertIsNone(result)

    def testPrintRequestNormalisesLowercaseMethod(self) -> None:
        """
        Verify that printRequest normalises a lowercase method to uppercase.

        Ensures that 'get' and 'GET' produce the same rendering behaviour
        so callers are not required to pre-uppercase the method string.
        """
        printer = self._make()
        with patch("sys.stdout", new_callable=io.StringIO):
            result = printer.printRequest("get", "/api", time.perf_counter() - 0.01)
        self.assertIsNone(result)

    # ------------------------------------------------------------------ #
    #  printRequest -- duration formatting                               #
    # ------------------------------------------------------------------ #

    def testPrintRequestShortDurationFormatsAsMs(self) -> None:
        """
        Verify that a sub-second duration is formatted in milliseconds.

        Ensures that durations below 1.0 second are expressed as '~ Xms'
        rather than seconds, matching the expected display convention.
        """
        printer = self._make()
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            printer.printRequest("GET", "/", time.perf_counter() - 0.123)
        self.assertIn("ms", buf.getvalue())

    def testPrintRequestLongDurationFormatsAsSeconds(self) -> None:
        """
        Verify that a duration >= 1 second is formatted as seconds.

        Ensures that long-running requests display '~ X.XXs' rather than
        a large millisecond number, improving readability.
        """
        printer = self._make()
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            printer.printRequest("GET", "/slow", time.perf_counter() - 2.5)
        output = buf.getvalue()
        self.assertNotIn("ms", output)
        self.assertIn("s", output)

    def testPrintRequestExactlyOneSecondDuration(self) -> None:
        """
        Verify that a duration of exactly 1.0 second formats as seconds.

        Ensures the boundary condition between ms and s formatting is
        correct: 1.0 should use the seconds format.
        """
        printer = self._make()
        with patch("sys.stdout", new_callable=io.StringIO):
            result = printer.printRequest("GET", "/boundary", time.perf_counter() - 1.0)
        self.assertIsNone(result)

    def testPrintRequestZeroDuration(self) -> None:
        """
        Verify that a start_time equal to now does not raise an exception.

        Ensures edge-case input (near-zero elapsed time) is handled without
        crashing the formatter.
        """
        printer = self._make()
        with patch("sys.stdout", new_callable=io.StringIO):
            result = printer.printRequest("GET", "/instant", time.perf_counter())
        self.assertIsNone(result)

    # ------------------------------------------------------------------ #
    #  printRequest -- status icon by HTTP code category                #
    # ------------------------------------------------------------------ #

    def testPrintRequest2xxShowsGreenIcon(self) -> None:
        """
        Verify that a 2xx status code renders the green circle icon.

        Ensures that a successful response (200) outputs the 🟢 icon.
        """
        printer = self._make()
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            printer.printRequest("GET", "/ok", time.perf_counter() - 0.1, code=200)
        self.assertIn("🟢", buf.getvalue())

    def testPrintRequest3xxShowsBlueIcon(self) -> None:
        """
        Verify that a 3xx status code renders the blue circle icon.

        Ensures that a redirect response (301) outputs the 🔵 icon.
        """
        printer = self._make()
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            printer.printRequest("GET", "/redirect", time.perf_counter() - 0.05, code=301)
        self.assertIn("🔵", buf.getvalue())

    def testPrintRequest4xxShowsYellowIcon(self) -> None:
        """
        Verify that a 4xx status code renders the yellow circle icon.

        Ensures that a client-error response (404) outputs the 🟡 icon.
        """
        printer = self._make()
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            printer.printRequest("GET", "/missing", time.perf_counter() - 0.03, code=404)
        self.assertIn("🟡", buf.getvalue())

    def testPrintRequest5xxShowsRedIcon(self) -> None:
        """
        Verify that a 5xx status code renders the red circle icon.

        Ensures that a server-error response (500) outputs the 🔴 icon.
        """
        printer = self._make()
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            printer.printRequest("GET", "/crash", time.perf_counter() - 0.1, code=500)
        self.assertIn("🔴", buf.getvalue())

    # ------------------------------------------------------------------ #
    #  printRequest -- HTTP status codes                                 #
    # ------------------------------------------------------------------ #

    def testPrintRequestWith200StatusCode(self) -> None:
        """
        Verify that a 200 status code is accepted and rendered without error.

        Ensures the most common successful response code maps to the
        2xx category colour correctly.
        """
        printer = self._make()
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            printer.printRequest("GET", "/", time.perf_counter() - 0.05, code=200)
        self.assertIn("200", buf.getvalue())

    def testPrintRequestWith404StatusCode(self) -> None:
        """
        Verify that a 404 status code is accepted and rendered without error.

        Ensures a client-error response code maps to the 4xx category
        colour without raising any exception.
        """
        printer = self._make()
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            printer.printRequest("GET", "/missing", time.perf_counter() - 0.03, code=404)
        self.assertIn("404", buf.getvalue())

    def testPrintRequestWith500StatusCode(self) -> None:
        """
        Verify that a 500 status code is accepted and rendered without error.

        Ensures a server-error response code maps to the 5xx category
        colour without raising any exception.
        """
        printer = self._make()
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            printer.printRequest("POST", "/crash", time.perf_counter() - 0.2, code=500)
        self.assertIn("500", buf.getvalue())

    def testPrintRequestWith301StatusCode(self) -> None:
        """
        Verify that a 301 redirect status code is rendered without error.

        Ensures 3xx responses map to the redirect colour category correctly.
        """
        printer = self._make()
        with patch("sys.stdout", new_callable=io.StringIO):
            result = printer.printRequest("GET", "/moved", time.perf_counter() - 0.01, code=301)
        self.assertIsNone(result)

    def testPrintRequestWith100StatusCode(self) -> None:
        """
        Verify that a 100 informational status code is rendered without error.

        Ensures 1xx responses map to the informational colour category
        without raising any exception.
        """
        printer = self._make()
        with patch("sys.stdout", new_callable=io.StringIO):
            result = printer.printRequest("GET", "/continue", time.perf_counter() - 0.001, code=100)
        self.assertIsNone(result)

    # ------------------------------------------------------------------ #
    #  printRequest -- path edge cases                                   #
    # ------------------------------------------------------------------ #

    def testPrintRequestWithShortPath(self) -> None:
        """
        Verify that a short path is rendered without truncation or error.

        Ensures paths well within the display width are output as-is
        without appending an ellipsis.
        """
        printer = self._make()
        with patch("sys.stdout", new_callable=io.StringIO):
            result = printer.printRequest("GET", "/a", time.perf_counter() - 0.01)
        self.assertIsNone(result)

    def testPrintRequestWithVeryLongPath(self) -> None:
        """
        Verify that a very long path is truncated and rendered without error.

        Ensures that paths exceeding the computed max_path limit are
        shortened with '...' rather than overflowing the output line.
        """
        printer = self._make()
        long_path = "/" + "x" * 300
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            printer.printRequest("GET", long_path, time.perf_counter() - 0.1)
        self.assertIn("...", buf.getvalue())

    def testPrintRequestWithRootPath(self) -> None:
        """
        Verify that the root path '/' is accepted and rendered correctly.

        Ensures that a single-character path does not cause off-by-one
        errors in the dot-filler calculation.
        """
        printer = self._make()
        with patch("sys.stdout", new_callable=io.StringIO):
            result = printer.printRequest("GET", "/", time.perf_counter() - 0.02)
        self.assertIsNone(result)

    # ------------------------------------------------------------------ #
    #  setEnabled                                                        #
    # ------------------------------------------------------------------ #

    def testSetEnabledFalseDisablesOutput(self) -> None:
        """
        Verify that setEnabled(False) prevents any output from being produced.

        Ensures the disabled flag is respected and stdout is not written to.
        """
        printer = self._make()
        printer.setEnabled(enabled=False)
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            printer.printRequest("GET", "/", time.perf_counter())
        self.assertEqual(buf.getvalue(), "")

    def testSetEnabledTrueRestoresOutput(self) -> None:
        """
        Verify that re-enabling output after disabling restores stdout writes.

        Ensures toggling the flag back to True allows subsequent requests
        to be logged normally.
        """
        printer = self._make()
        printer.setEnabled(enabled=False)
        printer.setEnabled(enabled=True)
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            printer.printRequest("GET", "/", time.perf_counter() - 0.01)
        self.assertGreater(len(buf.getvalue()), 0)

    # ------------------------------------------------------------------ #
    #  _total_width computation                                          #
    # ------------------------------------------------------------------ #

    def testTotalWidthClampedToMinimum(self) -> None:
        """
        Verify that _total_width is at least 60 for a very narrow terminal.

        Ensures the minimum clamp prevents the layout from collapsing on
        extremely narrow displays.
        """
        printer = self._make_with_width(10)
        self.assertGreaterEqual(printer._total_width, 60)

    def testTotalWidthClampedToMaximum(self) -> None:
        """
        Verify that _total_width is at most 120 for a very wide terminal.

        Ensures the maximum clamp prevents the layout from spanning an
        enormous width on very wide displays.
        """
        printer = self._make_with_width(1000)
        self.assertLessEqual(printer._total_width, 120)

    # ------------------------------------------------------------------ #
    #  Queue + Worker lifecycle                                          #
    # ------------------------------------------------------------------ #

    async def testStartCreatesQueueAndWorker(self) -> None:
        """
        Verify that start() initialises the internal queue and worker task.

        Ensures the queue and worker_task attributes transition from None
        to a valid Queue and Task after start() is awaited.
        """
        printer = self._make()
        self.assertIsNone(printer._HTTPRequestPrinter__queue)
        self.assertIsNone(printer._HTTPRequestPrinter__worker_task)
        await printer.start()
        self.assertIsNotNone(printer._HTTPRequestPrinter__queue)
        self.assertIsNotNone(printer._HTTPRequestPrinter__worker_task)
        await printer.stop()

    async def testStopDrainsQueueAndCancelsWorker(self) -> None:
        """
        Verify that stop() resets queue and worker task references to None.

        Ensures the printer is returned to its pre-start state after stop(),
        allowing safe re-use or clean shutdown.
        """
        printer = self._make()
        await printer.start()
        await printer.stop()
        self.assertIsNone(printer._HTTPRequestPrinter__queue)
        self.assertIsNone(printer._HTTPRequestPrinter__worker_task)

    async def testPrintRequestEnqueuesWhenStarted(self) -> None:
        """
        Verify that printRequest enqueues a line when start() has been called.

        Ensures the worker drains the queue so no messages are lost after
        the printer is running in async mode.
        """
        printer = self._make()
        await printer.start()
        with patch("sys.stdout", new_callable=io.StringIO):
            printer.printRequest("GET", "/test", time.perf_counter() - 0.01)
        # Allow worker loop to process the enqueued item
        await asyncio.sleep(0.05)
        queue = printer._HTTPRequestPrinter__queue
        self.assertEqual(queue.qsize(), 0)
        await printer.stop()

    async def testQueueFullDropsMessageSilently(self) -> None:
        """
        Verify that a full queue causes messages to be dropped without raising.

        Ensures the printer never blocks the event loop under extreme back-
        pressure -- excess messages are silently discarded.
        """
        printer = self._make()
        await printer.start()
        queue = printer._HTTPRequestPrinter__queue
        # Saturate the queue
        for _ in range(1000):
            try:
                queue.put_nowait("x")
            except asyncio.QueueFull:
                break
        # Must not raise even when the queue is full
        with patch("sys.stdout", new_callable=io.StringIO):
            printer.printRequest("GET", "/overflow", time.perf_counter() - 0.01)
        await printer.stop()
