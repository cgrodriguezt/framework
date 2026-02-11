from __future__ import annotations
import fnmatch
import inspect
import unittest
from collections.abc import Callable
from typing import TYPE_CHECKING, Any
from orionis.support.facades.application import Application

if TYPE_CHECKING:
    from collections.abc import Callable

class TestCase(unittest.IsolatedAsyncioTestCase):

    __method_pattern: str = "test*"

    @classmethod
    def setMethodPattern(cls, pattern: str) -> None:
        """
        Set the method pattern for identifying test methods.

        Parameters
        ----------
        pattern : str
            The glob pattern to match test method names (e.g., "test*").
        """
        cls.__method_pattern = pattern

    def _resolveTest(self, method: Callable[..., Any]) -> Callable[..., Any]:
        """
        Wrap a test method to initialize the application context before execution.

        Parameters
        ----------
        method : Callable[..., Any]
            The test method to be wrapped.

        Returns
        -------
        Callable[..., Any]
            An asynchronous wrapper that invokes the test method within the
            application context.
        """
        # Wrapper ensures application context is initialized before test execution.
        async def wrapper(*args: object, **kwargs: object) -> object:
            """
            Invoke the test method within the application context.

            Parameters
            ----------
            *args : object
                Positional arguments for the test method.
            **kwargs : object
                Keyword arguments for the test method.

            Returns
            -------
            object
                The result of the invoked test method.
            """
            # Call the test method using the application context.
            return await Application.invoke(method, *args, **kwargs)

        # Preserve original method metadata for test reporting.
        return wrapper

    def __getattribute__(self, name: str) -> object:
        """
        Retrieve an attribute and wrap test methods for application context.

        Parameters
        ----------
        name : str
            The name of the attribute to retrieve.

        Returns
        -------
        object
            The attribute value. Test methods are wrapped for application context
            execution; other attributes are returned directly.
        """
        # Retrieve the attribute using the superclass method.
        attr: object = super().__getattribute__(name)

        # Return non-test or private attributes directly.
        if name.startswith("_") or not (
            inspect.ismethod(attr) or inspect.isfunction(attr)
        ):
            return attr

        # Wrap test methods to ensure application context.
        if fnmatch.fnmatch(name, self.__method_pattern):
            return self._resolveTest(attr)

        # Return the original attribute for non-test methods.
        return attr
