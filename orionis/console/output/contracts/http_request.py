from __future__ import annotations
from abc import ABC, abstractmethod

class IHTTPRequestPrinter(ABC):

    @abstractmethod
    def startTimer(self) -> float | None:
        """
        Capture the current high-resolution timestamp for request timing.

        Returns None immediately if printing is disabled (setEnabled(enabled=False)
        was called), avoiding unnecessary work.

        Returns
        -------
        float | None
            A high-resolution monotonic timestamp from time.perf_counter(),
            or None if output is disabled.
        """

    @abstractmethod
    def setEnabled(self, *, enabled: bool) -> None:
        """
        Set whether to enable or disable console output for HTTP requests.

        Parameters
        ----------
        enabled : bool
            If True, HTTP requests are printed to console. If False, output
            is suppressed.

        Returns
        -------
        None
            This method does not return a value.
        """

    @abstractmethod
    async def start(self) -> None:
        """
        Start the background print worker.

        Creates the internal async queue and spawns a background task
        to drain queued output lines. Must be called once from an async
        context before the first request is handled.

        Returns
        -------
        None
            This method does not return a value.
        """

    @abstractmethod
    async def stop(self) -> None:
        """
        Drain remaining output and stop the background worker.

        Waits for every queued line to be written before cancelling the
        worker task. Safe to call even if start() was never invoked.

        Returns
        -------
        None
            This method does not return a value.
        """

    @abstractmethod
    def printRequest(
        self,
        method: str,
        path: str,
        start_time: float | None,
        *,
        code: int = 200,
    ) -> None:
        """
        Print a formatted HTTP request line to stdout or queue.

        Computes the elapsed duration from start_time, builds an
        ANSI-coloured output line, and either enqueues it for the
        background worker (if start() was called) or writes directly
        to stdout.

        Parameters
        ----------
        method : str
            HTTP method (e.g., 'GET', 'POST').
        path : str
            Request path.
        start_time : float | None
            Timestamp from startTimer() at request beginning, or None if
            output was disabled at the time startTimer() was called.
        code : int, optional
            HTTP status code (default is 200).

        Returns
        -------
        None
            This method does not return a value.
        """

