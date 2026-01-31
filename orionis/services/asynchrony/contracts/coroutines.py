from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    import asyncio

T = TypeVar("T")

class ICoroutine(ABC):

    @abstractmethod
    def invoke(
        self,
        *args: object,
        **kwargs: object,
    ) -> T | asyncio.Task | None:
        """
        Invoke the callable coroutine function with provided arguments.

        Execute a callable coroutine function or regular function using the given
        positional and keyword arguments. Automatically detect whether the function
        is asynchronous and adapt execution to the current event loop context.

        Parameters
        ----------
        *args : tuple
            Positional arguments to pass to the callable function.
        **kwargs : dict
            Keyword arguments to pass to the callable function.

        Returns
        -------
        T | asyncio.Task | None
            Result of the coroutine if executed synchronously, an asyncio.Task if
            scheduled for asynchronous execution, or result of a regular callable.

        Raises
        ------
        OrionisCoroutineException
            If an error occurs during coroutine execution or object is not callable.
        RuntimeError
            If an unexpected error occurs during callable execution.

        Notes
        -----
        - Only callable objects can be invoked with this method.
        - For coroutine functions, execution context is automatically detected.
        - Non-coroutine callables are executed directly.
        """

    @abstractmethod
    def run(
        self,
    ) -> T | asyncio.Future[T]:
        """
        Execute the wrapped coroutine with automatic context detection.

        Determine whether to execute the coroutine synchronously or schedule it
        for asynchronous execution based on the presence of an active event loop.
        Validate that the stored object is a coroutine before execution.

        Returns
        -------
        T | asyncio.Future[T]
            The result of the coroutine if executed synchronously, or an
            asyncio.Future if scheduled for asynchronous execution.

        Raises
        ------
        OrionisCoroutineException
            If the stored object is not a coroutine.
        RuntimeError
            If the coroutine cannot be executed due to event loop issues.

        Notes
        -----
        - If called outside an active event loop, the coroutine is executed
          synchronously and its result is returned.
        - If called within an active event loop, the coroutine is scheduled
          for asynchronous execution and a Future is returned.
        - The method automatically detects the execution context and chooses
          the appropriate execution strategy.
        """
