from __future__ import annotations
import inspect
import keyword
from typing import Any, TYPE_CHECKING
from orionis.services.introspection.abstract.contracts.reflection import (
    IReflectionAbstract,
)
from orionis.services.introspection.dependencies.reflection import ReflectDependencies

if TYPE_CHECKING:
    from orionis.services.introspection.dependencies.entities.signature import (
        SignatureArguments,
    )

class ReflectionAbstract(IReflectionAbstract):

    # ruff: noqa: PERF401

    def __init__(self, abstract: type) -> None:
        """
        Initialize the reflection utility for an abstract base class.

        Parameters
        ----------
        abstract : type
            The abstract base class to reflect. Must inherit from abc.ABC.

        Raises
        ------
        TypeError
            If the class is not an abstract base class.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Ensure the provided class is abstract
        if not inspect.isabstract(abstract):
            error_msg = (
                f"The class '{abstract.__name__}' is not an abstract base class."
            )
            raise TypeError(error_msg)
        # Store the abstract class for reflection
        self.__abstract: type = abstract
        # Initialize memory cache for reflection results
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

    def getClass(self) -> type:
        """
        Return the class type associated with this reflection instance.

        Returns
        -------
        Type
            The abstract base class type provided during initialization.
        """
        # Return the abstract class type stored in the instance
        return self.__abstract

    def getClassName(self) -> str:
        """
        Return the name of the reflected abstract class.

        Returns
        -------
        str
            The name of the abstract class provided during initialization.
        """
        # Return the name of the abstract class
        return self.__abstract.__name__

    def getModuleName(self) -> str:
        """
        Return the module name of the reflected abstract class.

        Returns
        -------
        str
            The fully qualified module name containing the abstract class.
        """
        # Return the module name of the abstract class
        return self.__abstract.__module__

    def getModuleWithClassName(self) -> str:
        """
        Return the fully qualified name of the abstract class.

        Returns
        -------
        str
            The module path and class name separated by a dot, such as
            'module.submodule.ClassName'.
        """
        # Concatenate module name and class name for fully qualified name
        return f"{self.getModuleName()}.{self.getClassName()}"

    def getDocstring(self) -> str | None:
        """
        Retrieve the docstring for the reflected abstract class.

        Returns
        -------
        str or None
            The docstring of the abstract class, or None if not available.
        """
        # Return the class docstring if present, otherwise None
        return self.__abstract.__doc__ if self.__abstract.__doc__ else None

    def getBaseClasses(self) -> list[type]:
        """
        Return the direct base classes of the reflected abstract class.

        Returns
        -------
        list of type
            List of direct base classes for the abstract class.
        """
        # Return the tuple of base classes as a list
        return list(self.__abstract.__bases__)

    def getSourceCode(self) -> str:
        """
        Retrieve the source code of the reflected abstract class.

        Parameters
        ----------
        None

        Returns
        -------
        str
            The complete source code of the abstract class as a string.

        Raises
        ------
        ValueError
            If the source code cannot be retrieved due to file system errors or
            other unexpected exceptions.
        """
        # Return cached source code if available
        if "source_code" in self:
            return self["source_code"]

        # Attempt to get the source code of the abstract class
        try:
            self["source_code"] = inspect.getsource(self.__abstract)
            return self["source_code"]
        except OSError as e:
            error_msg = (
                f"Could not retrieve source code for '{self.__abstract.__name__}': {e}"
            )
            raise ValueError(error_msg) from e
        except Exception as e:
            error_msg = (
                f"An unexpected error occurred while retrieving source code for "
                f"'{self.__abstract.__name__}': {e}"
            )
            raise ValueError(error_msg) from e

    def getFile(self) -> str:
        """
        Retrieve the absolute file path of the reflected abstract class.

        Parameters
        ----------
        None

        Returns
        -------
        str
            The absolute file path containing the abstract class definition.

        Raises
        ------
        ValueError
            If the file path cannot be retrieved due to type errors or other
            unexpected exceptions.
        """
        # Return cached file path if available
        if "file_path" in self:
            return self["file_path"]

        # Attempt to get the file path of the abstract class
        try:
            self["file_path"] = inspect.getfile(self.__abstract)
            return self["file_path"]
        except TypeError as e:
            error_msg = (
                f"Could not retrieve file for '{self.__abstract.__name__}': {e}"
            )
            raise ValueError(error_msg) from e
        except Exception as e:
            error_msg = (
                f"An unexpected error occurred while retrieving file for "
                f"'{self.__abstract.__name__}': {e}"
            )
            raise ValueError(error_msg) from e

    def getAnnotations(self) -> dict:
        """
        Retrieve type annotations for class attributes.

        Returns
        -------
        dict
            Dictionary mapping attribute names to their annotated types.
            Private attribute names are normalized by removing name mangling
            prefixes.
        """
        # Collect type annotations, normalizing private attribute names
        annotations: dict = {}
        for k, v in getattr(self.__abstract, "__annotations__", {}).items():
            # Remove class name prefix for private attributes
            normalized_key = str(k).replace(f"_{self.getClassName()}", "")
            annotations[normalized_key] = v
        return annotations

    def hasAttribute(self, attribute: str) -> bool:
        """
        Check if the class has a specific attribute.

        Parameters
        ----------
        attribute : str
            The name of the attribute to check.

        Returns
        -------
        bool
            True if the attribute exists, False otherwise.
        """
        # Check for attribute existence in class attributes
        return attribute in self.getAttributes()

    def getAttribute(self, attribute: str) -> object | None:
        """
        Retrieve the value of a class attribute.

        Parameters
        ----------
        attribute : str
            Name of the attribute to retrieve.

        Returns
        -------
        object or None
            Value of the specified class attribute, or None if not found.

        Raises
        ------
        ValueError
            If the attribute does not exist or is inaccessible.
        """
        # Get all class attributes (excluding methods and properties)
        attrs = self.getAttributes()
        # Retrieve the attribute value if it exists
        return attrs.get(attribute, None)

    def setAttribute(self, name: str, value: object) -> bool:
        """
        Set the value of a class attribute.

        Parameters
        ----------
        name : str
            Name of the attribute to set. Must be a valid Python identifier and
            not a reserved keyword.
        value : object
            Value to assign to the attribute. Must not be callable.

        Returns
        -------
        bool
            True if the attribute was successfully set.

        Raises
        ------
        ValueError
            If the attribute name is invalid, is a Python keyword, or if the
            value is callable.
        """
        # Validate attribute name and ensure it is not a keyword
        if (
            not isinstance(name, str) or
            not name.isidentifier() or
            keyword.iskeyword(name)
        ):
            error_msg = (
                f"Invalid attribute name '{name}'. Must be a valid Python identifier "
                "and not a keyword."
            )
            raise ValueError(error_msg)

        # Prevent setting callable objects as attributes
        if callable(value):
            error_msg = (
                f"Cannot set attribute '{name}' to a callable. Use setMethod instead."
            )
            raise TypeError(error_msg)

        # Handle name mangling for private attributes
        if name.startswith("__") and not name.endswith("__"):
            class_name = self.getClassName()
            name = f"_{class_name}{name}"

        # Set the attribute on the class
        setattr(self.__abstract, name, value)

        # Invalidate cached attributes
        del self["attributes"]

        # Indicate successful setting of the attribute
        return True

    def removeAttribute(self, name: str) -> bool:
        """
        Remove an attribute from the reflected abstract class.

        Parameters
        ----------
        name : str
            Name of the attribute to remove.

        Returns
        -------
        bool
            True if the attribute was successfully removed.

        Raises
        ------
        ValueError
            If the attribute does not exist or cannot be removed.
        """
        # Check if the attribute exists in the class attributes
        if not self.hasAttribute(name):
            error_msg = (
                f"Attribute '{name}' does not exist in class '{self.getClassName()}'."
            )
            raise ValueError(error_msg)

        # Handle private attribute name mangling for correct attribute resolution
        if name.startswith("__") and not name.endswith("__"):
            class_name = self.getClassName()
            name = f"_{class_name}{name}"

        # Remove the attribute from the class
        delattr(self.__abstract, name)

        # Invalidate cached attributes
        del self["attributes"]

        # Indicate successful removal
        return True

    def getAttributes(self) -> dict:
        """
        Aggregate all class-level attributes.

        Combines public, protected, private, and dunder attributes into a single
        dictionary. Excludes callable objects, static/class methods, and properties.

        Returns
        -------
        dict
            Dictionary mapping attribute names to their values.
        """
        # Return cached attributes if available
        if "attributes" in self:
            return self["attributes"]

        # Aggregate attributes from all visibility levels
        self["attributes"] = {
            **self.getPublicAttributes(),
            **self.getProtectedAttributes(),
            **self.getPrivateAttributes(),
            **self.getDunderAttributes(),
        }
        return self["attributes"]

    def getPublicAttributes(self) -> dict:
        """
        Retrieve all public class-level attributes.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary mapping public attribute names to their values. Only includes
            attributes that do not start with underscores and are not callable,
            static methods, class methods, or properties.
        """
        # Return cached public attributes if available
        if "public_attributes" in self:
            return self["public_attributes"]

        class_name: str = self.getClassName()
        attributes: dict[str, Any] = self.__abstract.__dict__
        public: dict = {}

        # Filter out non-public attributes and callables
        for attr, value in attributes.items():
            if callable(value) or isinstance(
                value, (staticmethod, classmethod, property),
            ):
                continue
            if attr.startswith("__") and attr.endswith("__"):
                continue
            if attr.startswith(f"_{class_name}"):
                continue
            if attr.startswith("_"):
                continue
            public[attr] = value

        self["public_attributes"] = public
        return self["public_attributes"]

    def getProtectedAttributes(self) -> dict:
        """
        Retrieve all protected class-level attributes.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary mapping protected attribute names to their values. Only
            attributes that start with a single underscore, are not dunder,
            private, callable, static/class methods, or properties.
        """
        # Return cached protected attributes if available
        if "protected_attributes" in self:
            return self["protected_attributes"]

        class_name: str = self.getClassName()
        attributes: dict[str, Any] = self.__abstract.__dict__
        protected: dict[str, Any] = {}

        # Filter for protected attributes only
        for attr, value in attributes.items():
            # Skip callables, static/class methods, and properties
            if (
                callable(value)
                or isinstance(value, (staticmethod, classmethod, property))
            ):
                continue
            # Skip dunder attributes
            if attr.startswith("__") and attr.endswith("__"):
                continue
            # Skip private attributes (name-mangled)
            if attr.startswith(f"_{class_name}"):
                continue
            # Only include attributes that start with a single underscore
            if not attr.startswith("_"):
                continue
            # Exclude internal abc attributes
            if attr.startswith("_abc_"):
                continue
            protected[attr] = value

        self["protected_attributes"] = protected
        return self["protected_attributes"]

    def getPrivateAttributes(self) -> dict:
        """
        Retrieve all private class-level attributes.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary mapping private attribute names (with name mangling
            removed) to their values. Only includes attributes starting with
            _ClassName that are not callable, static methods, class methods,
            or properties.
        """
        # Return cached private attributes if available
        if "private_attributes" in self:
            return self["private_attributes"]

        class_name: str = self.getClassName()
        attributes: dict[str, Any] = self.__abstract.__dict__
        private: dict[str, Any] = {}

        # Filter for name-mangled private attributes only
        for attr, value in attributes.items():
            if (
                callable(value)
                or isinstance(value, (staticmethod, classmethod, property))
            ):
                continue
            if attr.startswith(f"_{class_name}"):
                private[str(attr).replace(f"_{class_name}", "")] = value

        self["private_attributes"] = private
        return self["private_attributes"]

    def getDunderAttributes(self) -> dict:
        """
        Retrieve dunder (double underscore) class-level attributes.

        Returns
        -------
        dict
            Dictionary mapping dunder attribute names to their values. Only
            includes attributes that start and end with double underscores,
            are not callable, static methods, class methods, or properties,
            and are not in the excluded built-in list.
        """
        # Return cached dunder attributes if available
        if "dunder_attributes" in self:
            return self["dunder_attributes"]

        attributes: dict[str, Any] = self.__abstract.__dict__
        dunder: dict[str, Any] = {}

        # List of built-in dunder attributes to exclude
        exclude: list[str] = [
            "__class__", "__delattr__", "__dir__", "__doc__", "__eq__", "__format__",
            "__ge__", "__getattribute__", "__gt__", "__hash__", "__init__",
            "__init_subclass__", "__le__", "__lt__", "__module__", "__ne__", "__new__",
            "__reduce__", "__reduce_ex__", "__repr__", "__setattr__", "__sizeof__",
            "__str__", "__subclasshook__", "__firstlineno__", "__annotations__",
            "__static_attributes__", "__dict__", "__weakref__", "__slots__", "__mro__",
            "__subclasses__", "__bases__", "__base__", "__flags__",
            "__abstractmethods__", "__code__", "__defaults__",
            "__kwdefaults__", "__closure__",
        ]

        # Filter for dunder attributes that are not excluded and not callable
        for attr, value in attributes.items():
            if (
                callable(value)
                or isinstance(value, (staticmethod, classmethod, property))
                or not attr.startswith("__")
            ):
                continue
            if attr in exclude:
                continue
            if attr.startswith("__") and attr.endswith("__"):
                dunder[attr] = value

        self["dunder_attributes"] = dunder
        return self["dunder_attributes"]

    def getMagicAttributes(self) -> dict:
        """
        Return a dictionary of magic (dunder) class attributes.

        Returns
        -------
        dict
            Dictionary mapping magic attribute names to their values. Only includes
            attributes that start with double underscores and are not callable,
            static methods, class methods, or properties.
        """
        # Delegate to getDunderAttributes for magic attributes
        return self.getDunderAttributes()

    def hasMethod(self, name: str) -> bool:
        """
        Determine if the abstract class contains a method with the given name.

        Parameters
        ----------
        name : str
            The name of the method to check.

        Returns
        -------
        bool
            True if the method exists in the class, otherwise False.
        """
        # Check if the method name is present in the list of all methods
        return name in self.getMethods()

    def removeMethod(self, name: str) -> bool:
        """
        Remove a method from the abstract class.

        Parameters
        ----------
        name : str
            Name of the method to remove.

        Returns
        -------
        bool
            True if the method was successfully removed.

        Raises
        ------
        ValueError
            If the method does not exist or cannot be removed.
        """
        # Check if the method exists before attempting removal
        if not self.hasMethod(name):
            error_msg = (
                f"Method '{name}' does not exist in class '{self.getClassName()}'."
            )
            raise ValueError(error_msg)

        # Handle name mangling for private methods
        if name.startswith("__") and not name.endswith("__"):
            class_name = self.getClassName()
            name = f"_{class_name}{name}"

        # Remove the method from the class
        delattr(self.__abstract, name)

        # Invalidate cached methods
        del self["methods"]

        # Indicate successful removal
        return True

    def getMethodSignature(self, name: str) -> inspect.Signature:
        """
        Retrieve the signature of a method in the abstract class.

        Parameters
        ----------
        name : str
            Name of the method to retrieve the signature for.

        Returns
        -------
        inspect.Signature
            Signature object of the specified method.

        Raises
        ------
        ValueError
            If the method does not exist or is not callable.
        """
        # Return cached signature if available
        if f"{name}_signature" in self:
            return self[f"{name}_signature"]

        if not self.hasMethod(name):
            error_msg = (
                f"Method '{name}' does not exist in class '{self.getClassName()}'."
            )
            raise ValueError(error_msg)

        # Extract the method from the class if instance is not initialized
        method = getattr(self.__abstract, name, None)

        if not callable(method):
            error_msg = (
                f"'{name}' is not callable in class '{self.getClassName()}'."
            )
            raise TypeError(error_msg)

        # Get and cache the signature of the method
        self[f"{name}_signature"] = inspect.signature(method)
        return self[f"{name}_signature"]

    def getMethods(self) -> list[str]:
        """
        Return all method names defined in the abstract class.

        Returns
        -------
        list of str
            List of all method names, including public, protected, private,
            static, and class methods.
        """
        # Use cache if available for performance
        if "methods" in self:
            return self["methods"]

        # Aggregate all method names from various visibility levels
        self["methods"] = [
            *self.getPublicMethods(),
            *self.getProtectedMethods(),
            *self.getPrivateMethods(),
            *self.getPublicClassMethods(),
            *self.getProtectedClassMethods(),
            *self.getPrivateClassMethods(),
            *self.getPublicStaticMethods(),
            *self.getProtectedStaticMethods(),
            *self.getPrivateStaticMethods(),
        ]
        return self["methods"]

    def getPublicMethods(self) -> list[str]:
        """
        Return all public instance method names.

        Returns
        -------
        list of str
            List of public instance method names. Excludes dunder, protected,
            private methods, static methods, class methods, and properties.
        """
        # Use cache for performance
        if "public_methods" in self:
            return self["public_methods"]

        # Collect public instance methods only
        class_name: str = self.getClassName()
        attributes: dict[str, Any] = self.__abstract.__dict__
        public_methods: list[str] = []

        # Collect public instance methods only
        for attr, value in attributes.items():
            if callable(value) and not isinstance(value, (staticmethod, classmethod)) \
               and not isinstance(value, property):
                if attr.startswith("__") and attr.endswith("__"):
                    continue
                if attr.startswith(f"_{class_name}"):
                    continue
                if attr.startswith("_"):
                    continue
                public_methods.append(attr)

        self["public_methods"] = public_methods
        return self["public_methods"]

    def getPublicSyncMethods(self) -> list[str]:
        """
        Return all public synchronous method names from the abstract class.

        Returns
        -------
        list of str
            List of public synchronous method names. Excludes asynchronous methods.
        """
        # Use cache for performance
        if "public_sync_methods" in self:
            return self["public_sync_methods"]

        methods: list[str] = self.getPublicMethods()
        sync_methods: list[str] = []
        for method in methods:
            # Only include methods that are not coroutine functions
            if not inspect.iscoroutinefunction(getattr(self.__abstract, method)):
                sync_methods.append(method)
        self["public_sync_methods"] = sync_methods
        return self["public_sync_methods"]

    def getPublicAsyncMethods(self) -> list[str]:
        """
        Return all public asynchronous method names.

        Returns
        -------
        list of str
            List of public asynchronous method names. Only coroutine functions
            are included.
        """
        # Use cache for performance
        if "public_async_methods" in self:
            return self["public_async_methods"]

        methods: list[str] = self.getPublicMethods()
        async_methods: list[str] = []
        for method in methods:
            # Only include coroutine functions
            if inspect.iscoroutinefunction(getattr(self.__abstract, method)):
                async_methods.append(method)
        self["public_async_methods"] = async_methods
        return self["public_async_methods"]

    def getProtectedMethods(self) -> list[str]:
        """
        Return all protected instance method names.

        Parameters
        ----------
        None

        Returns
        -------
        list of str
            List of protected instance method names. Includes only methods that
            start with a single underscore, are not dunder, private, static,
            class methods, or properties.
        """
        # Use cache for performance
        if "protected_methods" in self:
            return self["protected_methods"]

        attributes: dict[str, Any] = self.__abstract.__dict__
        protected_methods: list[str] = []

        # Collect protected instance methods only
        for attr, value in attributes.items():
            if (
                callable(value)
                and not isinstance(value, (staticmethod, classmethod))
                and not isinstance(value, property)
                and attr.startswith("_")
                and not attr.startswith("__")
                and not attr.startswith(f"_{self.getClassName()}")
            ):
                protected_methods.append(attr)

        self["protected_methods"] = protected_methods
        return self["protected_methods"]

    def getProtectedSyncMethods(self) -> list[str]:
        """
        Return all protected synchronous method names.

        Returns
        -------
        list of str
            List of protected synchronous method names. Only includes protected
            methods that are not coroutine functions.
        """
        # Use cache for performance
        if "protected_sync_methods" in self:
            return self["protected_sync_methods"]

        methods: list[str] = self.getProtectedMethods()
        sync_methods: list[str] = []
        for method in methods:
            # Only include methods that are not coroutine functions
            if not inspect.iscoroutinefunction(getattr(self.__abstract, method)):
                sync_methods.append(method)
        self["protected_sync_methods"] = sync_methods
        return self["protected_sync_methods"]

    def getProtectedAsyncMethods(self) -> list[str]:
        """
        Return all protected asynchronous method names.

        Parameters
        ----------
        None

        Returns
        -------
        list of str
            List of protected asynchronous method names. Only includes protected
            methods that are coroutine functions.
        """
        # Use cache for performance
        if "protected_async_methods" in self:
            return self["protected_async_methods"]

        methods: list[str] = self.getProtectedMethods()
        async_methods: list[str] = []
        for method in methods:
            # Only include coroutine functions
            if inspect.iscoroutinefunction(getattr(self.__abstract, method)):
                async_methods.append(method)
        self["protected_async_methods"] = async_methods
        return self["protected_async_methods"]

    def getPrivateMethods(self) -> list[str]:
        """
        Return all private instance method names.

        Private methods are those with name-mangling (start with _ClassName).
        Excludes static methods, class methods, properties, and dunder methods.

        Returns
        -------
        list of str
            List of private instance method names with class name prefixes removed.
        """
        # Use cache for performance
        if "private_methods" in self:
            return self["private_methods"]

        class_name: str = self.getClassName()
        attributes: dict[str, Any] = self.__abstract.__dict__
        private_methods: list[str] = []

        # Collect private instance methods only
        for attr, value in attributes.items():
            if (
                callable(value)
                and not isinstance(value, (staticmethod, classmethod))
                and not isinstance(value, property)
                and attr.startswith(f"_{class_name}")
            ):
                # Remove class name prefix for clarity
                private_methods.append(str(attr).replace(f"_{class_name}", ""))

        self["private_methods"] = private_methods
        return self["private_methods"]

    def getPrivateSyncMethods(self) -> list[str]:
        """
        Return all private synchronous method names.

        Returns
        -------
        list of str
            List of private synchronous method names. Only includes private methods
            that are not coroutine functions.
        """
        # Use cache for performance
        if "private_sync_methods" in self:
            return self["private_sync_methods"]

        methods: list[str] = self.getPrivateMethods()
        sync_methods: list[str] = []
        for method in methods:
            # Only include methods that are not coroutine functions
            if not inspect.iscoroutinefunction(
                getattr(self.__abstract, f"_{self.getClassName()}{method}"),
            ):
                sync_methods.append(method)
        self["private_sync_methods"] = sync_methods
        return self["private_sync_methods"]

    def getPrivateAsyncMethods(self) -> list[str]:
        """
        Retrieve private asynchronous method names.

        Parameters
        ----------
        self : ReflectionAbstract
            The reflection instance.

        Returns
        -------
        list of str
            List of private asynchronous method names. Only includes private
            methods that are coroutine functions.
        """
        # Use cache for performance
        if "private_async_methods" in self:
            return self["private_async_methods"]

        methods: list[str] = self.getPrivateMethods()
        async_methods: list[str] = []
        for method in methods:
            # Only include coroutine functions
            if inspect.iscoroutinefunction(
                getattr(self.__abstract, f"_{self.getClassName()}{method}"),
            ):
                async_methods.append(method)
        self["private_async_methods"] = async_methods
        return self["private_async_methods"]

    def getPublicClassMethods(self) -> list[str]:
        """
        Return all public class method names.

        Returns
        -------
        list of str
            List of public class method names. Only includes methods decorated
            with @classmethod that do not start with underscores.
        """
        # Use cache for performance
        if "public_class_methods" in self:
            return self["public_class_methods"]

        class_name: str = self.getClassName()
        attributes: dict[str, Any] = self.__abstract.__dict__
        public_class_methods: list[str] = []

        # Collect public class methods only
        for attr, value in attributes.items():
            if isinstance(value, classmethod):
                if attr.startswith("__") and attr.endswith("__"):
                    continue
                if attr.startswith(f"_{class_name}"):
                    continue
                if attr.startswith("_"):
                    continue
                public_class_methods.append(attr)

        self["public_class_methods"] = public_class_methods
        return self["public_class_methods"]

    def getPublicClassSyncMethods(self) -> list[str]:
        """
        Return all public synchronous class method names.

        Returns
        -------
        list of str
            List of public synchronous class method names. Only includes methods
            that are not coroutine functions.
        """
        # Use cache for performance
        if "public_class_sync_methods" in self:
            return self["public_class_sync_methods"]

        methods: list[str] = self.getPublicClassMethods()
        sync_methods: list[str] = []
        for method in methods:
            # Only include methods that are not coroutine functions
            if not inspect.iscoroutinefunction(getattr(self.__abstract, method)):
                sync_methods.append(method)
        self["public_class_sync_methods"] = sync_methods
        return self["public_class_sync_methods"]

    def getPublicClassAsyncMethods(self) -> list[str]:
        """
        Return all public asynchronous class method names.

        Returns
        -------
        list of str
            List of public asynchronous class method names. Only includes methods
            decorated with @classmethod that are coroutine functions and do not
            start with underscores.
        """
        # Use cache for performance
        if "public_class_async_methods" in self:
            return self["public_class_async_methods"]

        methods: list[str] = self.getPublicClassMethods()
        async_methods: list[str] = []
        for method in methods:
            # Only include coroutine functions
            if inspect.iscoroutinefunction(getattr(self.__abstract, method)):
                async_methods.append(method)
        self["public_class_async_methods"] = async_methods
        return self["public_class_async_methods"]

    def getProtectedClassMethods(self) -> list[str]:
        """
        Return a list of protected class methods.

        Parameters
        ----------
        self : ReflectionAbstract
            The reflection instance.

        Returns
        -------
        list of str
            Names of protected class methods (not instance methods).
        """
        # Use cache for performance
        if "protected_class_methods" in self:
            return self["protected_class_methods"]

        class_name: str = self.getClassName()
        attributes: dict[str, Any] = self.__abstract.__dict__
        protected_class_methods: list[str] = []

        # Collect protected class methods only
        for attr, value in attributes.items():
            if (
                isinstance(value, classmethod)
                and attr.startswith("_")
                and not attr.startswith("__")
                and not attr.startswith(f"_{class_name}")
            ):
                protected_class_methods.append(attr)

        self["protected_class_methods"] = protected_class_methods
        return self["protected_class_methods"]

    def getProtectedClassSyncMethods(self) -> list[str]:
        """
        Return all protected synchronous class method names.

        Parameters
        ----------
        self : ReflectionAbstract

        Returns
        -------
        list of str
            List of protected synchronous class method names. Only includes
            protected class methods that are not coroutine functions.
        """
        # Use cache for performance
        if "protected_class_sync_methods" in self:
            return self["protected_class_sync_methods"]

        methods: list[str] = self.getProtectedClassMethods()
        sync_methods: list[str] = []
        for method in methods:
            # Only include methods that are not coroutine functions
            if not inspect.iscoroutinefunction(getattr(self.__abstract, method)):
                sync_methods.append(method)
        self["protected_class_sync_methods"] = sync_methods
        return self["protected_class_sync_methods"]

    def getProtectedClassAsyncMethods(self) -> list[str]:
        """
        Return all protected asynchronous class method names.

        Parameters
        ----------
        self : ReflectionAbstract

        Returns
        -------
        list of str
            List of protected asynchronous class method names. Only includes
            protected class methods that are coroutine functions.
        """
        # Use cache for performance
        if "protected_class_async_methods" in self:
            return self["protected_class_async_methods"]

        methods: list[str] = self.getProtectedClassMethods()
        async_methods: list[str] = []
        for method in methods:
            # Only include coroutine functions
            if inspect.iscoroutinefunction(getattr(self.__abstract, method)):
                async_methods.append(method)
        self["protected_class_async_methods"] = async_methods
        return self["protected_class_async_methods"]

    def getPrivateClassMethods(self) -> list[str]:
        """
        Return a list of private class methods.

        Parameters
        ----------
        self : ReflectionAbstract

        Returns
        -------
        list of str
            List of private class method names with class name prefixes removed.
        """
        # Use cache for performance
        if "private_class_methods" in self:
            return self["private_class_methods"]

        class_name: str = self.getClassName()
        attributes: dict[str, Any] = self.__abstract.__dict__
        private_class_methods: list[str] = []

        # Collect private class methods only (name-mangled)
        for attr, value in attributes.items():
            if (
                isinstance(value, classmethod)
                and attr.startswith(f"_{class_name}")
            ):
                private_class_methods.append(
                    str(attr).replace(f"_{class_name}", ""),
                )

        self["private_class_methods"] = private_class_methods
        return self["private_class_methods"]

    def getPrivateClassSyncMethods(self) -> list[str]:
        """
        Return all private synchronous class method names.

        Parameters
        ----------
        self : ReflectionAbstract

        Returns
        -------
        list of str
            List of private synchronous class method names. Only includes private
            class methods that are not coroutine functions.
        """
        # Use cache for performance
        if "private_class_sync_methods" in self:
            return self["private_class_sync_methods"]

        methods: list[str] = self.getPrivateClassMethods()
        sync_methods: list[str] = []
        for method in methods:
            # Only include methods that are not coroutine functions
            if not inspect.iscoroutinefunction(
                getattr(self.__abstract, f"_{self.getClassName()}{method}"),
            ):
                sync_methods.append(method)
        self["private_class_sync_methods"] = sync_methods
        return self["private_class_sync_methods"]

    def getPrivateClassAsyncMethods(self) -> list[str]:
        """
        Return all private asynchronous class method names.

        Finds private class methods (name-mangled) that are coroutine functions.

        Returns
        -------
        list of str
            List of private asynchronous class method names with class name
            prefixes removed.
        """
        # Use cache for performance
        if "private_class_async_methods" in self:
            return self["private_class_async_methods"]

        methods: list[str] = self.getPrivateClassMethods()
        async_methods: list[str] = []
        for method in methods:
            # Only include coroutine functions
            if inspect.iscoroutinefunction(
                getattr(self.__abstract, f"_{self.getClassName()}{method}"),
            ):
                async_methods.append(method)
        self["private_class_async_methods"] = async_methods
        return self["private_class_async_methods"]

    def getPublicStaticMethods(self) -> list[str]:
        """
        Return all public static method names.

        Returns
        -------
        list of str
            List of public static method names. Only includes methods decorated
            with @staticmethod that do not start with underscores.
        """
        # Use cache for performance
        if "public_static_methods" in self:
            return self["public_static_methods"]

        class_name: str = self.getClassName()
        attributes: dict[str, Any] = self.__abstract.__dict__
        public_static_methods: list[str] = []

        # Collect public static methods only
        for attr, value in attributes.items():
            if isinstance(value, staticmethod):
                if attr.startswith("__") and attr.endswith("__"):
                    continue
                if attr.startswith(f"_{class_name}"):
                    continue
                if attr.startswith("_"):
                    continue
                public_static_methods.append(attr)

        self["public_static_methods"] = public_static_methods
        return self["public_static_methods"]

    def getPublicStaticSyncMethods(self) -> list[str]:
        """
        Return all public synchronous static method names.

        Parameters
        ----------
        self : ReflectionAbstract

        Returns
        -------
        list of str
            List of public static method names that are synchronous (not coroutine
            functions).
        """
        # Use cache for performance
        if "public_static_sync_methods" in self:
            return self["public_static_sync_methods"]

        methods: list[str] = self.getPublicStaticMethods()
        sync_methods: list[str] = []
        for method in methods:
            # Only include methods that are not coroutine functions
            if not inspect.iscoroutinefunction(getattr(self.__abstract, method)):
                sync_methods.append(method)
        self["public_static_sync_methods"] = sync_methods
        return self["public_static_sync_methods"]

    def getPublicStaticAsyncMethods(self) -> list[str]:
        """
        Return all public asynchronous static method names.

        Parameters
        ----------
        self : ReflectionAbstract

        Returns
        -------
        list of str
            List of public static method names that are coroutine functions.
        """
        # Use cache for performance
        if "public_static_async_methods" in self:
            return self["public_static_async_methods"]

        methods: list[str] = self.getPublicStaticMethods()
        async_methods: list[str] = []
        for method in methods:
            # Only include coroutine functions
            if inspect.iscoroutinefunction(getattr(self.__abstract, method)):
                async_methods.append(method)
        self["public_static_async_methods"] = async_methods
        return self["public_static_async_methods"]

    def getProtectedStaticMethods(self) -> list[str]:
        """
        Return a list of protected static method names.

        Parameters
        ----------
        self : ReflectionAbstract

        Returns
        -------
        list of str
            List of protected static method names. Only includes methods decorated
            with @staticmethod that start with a single underscore, are not dunder,
            and are not name-mangled private methods.
        """
        # Use cache for performance
        if "protected_static_methods" in self:
            return self["protected_static_methods"]

        class_name: str = self.getClassName()
        attributes: dict[str, Any] = self.__abstract.__dict__
        protected_static_methods: list[str] = []

        # Collect protected static methods only
        for attr, value in attributes.items():
            if (
                isinstance(value, staticmethod)
                and attr.startswith("_")
                and not attr.startswith("__")
                and not attr.startswith(f"_{class_name}")
            ):
                protected_static_methods.append(attr)

        self["protected_static_methods"] = protected_static_methods
        return self["protected_static_methods"]

    def getProtectedStaticSyncMethods(self) -> list[str]:
        """
        Return all protected synchronous static method names.

        Parameters
        ----------
        self : ReflectionAbstract

        Returns
        -------
        list of str
            List of protected static method names that are synchronous (not
            coroutine functions).
        """
        # Use cache for performance
        if "protected_static_sync_methods" in self:
            return self["protected_static_sync_methods"]

        methods: list[str] = self.getProtectedStaticMethods()
        sync_methods: list[str] = []
        for method in methods:
            # Only include methods that are not coroutine functions
            if not inspect.iscoroutinefunction(getattr(self.__abstract, method)):
                sync_methods.append(method)
        self["protected_static_sync_methods"] = sync_methods
        return self["protected_static_sync_methods"]

    def getProtectedStaticAsyncMethods(self) -> list[str]:
        """
        Return all protected asynchronous static method names.

        Parameters
        ----------
        self : ReflectionAbstract

        Returns
        -------
        list of str
            List of protected static method names that are coroutine functions.
        """
        # Use cache for performance
        if "protected_static_async_methods" in self:
            return self["protected_static_async_methods"]

        methods: list[str] = self.getProtectedStaticMethods()
        async_methods: list[str] = []
        for method in methods:
            # Only include methods that are coroutine functions
            if inspect.iscoroutinefunction(getattr(self.__abstract, method)):
                async_methods.append(method)
        self["protected_static_async_methods"] = async_methods
        return self["protected_static_async_methods"]

    def getPrivateStaticMethods(self) -> list[str]:
        """
        Return a list of private static method names.

        Parameters
        ----------
        self : ReflectionAbstract

        Returns
        -------
        list of str
            List of private static method names with class name prefixes removed.
        """
        # Use cache for performance
        if "private_static_methods" in self:
            return self["private_static_methods"]

        class_name: str = self.getClassName()
        attributes: dict[str, Any] = self.__abstract.__dict__
        private_static_methods: list[str] = []

        # Collect private static methods only (name-mangled)
        for attr, value in attributes.items():
            if isinstance(value, staticmethod) and attr.startswith(f"_{class_name}"):
                private_static_methods.append(
                    str(attr).replace(f"_{class_name}", ""),
                )

        self["private_static_methods"] = private_static_methods
        return self["private_static_methods"]

    def getPrivateStaticSyncMethods(self) -> list[str]:
        """
        Return all private synchronous static method names.

        Parameters
        ----------
        self : ReflectionAbstract

        Returns
        -------
        list of str
            List of private static method names that are synchronous (not coroutine
            functions).
        """
        # Use cache for performance
        if "private_static_sync_methods" in self:
            return self["private_static_sync_methods"]

        methods: list[str] = self.getPrivateStaticMethods()
        sync_methods: list[str] = []
        for method in methods:
            # Only include methods that are not coroutine functions
            if not inspect.iscoroutinefunction(
                getattr(self.__abstract, f"_{self.getClassName()}{method}"),
            ):
                sync_methods.append(method)
        self["private_static_sync_methods"] = sync_methods
        return self["private_static_sync_methods"]

    def getPrivateStaticAsyncMethods(self) -> list[str]:
        """
        Return all private asynchronous static method names.

        Parameters
        ----------
        self : ReflectionAbstract

        Returns
        -------
        list of str
            List of private static method names that are coroutine functions.
        """
        # Use cache for performance
        if "private_static_async_methods" in self:
            return self["private_static_async_methods"]

        methods: list[str] = self.getPrivateStaticMethods()
        async_methods: list[str] = []
        for method in methods:
            # Only include coroutine functions
            if inspect.iscoroutinefunction(
                getattr(self.__abstract, f"_{self.getClassName()}{method}"),
            ):
                async_methods.append(method)
        self["private_static_async_methods"] = async_methods
        return self["private_static_async_methods"]

    def getDunderMethods(self) -> list[str]:
        """
        Return all dunder (double underscore) method names in the abstract class.

        Returns
        -------
        list of str
            List of dunder method names. Only includes methods that start and end
            with double underscores, are callable, and are not static, class
            methods, or properties.
        """
        # Use cache for performance
        if "dunder_methods" in self:
            return self["dunder_methods"]

        attributes: dict[str, Any] = self.__abstract.__dict__
        dunder_methods: list[str] = []
        exclude: list[str] = []

        # Collect dunder methods only
        for attr, value in attributes.items():
            if (
                callable(value)
                and not isinstance(value, (staticmethod, classmethod, property))
                and attr.startswith("__")
                and attr.endswith("__")
                and attr not in exclude
            ):
                dunder_methods.append(attr)

        self["dunder_methods"] = dunder_methods
        return self["dunder_methods"]

    def getMagicMethods(self) -> list[str]:
        """
        Return all magic (dunder) methods from the abstract class.

        Returns
        -------
        list of str
            List of magic method names. This is an alias for getDunderMethods().
        """
        return self.getDunderMethods()

    def getProperties(self) -> list[str]:
        """
        Retrieve all property names from the abstract class.

        Returns
        -------
        List[str]
            List of property names with name mangling prefixes removed for clarity.
        """
        # Return cached properties if available
        if "properties" in self:
            return self["properties"]

        properties: list[str] = []
        class_name: str = self.getClassName()
        for name, prop in self.__abstract.__dict__.items():
            if isinstance(prop, property):
                # Remove class name prefix for private properties
                name_prop: str = name.replace(f"_{class_name}", "")
                properties.append(name_prop)
        self["properties"] = properties
        return self["properties"]

    def getPublicProperties(self) -> list[str]:
        """
        Return all public property names from the abstract class.

        Parameters
        ----------
        self : ReflectionAbstract

        Returns
        -------
        list of str
            List of public property names with name mangling prefixes removed.
            Only properties that do not start with underscores are included.
        """
        # Use cache for performance
        if "public_properties" in self:
            return self["public_properties"]

        properties: list[str] = []
        cls_name: str = self.getClassName()
        for name, prop in self.__abstract.__dict__.items():
            if (
                isinstance(prop, property)
                and not name.startswith("_")
                and not name.startswith(f"_{cls_name}")
            ):
                properties.append(name.replace(f"_{cls_name}", ""))
        self["public_properties"] = properties
        return self["public_properties"]

    def getProtectedProperties(self) -> list[str]:
        """
        Retrieve all protected properties from the abstract class.

        Parameters
        ----------
        self : ReflectionAbstract

        Returns
        -------
        list of str
            List of protected property names. Only includes properties that start
            with a single underscore, are not dunder, and are not name-mangled
            private properties.
        """
        # Return cached protected properties if available
        if "protected_properties" in self:
            return self["protected_properties"]

        properties: list[str] = []
        class_name: str = self.getClassName()
        for name, prop in self.__abstract.__dict__.items():
            # Only include protected properties (single underscore, not dunder/private)
            if (
                isinstance(prop, property)
                and name.startswith("_")
                and not name.startswith("__")
                and not name.startswith(f"_{class_name}")
            ):
                properties.append(name)
        self["protected_properties"] = properties
        return self["protected_properties"]

    def getPrivateProperties(self) -> list[str]:
        """
        Retrieve all private properties from the abstract class.

        Parameters
        ----------
        self : ReflectionAbstract

        Returns
        -------
        list of str
            List of private property names with class name prefixes removed.
            Only includes name-mangled properties that start with _ClassName.
        """
        # Use cache for performance
        if "private_properties" in self:
            return self["private_properties"]

        properties: list[str] = []
        class_name: str = self.getClassName()
        for name, prop in self.__abstract.__dict__.items():
            if (
                isinstance(prop, property)
                and name.startswith(f"_{class_name}")
                and not name.startswith("__")
            ):
                # Remove class name prefix for clarity
                properties.append(name.replace(f"_{class_name}", ""))
        self["private_properties"] = properties
        return self["private_properties"]

    def getPropertySignature(self, name: str) -> inspect.Signature:
        """
        Retrieve the signature of a property's getter method.

        Parameters
        ----------
        name : str
            Name of the property to inspect.

        Returns
        -------
        inspect.Signature
            Signature object of the property's getter method.

        Raises
        ------
        ValueError
            If the property does not exist or is not accessible.
        """
        # Use cache for performance
        if f"{name}_property_signature" in self:
            return self[f"{name}_property_signature"]

        # Handle private property name mangling
        if name.startswith("__") and not name.endswith("__"):
            class_name: str = self.getClassName()
            name = f"_{class_name}{name}"

        # Check if the property exists on the class
        if not hasattr(self.__abstract, name):
            error_msg = (
                f"Property '{name}' does not exist in class '{self.getClassName()}'."
            )
            raise ValueError(error_msg)

        prop = getattr(self.__abstract, name)
        if not isinstance(prop, property):
            error_msg = (
                f"'{name}' is not a property in class '{self.getClassName()}'."
            )
            raise TypeError(error_msg)

        # Cache and return the signature of the property's getter
        self[f"{name}_property_signature"] = inspect.signature(prop.fget)
        return self[f"{name}_property_signature"]

    def getPropertyDocstring(self, name: str) -> str | None:
        """
        Retrieve the docstring of a property's getter method.

        Parameters
        ----------
        name : str
            The name of the property.

        Returns
        -------
        str or None
            The docstring of the property's getter method, or None if unavailable.

        Raises
        ------
        ValueError
            If the property does not exist or is not accessible.
        """
        # Return cached docstring if available
        if f"{name}_property_docstring" in self:
            return self[f"{name}_property_docstring"]

        # Handle name mangling for private properties
        if name.startswith("__") and not name.endswith("__"):
            class_name: str = self.getClassName()
            name = f"_{class_name}{name}"

        # Check if the property exists
        if not hasattr(self.__abstract, name):
            error_msg = (
                f"Property '{name}' does not exist in class '{self.getClassName()}'."
            )
            raise ValueError(error_msg)

        prop = getattr(self.__abstract, name)
        if not isinstance(prop, property):
            error_msg = (
                f"'{name}' is not a property in class '{self.getClassName()}'."
            )
            raise TypeError(error_msg)

        # Cache and return the docstring of the property's getter
        self[f"{name}_property_docstring"] = prop.fget.__doc__ if prop.fget else None
        return self[f"{name}_property_docstring"]

    def constructorSignature(self) -> SignatureArguments:
        """
        Retrieve constructor dependencies for the reflected class.

        Returns
        -------
        SignatureArguments
            Structured representation of constructor dependencies, including
            resolved (names and values) and unresolved (parameter names without
            default values or annotations).
        """
        # Return cached constructor signature if available
        if "dependencies_constructor" in self:
            return self["dependencies_constructor"]

        # Use ReflectDependencies to inspect constructor dependencies
        self["dependencies_constructor"] = ReflectDependencies(
            self.__abstract,
        ).constructorSignature()
        return self["dependencies_constructor"]

    def methodSignature(self, method_name: str) -> SignatureArguments:
        """
        Retrieve resolved and unresolved dependencies for a method.

        Parameters
        ----------
        method_name : str
            Name of the method to inspect.

        Returns
        -------
        SignatureArguments
            Structured representation of method dependencies, including resolved
            and unresolved dependencies.

        Raises
        ------
        AttributeError
            If the method does not exist on the abstract class.
        """
        # Return cached dependencies if available
        if f"{method_name}_dependencies_signature" in self:
            return self[f"{method_name}_dependencies_signature"]

        # Check if the method exists
        if not self.hasMethod(method_name):
            error_msg = (
                f"Method '{method_name}' does not exist on '{self.getClassName()}'."
            )
            raise AttributeError(error_msg)

        # Handle name mangling for private methods
        if method_name.startswith("__") and not method_name.endswith("__"):
            class_name = self.getClassName()
            method_name = f"_{class_name}{method_name}"

        # Use ReflectDependencies to get method dependencies
        self[f"{method_name}_dependencies_signature"] = ReflectDependencies(
            self.__abstract,
        ).methodSignature(method_name)
        return self[f"{method_name}_dependencies_signature"]

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
