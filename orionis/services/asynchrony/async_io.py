import asyncio
from typing import Callable, Any

class Async:

    @staticmethod
    def getOrCreateEventLoop() -> asyncio.AbstractEventLoop:
        """
        Get or create an asyncio event loop.

        Attempts to retrieve the currently running event loop. If none exists,
        creates a new event loop and sets it as the default.

        Returns
        -------
        asyncio.AbstractEventLoop
            The running or newly created event loop.
        """
        try:
            # Try to get the currently running event loop
            return asyncio.get_running_loop()
        except RuntimeError:
            # No running loop; create and set a new event loop as default
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    @staticmethod
    def isCoroutineFunction(func: object) -> bool:
        """
        Check if the given object is a coroutine function.

        Parameters
        ----------
        func : object
            The object to check.

        Returns
        -------
        bool
            True if the object is a coroutine function, otherwise False.
        """
        return asyncio.iscoroutinefunction(func)

    @staticmethod
    def runSyncOrAwait(
        callback: Callable[[], Any],
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> Any:
        """
        Execute a function or coroutine synchronously.

        If the callback is a coroutine function, execute it in the event loop
        until completion. If it is a regular function, call it directly.

        Parameters
        ----------
        callback : Callable[[], Any]
            The function or coroutine to execute.
        loop : asyncio.AbstractEventLoop or None, optional
            The event loop to use. If None, a new or existing loop is used.

        Returns
        -------
        Any
            The result of the function or coroutine execution.

        Raises
        ------
        TypeError
            If the callback is not callable.
        """
        # Obtain or create the event loop for coroutine execution
        if not callable(callback):
            error_msg = "callback must be a callable object"
            raise TypeError(error_msg)

        # Check if the callback is a coroutine function
        if Async.isCoroutineFunction(callback):
            if not loop:
                loop = Async.getOrCreateEventLoop()
            return loop.run_until_complete(callback())

        # If it's a regular function, call it directly
        else:
            return callback()