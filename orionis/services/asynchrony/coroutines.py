from __future__ import annotations
import asyncio
import inspect
from typing import TYPE_CHECKING, Any, TypeVar
from orionis.services.asynchrony.contracts.coroutines import ICoroutine

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Coroutine as TypingCoroutine

T = TypeVar("T")

class Coroutine(ICoroutine):

    def __init__(
        self,
        func: (
            TypingCoroutine[Any, Any, T] |
            Callable[..., TypingCoroutine[Any, Any, T]]
        ),
    ) -> None:
        """
        Initialize a Coroutine wrapper to manage coroutine objects or functions.

        This constructor accepts either a coroutine object or a callable that
        returns a coroutine. The wrapped coroutine or function can be executed
        later using the run() or invoke() methods.

        Parameters
        ----------
        func : TypingCoroutine[Any, Any, T] |
               Callable[..., TypingCoroutine[Any, Any, T]]
            A coroutine object or a callable that returns a coroutine object.

        Returns
        -------
        None
            No return value. Initializes the instance state.

        Notes
        -----
        - Type validation is deferred until execution.
        - Accepts both coroutine objects and coroutine functions.
        """
        # Store the coroutine object or callable for later execution
        self.__func = func

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
        TypeError
            If an error occurs during coroutine execution or object is not callable.
        RuntimeError
            If an unexpected error occurs during callable execution.

        Notes
        -----
        - Only callable objects can be invoked with this method.
        - For coroutine functions, execution context is automatically detected.
        - Non-coroutine callables are executed directly.
        """
        # Validate that the stored object is callable before invocation
        if not callable(self.__func):
            error_msg = (
                f"Cannot invoke non-callable object of type "
                f"{type(self.__func).__name__}"
            )
            raise TypeError(error_msg)

        try:
            # Check if the callable is a coroutine function
            if asyncio.iscoroutinefunction(self.__func):
                # Create the coroutine object using provided arguments
                coroutine_obj = self.__func(*args, **kwargs)

                try:
                    # Attempt to get the currently running event loop
                    loop = asyncio.get_running_loop()

                    # Schedule coroutine for async execution and return Task
                    return loop.create_task(coroutine_obj)

                except RuntimeError:
                    # No running event loop; execute coroutine synchronously
                    try:
                        # Use asyncio.run to execute coroutine and return result
                        return asyncio.run(coroutine_obj)

                    except Exception as e:
                        # Wrap exceptions that occur during synchronous execution
                        error_msg = f"Failed to execute coroutine synchronously: {e!s}"
                        raise RuntimeError(error_msg) from e

            else:
                # Execute regular callable directly and return its result
                return self.__func(*args, **kwargs)

        except TypeError:
            # Re-raise TypeError exceptions as-is
            raise

        except Exception as e:
            # Wrap any other exceptions that occur during invocation
            error_msg = f"Unexpected error during callable invocation: {e!s}"
            raise RuntimeError(error_msg) from e

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
        TypeError
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
        # Validate that the provided object is a coroutine
        if not inspect.iscoroutine(self.__func):
            error_msg = (
                f"Expected a coroutine object, but got "
                f"{type(self.__func).__name__}."
            )
            raise TypeError(error_msg)

        # Attempt to get the currently running event loop
        try:
            loop = asyncio.get_running_loop()

        # No running event loop; execute the coroutine synchronously
        except RuntimeError:
            return asyncio.run(self.__func)

        # If inside an active event loop, schedule the coroutine
        if loop.is_running():
            return asyncio.ensure_future(self.__func)

        # If no event loop is running, execute using the loop
        return loop.run_until_complete(self.__func)
