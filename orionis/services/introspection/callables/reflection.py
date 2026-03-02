from __future__ import annotations
import inspect
from typing import TYPE_CHECKING
from orionis.services.introspection.callables.contracts.reflection import (
    IReflectionCallable,
)
from orionis.services.introspection.dependencies.reflection import ReflectDependencies

if TYPE_CHECKING:
    from orionis.services.introspection.dependencies.entities.signature import (
        Signature,
    )

class ReflectionCallable(IReflectionCallable):

    def __init__(self, fn: callable) -> None:
        """
        Initialize the reflection wrapper with a callable object.

        Parameters
        ----------
        fn : callable
            The function, method, or lambda to be wrapped.

        Raises
        ------
        TypeError
            If `fn` is not a function, method, or lambda.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Validate that the input is a proper callable with introspectable attributes
        if not (
            inspect.isfunction(fn)
            or inspect.ismethod(fn)
            or (callable(fn) and hasattr(fn, "__code__"))
        ):
            error_msg = (
                f"Expected a function, method, or lambda, got {type(fn).__name__}"
            )
            raise TypeError(error_msg)
        # Store the callable for reflection operations
        self.__function = fn
        # Initialize an internal cache for storing computed properties
        self.__memory_cache: dict = {}

    def __getitem__(self, key: str) -> object | None:
        """
        Retrieve a cached value by key.

        Parameters
        ----------
        key : str
            The key to look up in the cache.

        Returns
        -------
        object or None
            The cached value if found, otherwise None.
        """
        # Return the value from the memory cache for the given key
        return self.__memory_cache.get(key, None)

    def __setitem__(self, key: str, value: object) -> None:
        """
        Store a value in the cache with the specified key.

        Parameters
        ----------
        key : str
            The key under which to store the value.
        value : object
            The value to store in the cache.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Set the value in the memory cache for the given key
        self.__memory_cache[key] = value

    def __contains__(self, key: str) -> bool:
        """
        Check if the cache contains the specified key.

        Parameters
        ----------
        key : str
            The key to check for existence in the cache.

        Returns
        -------
        bool
            True if the key exists in the cache, False otherwise.
        """
        # Return True if the key is present in the memory cache
        return key in self.__memory_cache

    def __delitem__(self, key: str) -> None:
        """
        Remove an item from the memory cache by key.

        Parameters
        ----------
        key : str
            The key to remove from the cache.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Remove the key from the cache if present
        self.__memory_cache.pop(key, None)

    def getCallable(self) -> callable:
        """
        Return the callable function associated with this instance.

        Returns
        -------
        callable
            The function object encapsulated by this instance.
        """
        return self.__function

    def getName(self) -> str:
        """
        Return the name of the callable.

        Returns
        -------
        str
            Name of the function as defined in its declaration.
        """
        return self.__function.__name__

    def getModuleName(self) -> str:
        """
        Return the module name where the callable is defined.

        Returns
        -------
        str
            The name of the module in which the function was declared.
        """
        return self.__function.__module__

    def getModuleWithCallableName(self) -> str:
        """
        Return the fully qualified name of the callable.

        Combines the module name and callable name to create a complete identifier.

        Returns
        -------
        str
            The module and callable name separated by a dot.
        """
        # Combine module and function name for a fully qualified identifier
        return f"{self.getModuleName()}.{self.getName()}"

    def getDocstring(self) -> str:
        """
        Return the docstring of the callable.

        Returns
        -------
        str
            The docstring of the function, or an empty string if not present.
        """
        # Return the function's docstring or an empty string if missing
        return self.__function.__doc__ or ""

    def getSourceCode(self) -> str:
        """
        Retrieve the source code of the wrapped callable.

        Uses Python's inspect module to extract the complete source code of the
        callable function from its definition file.

        Returns
        -------
        str
            The source code of the callable function as a string.

        Raises
        ------
        AttributeError
            If the source code cannot be obtained due to an OSError or if the
            callable is built-in without accessible source.
        """
        # Return cached source code if available
        if "source_code" in self:
            return self["source_code"]

        try:
            # Get and cache the source code
            self["source_code"] = inspect.getsource(self.__function)
            return self["source_code"]
        except OSError as e:
            error_msg = f"Could not retrieve source code: {e}"
            raise AttributeError(error_msg) from e

    def getFile(self) -> str:
        """
        Retrieve the absolute path to the source file of the callable.

        Returns
        -------
        str
            Absolute path to the file containing the callable.

        Raises
        ------
        TypeError
            If the callable is built-in or its file cannot be determined.
        """
        # Return cached file path if available
        if "file" in self:
            return self["file"]

        # Cache and return the file path of the callable
        self["file"] = inspect.getfile(self.__function)
        return self["file"]

    def getSignature(self) -> inspect.Signature:
        """
        Return the signature of the callable.

        Returns
        -------
        inspect.Signature
            The signature object representing the callable's parameters,
            default values, and type annotations.
        """
        # Return cached signature if available
        if "signature" in self:
            return self["signature"]

        # Cache and return the signature of the callable
        self["signature"] = inspect.signature(self.__function)
        return self["signature"]

    def getDependencies(self) -> Signature:
        """
        Analyze and return dependency information for the callable.

        Parameters
        ----------
        self : ReflectionCallable
            The instance of the ReflectionCallable.

        Returns
        -------
        Signature
            Contains resolved and unresolved dependencies for the callable.
        """
        # Return cached dependencies if available
        if "dependencies" in self:
            return self["dependencies"]

        # Analyze and cache dependencies using ReflectDependencies
        self["dependencies"] = ReflectDependencies(
            self.__function,
        ).callableSignature()
        return self["dependencies"]

    def clearCache(self) -> None:
        """
        Clear all cached reflection data.

        Removes all cached entries stored in the reflection instance. Forces
        fresh computation on subsequent method calls.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Clear the internal memory cache for reflection results
        self.__memory_cache.clear()
