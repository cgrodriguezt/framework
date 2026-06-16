import asyncio
import concurrent.futures
import functools
import inspect
import sys
import threading
import types
from typing import Any
from typing import TYPE_CHECKING
from contextlib import contextmanager, suppress

if TYPE_CHECKING:
    from collections.abc import Coroutine, Callable

# Get the appropriate function to retrieve the running event loop,
# depending on Python version.
_get_running_loop: Any = getattr(asyncio, "_get_running_loop")  # noqa: B009

# Sentinel to distinguish "not yet computed" from None (a valid factory result).
_Unset: object = object()

# CO_COROUTINE flag — stable in CPython since 3.5+
_CO_COROUTINE: int = 0x100

def _is_coroutine_function(func: object) -> bool:
    """
    Check whether a callable is a coroutine function.

    Use the ``CO_COROUTINE`` flag for speed; fall back to
    ``inspect.iscoroutinefunction`` for wrapped callables that lack
    a ``__code__`` attribute.

    Parameters
    ----------
    func : object
        The callable to inspect.

    Returns
    -------
    bool
        True if *func* is a coroutine function, False otherwise.
    """
    try:
        return bool(func.__code__.co_flags & _CO_COROUTINE)
    except AttributeError:
        return inspect.iscoroutinefunction(func)

class ReactorLoop:

    # ruff: noqa: PLC0415, ANN401, PGH003

    # Per-thread event loop cache; avoids cross-thread loop sharing.
    _loop_local = threading.local()

    # Cached uvloop factory; None until detection runs.
    _uvloop_factory: Callable[[], asyncio.AbstractEventLoop] | None = None

    # Guard to run uvloop detection only once across all threads.
    _uvloop_checked: bool = False

    # Protects uvloop detection and factory caching from race conditions.
    _loop_lock = threading.Lock()

    # Shared single-worker pool for sync↔async bridging; created on demand.
    _sync_executor: concurrent.futures.ThreadPoolExecutor | None = None

    # Protects lazy initialisation of _sync_executor.
    _sync_executor_lock: threading.Lock = threading.Lock()

    # True when running on Windows; evaluated once at import time.
    _IS_WIN32: bool = sys.platform == "win32"

    # Cached loop factory result; _Unset means not yet resolved.
    _loop_factory_cached: Any = _Unset

    @classmethod
    def _detectUvloop(cls) -> Callable[[], asyncio.AbstractEventLoop] | None:
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
                try:
                    import uvloop  # type: ignore
                    cls._uvloop_factory = uvloop.new_event_loop
                except ImportError:
                    pass

            cls._uvloop_checked = True

        return cls._uvloop_factory

    @classmethod
    def _getLoopFactory(cls) -> Callable[[], asyncio.AbstractEventLoop] | None:
        """
        Return the optimal event loop factory for the current platform.

        Returns
        -------
        Callable[[], asyncio.AbstractEventLoop] or None
            The event loop factory suitable for the platform, or None.
        """
        if cls._loop_factory_cached is not _Unset:
            return cls._loop_factory_cached  # type: ignore[return-value]

        uvloop_factory = cls._detectUvloop()
        if uvloop_factory:
            cls._loop_factory_cached = uvloop_factory
            return uvloop_factory

        result: Callable[[], asyncio.AbstractEventLoop] | None = None
        if cls._IS_WIN32:
            with suppress(AttributeError):
                result = asyncio.ProactorEventLoop

        cls._loop_factory_cached = result
        return result

    @classmethod
    def getEventLoop(cls) -> asyncio.AbstractEventLoop:
        """
        Retrieve or create the event loop for the current thread.

        Returns
        -------
        asyncio.AbstractEventLoop
            The event loop associated with the current thread.
        """
        running: asyncio.AbstractEventLoop | None = _get_running_loop()
        if running is not None:
            return running

        # Use thread-local storage to cache the loop
        loop = cls._loop_local.__dict__.get("loop")
        if loop and not loop.is_closed():
            return loop

        factory = cls._getLoopFactory()
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
        if not isinstance(coro, types.CoroutineType):
            error_msg = "A coroutine object is required"
            raise TypeError(error_msg)

        factory = ReactorLoop._getLoopFactory()
        try:
            if factory:
                # Use asyncio.Runner with custom loop factory if available
                with asyncio.Runner(loop_factory=factory) as runner:
                    return runner.run(coro)
            return asyncio.run(coro)
        except KeyboardInterrupt:
            # Ctrl+C during a long-running command (e.g. serve) is a normal
            # exit signal, not an error. Return 0 so the process exits cleanly.
            return 0

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

        if _is_coroutine_function(func):
            return await func(*args, **kwargs)

        # If it's a regular function, run it in the event loop's default executor
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, functools.partial(func, *args, **kwargs),
        )
        if hasattr(result, "__await__"):
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
                if not loop.is_running() and (pending := asyncio.all_tasks(loop)):
                    for task in pending:
                        task.cancel()
                    loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True),
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
        return _get_running_loop() is not None

    @staticmethod
    async def createTask(
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
        return asyncio.get_running_loop().create_task(coro, name=name)

    @classmethod
    def _getSyncExecutor(cls) -> concurrent.futures.ThreadPoolExecutor:
        """
        Return the reusable single-worker pool for sync↔async bridging.

        Create the pool on first call and cache it for subsequent calls.

        Returns
        -------
        concurrent.futures.ThreadPoolExecutor
            A thread pool with a single worker dedicated to running coroutines
            from synchronous contexts.
        """
        if cls._sync_executor is None:
            with cls._sync_executor_lock:
                if cls._sync_executor is None:
                    cls._sync_executor = concurrent.futures.ThreadPoolExecutor(
                        max_workers=1,
                        thread_name_prefix="orionis-sync",
                    )
        return cls._sync_executor

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
        if _get_running_loop() is None:
            return cls.run(coro)

        # Already inside a running loop — dispatch to the reusable single-worker pool
        return cls._getSyncExecutor().submit(cls.run, coro).result()
