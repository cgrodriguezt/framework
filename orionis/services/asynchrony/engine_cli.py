import asyncio
import sys
import inspect
import threading
from typing import Any
from collections.abc import Coroutine
from collections.abc import Callable
from contextlib import contextmanager
from contextlib import suppress

class ReactorLoop:

    # ruff: noqa: PLC0415, ANN401,PGH003

    # Track if the event loop policy has been configured
    _loop_configured: bool = False
    _current_loop: asyncio.AbstractEventLoop | None = None
    _loop_lock = threading.Lock()

    @classmethod
    def _configure_event_loop_policy(cls) -> None:
        """
        Configure the optimal event loop policy for the current platform.

        Installs the best available event loop policy, such as uvloop on
        non-Windows platforms, if running in CLI mode.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Prevent reconfiguration if already set
        if cls._loop_configured:
            return

        with cls._loop_lock:

            # Double-check within the lock
            if cls._loop_configured:
                return

            # Set the event loop policy
            cls.setEventPolicy()

            # Mark as configured
            cls._loop_configured = True

    @classmethod
    def setEventPolicy(cls) -> None:
        """
        Configure the event loop policy for the current platform.

        Sets the optimal event loop policy for the current platform and runtime
        context. Uses uvloop on non-Windows platforms if available, otherwise
        uses the default policy. On Windows, uses ProactorEventLoop if
        available.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Use uvloop if available and not on Windows
        if sys.platform != "win32":
            try:
                import uvloop  # type: ignore
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            except ImportError:
                pass
        # On Windows, use ProactorEventLoop for better performance
        elif sys.platform == "win32":
            with suppress(AttributeError):
                asyncio.set_event_loop_policy(
                    asyncio.WindowsProactorEventLoopPolicy(),
                )

    @classmethod
    def getEventLoop(cls) -> asyncio.AbstractEventLoop:
        """
        Retrieve the current event loop or create one if necessary.

        Attempts to return the running event loop. If none is running, returns
        the stored loop or creates a new one for the current thread. Ensures a
        single event loop is maintained throughout the application lifecycle.

        Returns
        -------
        asyncio.AbstractEventLoop
            The current or newly created event loop.

        Raises
        ------
        RuntimeError
            If no event loop is available or can be created.
        """
        try:
            # Attempt to get the currently running event loop.
            loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
            if cls._current_loop is None:
                cls._current_loop = loop
            return loop
        except RuntimeError:
            # No running loop; check for a stored loop.
            if cls._current_loop and not cls._current_loop.is_closed():
                return cls._current_loop

            # Try to get or create an event loop for the current thread.
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    error_msg = "Event loop is closed"
                    raise RuntimeError(error_msg)
                cls._current_loop = loop
                return loop
            except RuntimeError:
                # Configure event loop policy if needed.
                cls._configure_event_loop_policy()
                try:
                    loop = asyncio.get_event_loop()
                    cls._current_loop = loop
                    return loop
                except RuntimeError as e:
                    error_msg = "No event loop available"
                    raise RuntimeError(error_msg) from e

    @classmethod
    def isLoopRunning(cls) -> bool:
        """
        Check if an event loop is currently running.

        Returns
        -------
        bool
            True if an event loop is running, otherwise False.
        """
        try:
            # Attempt to get the currently running event loop.
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False

    @classmethod
    def closeLoop(cls) -> None:
        """
        Close the current event loop if it is not running.

        This method closes the current event loop if it exists and is not
        currently running. After closing, the internal reference to the loop
        is set to None.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Close the loop only if it exists and is not running
        if cls._current_loop and not cls._current_loop.is_running():
            cls._current_loop.close()
            cls._current_loop = None

    @staticmethod
    def run(coro: Coroutine[Any, Any, Any]) -> Any:
        """
        Run a coroutine as the main entry point for a CLI application.

        Configure the event loop policy and execute the given coroutine as the
        application's main entry point.

        Parameters
        ----------
        coro : Coroutine[Any, Any, Any]
            Coroutine object to be executed.

        Returns
        -------
        Any
            Result returned by the coroutine.

        Raises
        ------
        TypeError
            If the provided argument is not a coroutine.
        """
        # Validate that the input is a coroutine
        if not inspect.iscoroutine(coro):
            error_msg = "A coroutine object is required"
            raise TypeError(error_msg)
        ReactorLoop._configure_event_loop_policy()
        return asyncio.run(coro)

    @staticmethod
    async def execute(
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a callable, handling both sync and async cases.

        If the callable is synchronous, execute it in the default thread pool
        executor to avoid blocking the event loop. If asynchronous, await it
        directly.

        Parameters
        ----------
        func : Callable[..., Any]
            The function or coroutine to execute.
        *args : Any
            Positional arguments to pass to the callable.
        **kwargs : Any
            Keyword arguments to pass to the callable.

        Returns
        -------
        Any
            The result of the callable, awaited if necessary.

        Raises
        ------
        TypeError
            If func is not callable.
        """
        if not callable(func):
            error_msg = "The provided object is not callable"
            raise TypeError(error_msg)

        # If the function is a coroutine function, await it directly
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)

        # Call the function and check if the result is awaitable
        result = func(*args, **kwargs)

        # Await the result if it is awaitable (e.g., coroutine, future, task)
        if inspect.isawaitable(result):
            return await result

        # For CPU-bound synchronous operations, use thread pool executor
        if inspect.isfunction(func) or inspect.ismethod(func):
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, func, *args, **kwargs)

        return result

    @staticmethod
    @contextmanager
    def eventLoopContext() -> Any:
        """
        Manage the event loop lifecycle within a context.

        Ensures the event loop is properly configured and cleaned up after use.
        Cancels all pending tasks if the loop is not running when exiting.

        Yields
        ------
        asyncio.AbstractEventLoop
            The managed event loop.
        """
        # Ensure the event loop policy is set before acquiring the loop
        ReactorLoop._configure_event_loop_policy()
        loop = ReactorLoop.getEventLoop()
        try:
            yield loop
        finally:
            try:
                # Cancel all pending tasks only if the loop is not running
                if not ReactorLoop.isLoopRunning():
                    pending = asyncio.all_tasks(loop)
                    if pending:
                        for task in pending:
                            task.cancel()
                        # Wait for all tasks to complete cancellation
                        if pending:
                            loop.run_until_complete(
                                asyncio.gather(*pending, return_exceptions=True),
                            )
            except (asyncio.CancelledError, RuntimeError):
                # Suppress expected exceptions during cleanup
                pass

    @classmethod
    async def createTask(
        cls,
        coro: Coroutine[Any, Any, Any],
        *,
        name: str | None = None,
    ) -> asyncio.Task[Any]:
        """
        Create a task from a coroutine in the current event loop.

        Parameters
        ----------
        coro : Coroutine[Any, Any, Any]
            Coroutine to wrap in a task.
        name : str | None, optional
            Name for the task.

        Returns
        -------
        asyncio.Task[Any]
            The created asyncio task.

        Raises
        ------
        RuntimeError
            If no event loop is running.
        """
        # Get the currently running event loop and create a new task
        loop = asyncio.get_running_loop()
        return loop.create_task(coro, name=name)

    @classmethod
    def runSync(cls, coro: Coroutine[Any, Any, Any]) -> Any:
        """
        Run a coroutine synchronously, handling existing event loops.

        Executes a coroutine from synchronous code, even if an event loop is
        already running.

        Parameters
        ----------
        coro : Coroutine[Any, Any, Any]
            The coroutine to execute.

        Returns
        -------
        Any
            The result of the coroutine execution.
        """
        try:
            # If a loop is running, execute the coroutine in a thread pool.
            asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        except RuntimeError:
            # If no loop is running, use the standard run method.
            return cls.run(coro)
