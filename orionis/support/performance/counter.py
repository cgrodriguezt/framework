from __future__ import annotations
import asyncio
import time
from typing import Self, TYPE_CHECKING
from orionis.support.performance.contracts.counter import IPerformanceCounter

if TYPE_CHECKING:
    from types import TracebackType

class PerformanceCounter(IPerformanceCounter):

    def __init__(self) -> None:
        """
        Initialize the PerformanceCounter instance.

        Initializes internal attributes for tracking start, end, and elapsed time.

        Returns
        -------
        None
            This constructor does not return a value.
        """
        # Initialize timing attributes for performance measurement
        self.__start_time: float | None = None
        self.__end_time: float | None = None
        self.__diff_time: float | None = None
        self.__is_async_mode: bool = False

    def start(self) -> PerformanceCounter:
        """
        Start the performance counter.

        Records the current high-resolution time as the start time.

        Returns
        -------
        PerformanceCounter
            This instance for method chaining.
        """
        # Record the current time as the start time for sync usage
        self.__start_time = time.perf_counter()
        self.__is_async_mode = False
        return self

    async def astart(self) -> PerformanceCounter:
        """
        Start the performance counter asynchronously.

        Records the current high-resolution time as the start time using the
        event loop.

        Returns
        -------
        PerformanceCounter
            The current instance for method chaining.
        """
        # Record the current time as the start time for async usage
        loop = asyncio.get_running_loop()
        self.__start_time = loop.time()
        self.__is_async_mode = True
        return self

    def stop(self) -> PerformanceCounter:
        """
        Stop the performance counter and compute elapsed time.

        Records the current high-resolution time as the end time and computes the
        elapsed time since `start()` was called.

        Returns
        -------
        PerformanceCounter
            The current instance for method chaining.

        Raises
        ------
        RuntimeError
            If called after asynchronous start.
        """
        # Ensure synchronous mode before stopping
        if self.__is_async_mode:
            error_msg = (
                "Cannot use stop() after astart(). Use astop() instead."
            )
            raise RuntimeError(error_msg)
        # Record the current time as the end time
        self.__end_time = time.perf_counter()
        # Compute the elapsed time
        self.__diff_time = self.__end_time - self.__start_time
        return self

    async def astop(self) -> PerformanceCounter:
        """
        Stop the performance counter asynchronously.

        Records the current high-resolution time as the end time and computes the
        elapsed time since `astart()` was called.

        Returns
        -------
        PerformanceCounter
            This instance for method chaining.

        Raises
        ------
        RuntimeError
            If called after synchronous start.
        """
        # Ensure asynchronous mode before stopping
        if not self.__is_async_mode:
            error_msg = (
                "Cannot use astop() after start(). Use stop() instead."
            )
            raise RuntimeError(error_msg)
        # Record the current time as the end time for async usage
        loop = asyncio.get_running_loop()
        self.__end_time = loop.time()
        # Compute the elapsed time
        self.__diff_time = self.__end_time - self.__start_time
        return self

    def elapsedTime(self) -> float:
        """
        Return the elapsed time in seconds between the last start and stop calls.

        Raises
        ------
        ValueError
            If the counter has not been started and stopped properly.

        Returns
        -------
        float
            Elapsed time in seconds as a float.
        """
        # Ensure the counter has been started and stopped before returning elapsed time
        if self.__diff_time is None:
            error_msg = (
                "Counter has not been started and stopped properly."
            )
            raise ValueError(error_msg)
        return self.__diff_time

    async def aelapsedTime(self) -> float:
        """
        Return the elapsed time in seconds asynchronously.

        Returns
        -------
        float
            Elapsed time in seconds as a float.

        Raises
        ------
        ValueError
            If the counter has not been started and stopped properly.
        """
        # Use the synchronous elapsedTime method for async context
        return self.elapsedTime()

    def getMicroseconds(self) -> float:
        """
        Return the elapsed time in microseconds.

        Converts the elapsed time in seconds to microseconds.

        Returns
        -------
        float
            Elapsed time in microseconds.
        """
        # Convert seconds to microseconds
        return self.elapsedTime() * 1_000_000

    async def agetMicroseconds(self) -> float:
        """
        Return the elapsed time in microseconds asynchronously.

        Returns
        -------
        float
            Elapsed time in microseconds as a float.
        """
        # Convert seconds to microseconds asynchronously
        return self.elapsedTime() * 1_000_000

    def getMilliseconds(self) -> float:
        """
        Return the elapsed time in milliseconds.

        Converts the elapsed time in seconds to milliseconds.

        Returns
        -------
        float
            Elapsed time in milliseconds as a float.
        """
        # Convert seconds to milliseconds
        return self.elapsedTime() * 1_000

    async def agetMilliseconds(self) -> float:
        """
        Return the elapsed time in milliseconds asynchronously.

        Returns
        -------
        float
            Elapsed time in milliseconds as a float.
        """
        # Convert seconds to milliseconds asynchronously
        return self.elapsedTime() * 1_000

    def getSeconds(self) -> float:
        """
        Return the elapsed time in seconds.

        Returns
        -------
        float
            Elapsed time in seconds as a float.
        """
        # Return the elapsed time in seconds
        return self.elapsedTime()

    async def agetSeconds(self) -> float:
        """
        Return the elapsed time in seconds asynchronously.

        Returns
        -------
        float
            Elapsed time in seconds as a float.
        """
        # Return elapsed time in seconds asynchronously
        return self.elapsedTime()

    def getMinutes(self) -> float:
        """
        Return the elapsed time in minutes.

        Returns
        -------
        float
            Elapsed time in minutes as a float.
        """
        # Convert seconds to minutes
        return self.elapsedTime() / 60

    async def agetMinutes(self) -> float:
        """
        Return the elapsed time in minutes asynchronously.

        Returns
        -------
        float
            Elapsed time in minutes as a float.
        """
        # Convert seconds to minutes asynchronously
        return self.elapsedTime() / 60

    def restart(self) -> PerformanceCounter:
        """
        Restart the performance counter.

        Resets internal timing attributes and starts the counter again. Useful for
        measuring a new interval without creating a new instance.

        Returns
        -------
        PerformanceCounter
            This instance for method chaining.
        """
        # Reset timing attributes for a fresh measurement
        self.__start_time = None
        self.__end_time = None
        self.__diff_time = None
        self.__is_async_mode = False
        return self.start()

    async def arestart(self) -> PerformanceCounter:
        """
        Restart the performance counter asynchronously.

        Resets internal timing attributes and starts the counter again in async
        mode.

        Returns
        -------
        PerformanceCounter
            This instance for method chaining.
        """
        # Reset timing attributes for a fresh async measurement
        self.__start_time = None
        self.__end_time = None
        self.__diff_time = None
        self.__is_async_mode = False
        return await self.astart()

    def __enter__(self) -> Self:
        """
        Enter the context manager and start the counter.

        Returns
        -------
        PerformanceCounter
            This instance of the performance counter.
        """
        # Start the counter when entering the context
        return self.start()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Exit the context manager and stop the counter.

        Parameters
        ----------
        exc_type : type or None
            Exception type if raised, else None.
        exc_val : BaseException or None
            Exception value if raised, else None.
        exc_tb : object or None
            Traceback object if exception occurred, else None.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Stop the counter when exiting the context
        self.stop()

    async def __aenter__(self) -> Self:
        """
        Enter the async context manager and start the counter asynchronously.

        Returns
        -------
        PerformanceCounter
            This instance of the performance counter.
        """
        # Start the counter asynchronously when entering the context
        return await self.astart()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Exit the async context manager and stop the counter asynchronously.

        Parameters
        ----------
        exc_type : type or None
            Exception type if raised, else None.
        exc_val : BaseException or None
            Exception value if raised, else None.
        exc_tb : object or None
            Traceback object if exception occurred, else None.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Stop the counter asynchronously when exiting the context
        await self.astop()
