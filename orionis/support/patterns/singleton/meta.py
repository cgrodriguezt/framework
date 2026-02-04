from __future__ import annotations
import threading
import asyncio
from typing import TypeVar

T = TypeVar("T")

class Singleton(type):

    # ruff: noqa: RUF012

    # Class-level dictionary to hold singleton instances
    _instances: dict[type[T], T] = {}
    _lock = threading.Lock()
    _async_lock = asyncio.Lock()

    def __call__(
        cls: type[T],
        *args: object,
        **kwargs: object,
    ) -> T:
        """
        Create or retrieve the singleton instance in a thread-safe manner.

        Parameters
        ----------
        cls : Type[T]
            The class type for which the singleton instance is requested.
        *args : Any
            Positional arguments for the class constructor.
        **kwargs : Any
            Keyword arguments for the class constructor.

        Returns
        -------
        T
            The singleton instance of the class.
        """
        # Check if the instance already exists
        if cls not in cls._instances:
            # Acquire the thread lock to ensure thread safety
            with cls._lock:
                # Double-check if the instance was created while waiting for the lock
                if cls not in cls._instances:
                    # Create and store the singleton instance
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        # Return the singleton instance
        return cls._instances[cls]

    async def __acall__(
        cls: type[T],
        *args: object,
        **kwargs: object,
    ) -> T:
        """
        Retrieve or create the singleton instance asynchronously.

        Ensures only one instance of the class is created in an async-safe manner.
        Acquires an asynchronous lock to prevent race conditions, creates the
        instance if it does not exist, and stores it in the class-level
        `_instances` dictionary.

        Parameters
        ----------
        cls : Type[T]
            The class type for which the singleton instance is requested.
        *args : Any
            Positional arguments for the class constructor.
        **kwargs : Any
            Keyword arguments for the class constructor.

        Returns
        -------
        T
            The singleton instance of the class.
        """
        # Check if the instance already exists
        if cls not in cls._instances:
            # Acquire the asynchronous lock to ensure async safety
            async with cls._async_lock:
                # Double-check if the instance was created while waiting for the lock
                if cls not in cls._instances:
                    # Create and store the singleton instance
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        # Return the singleton instance
        return cls._instances[cls]
