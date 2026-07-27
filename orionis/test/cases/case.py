from __future__ import annotations
import fnmatch
import functools
import re
import unittest
from typing import TYPE_CHECKING
from orionis.support.facades.application import Application

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

# Lifecycle hooks that must never be wrapped regardless of naming pattern.
_LIFECYCLE_HOOKS: frozenset[str] = frozenset({
    "setUp", "tearDown",
    "setUpClass", "tearDownClass",
    "asyncSetUp", "asyncTearDown",
})

# Precompiled regex for the default glob pattern avoids repeated fnmatch compilation.
_DEFAULT_PATTERN: re.Pattern[str] = re.compile(fnmatch.translate("test*"))


class TestCase(unittest.IsolatedAsyncioTestCase): # NOSONAR

    # Class-level compiled regex; updated by setMethodPattern.
    _method_regex: re.Pattern[str] = _DEFAULT_PATTERN

    @classmethod
    def setMethodPattern(cls, pattern: str) -> None:
        """
        Set the method pattern for identifying test methods.

        Parameters
        ----------
        pattern : str
            The glob pattern to match test method names (e.g., "test*").
        """
        # Store the raw pattern and compile it once for all future lookups.
        cls._method_regex = re.compile(fnmatch.translate(pattern))

    def __init__(self, method_name: str = "runTest") -> None:
        """
        Initialize the test case and eagerly wrap the designated test method.

        Parameters
        ----------
        method_name : str, optional
            Name of the test method to run, by default "runTest".
        """
        super().__init__(method_name)

        # Wrap the single test method once at construction instead of
        # intercepting every attribute access via __getattribute__.
        _regex: re.Pattern[str] = getattr(type(self), "_method_regex", _DEFAULT_PATTERN)
        if (
            not method_name.startswith("_")
            and method_name not in _LIFECYCLE_HOOKS
            and _regex.match(method_name) is not None
        ):
            original = object.__getattribute__(self, method_name)
            if callable(original):
                object.__setattr__(self, method_name, self._resolveTest(original))

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
        @functools.wraps(method)
        async def wrapper(*args: object, **kwargs: object) -> object:
            # Execute the test method inside the application context.
            return await Application.invoke(method, *args, **kwargs)

        return wrapper
