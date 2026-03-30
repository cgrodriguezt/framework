import asyncio
import sys
import inspect
import threading
from typing import Any
from collections.abc import Coroutine, Callable
from contextlib import contextmanager, suppress

class ReactorLoop:

    # ruff: noqa: PLC0415, ANN401, PGH003

    _loop_local = threading.local()
    _uvloop_factory: Callable[[], asyncio.AbstractEventLoop] | None = None
    _uvloop_checked: bool = False
    _loop_lock = threading.Lock()

    @classmethod
    def _detect_uvloop(cls) -> Callable[[], asyncio.AbstractEventLoop] | None:
        """
        Detect and return the uvloop event loop factory if available.

        Returns
        -------
        Callable[[], asyncio.AbstractEventLoop] or None
            The uvloop event loop factory if detected, otherwise None.
        """
        # Check if uvloop has already been checked and cached
        if cls._uvloop_checked:
            return cls._uvloop_factory

        with cls._loop_lock:
            if cls._uvloop_checked:
                return cls._uvloop_factory

            # Attempt to import uvloop if not on Windows
            if sys.platform != "win32":
                with suppress(ImportError):
                    import uvloop  # type: ignore
                    cls._uvloop_factory = uvloop.new_event_loop

            cls._uvloop_checked = True

        return cls._uvloop_factory

    @classmethod
    def _get_loop_factory(cls) -> Callable[[], asyncio.AbstractEventLoop] | None:
        """
        Return the optimal event loop factory for the current platform.

        Returns
        -------
        Callable[[], asyncio.AbstractEventLoop] or None
            The event loop factory suitable for the platform, or None.
        """
        uvloop_factory = cls._detect_uvloop()

        if uvloop_factory:
            return uvloop_factory

        # Use ProactorEventLoop on Windows if available
        if sys.platform == "win32":
            with suppress(AttributeError):
                return asyncio.ProactorEventLoop

        return None

    @classmethod
    def getEventLoop(cls) -> asyncio.AbstractEventLoop:
        """
        Retrieve or create the event loop for the current thread.

        Returns
        -------
        asyncio.AbstractEventLoop
            The event loop associated with the current thread.
        """
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            # Use thread-local storage to cache the loop
            loop = getattr(cls._loop_local, "loop", None)
            if loop and not loop.is_closed():
                return loop

            factory = cls._get_loop_factory()
            loop = factory() if factory else asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            cls._loop_local.loop = loop
            return loop

    @staticmethod
    def run(coro: Coroutine[Any, Any, Any]) -> Any:
        """
        Run a coroutine as the main CLI entry point.

        Parameters
        ----------
        coro : Coroutine[Any, Any, Any]
            The coroutine object to execute.

        Returns
        -------
        Any
            The result returned by the coroutine.
        """
        if not inspect.iscoroutine(coro):
            error_msg = "A coroutine object is required"
            raise TypeError(error_msg)

        factory = ReactorLoop._get_loop_factory()
        if factory:
            # Use asyncio.Runner with custom loop factory if available
            with asyncio.Runner(loop_factory=factory) as runner:
                return runner.run(coro)
        return asyncio.run(coro)

    @staticmethod
    async def execute(
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a callable, handling both sync and async functions.

        Parameters
        ----------
        func : Callable[..., Any]
            The function or coroutine function to execute.
        *args : Any
            Positional arguments to pass to the function.
        **kwargs : Any
            Keyword arguments to pass to the function.

        Returns
        -------
        Any
            The result of the function or coroutine.
        """
        if not callable(func):
            error_msg = "The provided object is not callable"
            raise TypeError(error_msg)

        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)

        # If it's a regular function, run it in the event loop's default executor
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, lambda: func(*args, **kwargs))
        if inspect.isawaitable(result):
            return await result
        return result

    @staticmethod
    @contextmanager
    def eventLoopContext() -> Any:
        """
        Provide a context manager for the event loop.

        Yields
        ------
        asyncio.AbstractEventLoop
            The event loop for the context.
        """
        loop = ReactorLoop.getEventLoop()
        try:
            yield loop
        finally:
            try:
                # Cancel all pending tasks if the loop is not running
                if not ReactorLoop.isLoopRunning():
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()
                    if pending:
                        loop.run_until_complete(
                            asyncio.gather(*pending, return_exceptions=True)
                        )
            except (RuntimeError, asyncio.CancelledError):
                pass

    @staticmethod
    def isLoopRunning() -> bool:
        """
        Determine whether an event loop is currently running.

        Returns
        -------
        bool
            True if an event loop is running, False otherwise.
        """
        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False

    @classmethod
    async def createTask(
        cls,
        coro: Coroutine[Any, Any, Any],
        *,
        name: str | None = None,
    ) -> asyncio.Task[Any]:
        """
        Create and schedule a new asyncio task for the given coroutine.

        Parameters
        ----------
        coro : Coroutine[Any, Any, Any]
            The coroutine to schedule as a task.
        name : str or None, optional
            The name of the task.

        Returns
        -------
        asyncio.Task[Any]
            The created asyncio task.
        """
        loop = asyncio.get_running_loop()
        return loop.create_task(coro, name=name)

    @classmethod
    def runSync(cls, coro: Coroutine[Any, Any, Any]) -> Any:
        """
        Run a coroutine synchronously, using a thread pool if needed.

        Parameters
        ----------
        coro : Coroutine[Any, Any, Any]
            The coroutine to execute.

        Returns
        -------
        Any
            The result returned by the coroutine.
        """
        try:
            asyncio.get_running_loop()
            import concurrent.futures
            # Run the coroutine in a separate thread if already in an event loop
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(cls.run, coro)
                return future.result()
        except RuntimeError:
            return cls.run(coro)