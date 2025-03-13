import asyncio
from typing import Any, Callable

class AsyncExecutor:

    @staticmethod
    def run(callback: Callable[..., Any]) -> None:
        """
        Runs a coroutine synchronously.

        Parameters
        ----------
        callback : Callable[..., Any]
            The coroutine to run.
        """
        try:
            loop = asyncio.get_running_loop()
            loop.run_until_complete(callback())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(callback())