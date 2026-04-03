from __future__ import annotations
import asyncio
import functools
import inspect
from typing import TYPE_CHECKING
from orionis.support.background.contracts.task import IBackgroundTask

if TYPE_CHECKING:
    from collections.abc import Callable

class BackgroundTask(IBackgroundTask):
    """
    Represent a background task that can be executed asynchronously.

    Parameters
    ----------
    func : Callable
        The function to be executed in the background.
    *args : Any
        Positional arguments to pass to the function.
    **kwargs : Any
        Keyword arguments to pass to the function.
    """

    def __init__(
        self,
        func: Callable,
        *args: object,
        **kwargs: object,
    ) -> None:
        """
        Initialize the BackgroundTask instance.

        Parameters
        ----------
        func : Callable
            The function to be executed in the background.
        *args : Any
            Positional arguments to pass to the function.
        **kwargs : Any
            Keyword arguments to pass to the function.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.__func = func
        self.__args = args
        self.__kwargs = kwargs
        self.__is_async = inspect.iscoroutinefunction(func)

    async def __call__(self) -> None:
        """
        Execute the background task, handling both sync and async functions.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Await the coroutine function directly
        if self.__is_async:
            await self.__func(*self.__args, **self.__kwargs)  # type: ignore[arg-type]
        # Run the synchronous function in a thread pool executor.
        # functools.partial is required because run_in_executor only
        # accepts positional arguments and does not forward **kwargs.
        else:
            loop = asyncio.get_running_loop()
            bound = functools.partial(
                self.__func, *self.__args, **self.__kwargs,  # type: ignore[arg-type]
            )
            await loop.run_in_executor(None, bound)

    async def run(self) -> None:
        """
        Run the background task.

        Returns
        -------
        None
            This method does not return a value.
        """
        await self()
