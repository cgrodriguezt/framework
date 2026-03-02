import inspect
import keyword
from typing import Any
from collections.abc import Callable
from orionis.services.introspection.concretes.contracts.reflection import (
    IReflectionConcrete,
)
from orionis.services.introspection.dependencies.entities.signature import (
    Signature,
)
from orionis.services.introspection.dependencies.reflection import ReflectDependencies

class ReflectionConcrete(IReflectionConcrete):

    # ruff: noqa: ANN401, PERF401, PLC0415

    def __init__(self, concrete: type) -> None:
        """
        Initialize the reflection concrete with a validated class type.

        Parameters
        ----------
        concrete : Type
            The class type to reflect.

        Raises
        ------
        TypeError
            If the argument is not a class type.
        ValueError
            If the class is built-in, primitive, abstract, or an interface.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Validate that the provided type is a concrete class
        from orionis.services.introspection.reflection import Reflection
        if not Reflection.isConcreteClass(concrete):
            error_msg = (
                f"Argument 'concrete' must be a class type, got "
                f"'{type(concrete).__name__}' instead."
            )
            raise TypeError(error_msg)

        # Store the concrete class and initialize instance reference
        self._concrete = concrete
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
        Return the class type being reflected.

        Returns
        -------
        Type
            The class type provided during initialization.
        """
        return self._concrete

    def getClassName(self) -> str:
        """
        Return the name of the reflected class.

        Returns
        -------
        str
            The simple name of the class without module qualification.
        """
        return self._concrete.__name__

    def getModuleName(self) -> str:
        """
        Return the module name where the reflected class is defined.

        Returns
        -------
        str
            The fully qualified module name containing the class.
        """
        return self._concrete.__module__

    def getModuleWithClassName(self) -> str:
        """
        Return the fully qualified class name with module path.

        Returns
        -------
        str
            The module name concatenated with the class name, separated by a dot.
        """
        # Combine module and class name for fully qualified identifier
        return f"{self.getModuleName()}.{self.getClassName()}"

    def getDocstring(self) -> str | None:
        """
        Return the docstring of the reflected class.

        Returns
        -------
        str or None
            The docstring of the class if defined, otherwise None.
        """
        # Return the class docstring if available
        return self._concrete.__doc__ or None

    def getBaseClasses(self) -> list[type]:
        """
        Return all base classes of the reflected class.

        Returns
        -------
        list of type
            A list containing all base classes in the method resolution order.
        """
        # Return the tuple of base classes for the class
        return list(self._concrete.__bases__)

    def getSourceCode(self, method: str | None = None) -> str | None:
        """
        Retrieve the source code for the class or a specific method.

        Parameters
        ----------
        method : str or None, optional
            Name of the method to retrieve source code for. If None, returns
            the source code of the entire class.

        Returns
        -------
        str or None
            Source code as a string if available, otherwise None.
        """
        try:
            # Return cached class source code if available
            if not method:
                if "source_code" in self:
                    return self["source_code"]
                self["source_code"] = inspect.getsource(self._concrete)
                return self["source_code"]

            # Return cached method source code if available
            if f"source_code_{method}" in self:
                return self[f"source_code_{method}"]

            # Handle name mangling for private methods
            if method.startswith("__") and not method.endswith("__"):
                class_name = self.getClassName()
                method = f"_{class_name}{method}"

            # Check if the method exists
            if not self.hasMethod(method):
                return None

            # Retrieve and cache the method's source code
            self[f"source_code_{method}"] = inspect.getsource(
                getattr(self._concrete, method),
            )
            return self[f"source_code_{method}"]

        except (TypeError, OSError):
            # Return None if source code cannot be retrieved
            return None

    def getFile(self) -> str:
        """
        Return the absolute file path of the reflected class.

        Returns
        -------
        str
            The absolute file path containing the class definition.

        Raises
        ------
        ValueError
            If the file path cannot be determined.
        """
        # Return cached file path if available
        if "file_path" in self:
            return self["file_path"]

        try:
            # Retrieve and cache the file path of the class
            self["file_path"] = inspect.getfile(self._concrete)
            return self["file_path"]
        except TypeError as e:
            error_msg = (
                f"Could not retrieve file for '{self._concrete.__name__}': {e}"
            )
            raise ValueError(error_msg) from e

    def getAnnotations(self) -> dict:
        """
        Retrieve type annotations defined on the reflected class.

        Resolves name mangling for private attributes and returns a dictionary
        mapping attribute names to their type annotations.

        Returns
        -------
        dict
            Dictionary of attribute names and their type annotations.
        """
        # Return cached annotations if available
        if "annotations" in self:
            return self["annotations"]

        annotations = {}
        # Process type annotations, resolving name mangling for private attributes
        for k, v in getattr(self._concrete, "__annotations__", {}).items():
            unmangled = str(k).replace(f"_{self.getClassName()}", "")
            annotations[unmangled] = v
        self["annotations"] = annotations
        return annotations

    def hasAttribute(self, attribute: str) -> bool:
        """
        Determine if the reflected class has a specific attribute.

        Parameters
        ----------
        attribute : str
            Name of the attribute to check.

        Returns
        -------
        bool
            True if the attribute exists in the class, otherwise False.
        """
        # Check for attribute existence in the class attributes dictionary
        return attribute in self.getAttributes()

    def getAttribute(self, name: str, default: Any = None) -> Any:
        """
        Retrieve the value of a class attribute.

        Parameters
        ----------
        name : str
            Name of the attribute to retrieve.
        default : Any, optional
            Value to return if the attribute is not found. Defaults to None.

        Returns
        -------
        Any
            Value of the attribute if found, otherwise the default value.
        """
        # Get all attributes from the class (public, protected, private, dunder)
        attrs = self.getAttributes()
        # Try to get the attribute from the attributes dictionary; if not found,
        # use getattr on the class
        return attrs.get(name, getattr(self._concrete, name, default))

    def setAttribute(self, name: str, value: object) -> bool:
        """
        Set a class attribute to the specified value.

        Parameters
        ----------
        name : str
            Name of the attribute to set.
        value : object
            Value to assign to the attribute.

        Returns
        -------
        bool
            True if the attribute was set successfully.

        Raises
        ------
        ValueError
            If the attribute name is invalid or the value is callable.
        """
        # Validate attribute name: must be a valid identifier and not a keyword
        if (
            not isinstance(name, str)
            or not name.isidentifier()
            or keyword.iskeyword(name)
        ):
            error_msg = (
                f"Invalid attribute name '{name}'. Must be a valid Python identifier "
                "and not a keyword."
            )
            raise ValueError(error_msg)

        # Prevent setting callables as attributes; suggest setMethod instead
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
        setattr(self._concrete, name, value)

        # Clear memory cache to ensure consistency
        self.__memory_cache.clear()

        return True

    def removeAttribute(self, name: str) -> bool:
        """
        Remove an attribute from the reflected class.

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
        # Check if the attribute exists in the class
        if not self.hasAttribute(name):
            error_msg = (
                f"Attribute '{name}' does not exist in class '{self.getClassName()}'."
            )
            raise ValueError(error_msg)

        # Handle name mangling for private attributes
        if name.startswith("__") and not name.endswith("__"):
            class_name = self.getClassName()
            name = f"_{class_name}{name}"

        # Remove the attribute from the class
        delattr(self._concrete, name)

        # Clear the memory cache to maintain consistency
        self.__memory_cache.clear()

        return True

    def getAttributes(self) -> dict:
        """
        Aggregate all class attributes of all visibility levels.

        Returns
        -------
        dict
            Dictionary mapping attribute names (str) to their values. Includes
            public, protected, private (with name mangling removed), and dunder
            attributes. Excludes methods and properties. The result is cached.
        """
        # Return cached attributes if available
        if "attributes" in self:
            return self["attributes"]

        # Merge attribute dictionaries from all visibility levels
        self["attributes"] = {
            **self.getPublicAttributes(),
            **self.getProtectedAttributes(),
            **self.getPrivateAttributes(),
            **self.getDunderAttributes(),
        }
        return self["attributes"]

    def getPublicAttributes(self) -> dict:
        """
        Retrieve all public class attributes.

        Public attributes are those that do not start with an underscore and are
        not callables, static methods, class methods, or properties.

        Returns
        -------
        dict
            Dictionary mapping public attribute names to their values. Excludes
            dunder, protected, and private attributes.
        """
        # Return cached public attributes if available
        if "public_attributes" in self:
            return self["public_attributes"]

        class_name = self.getClassName()
        attributes = self._concrete.__dict__
        public = {}

        # Collect only public attributes, excluding methods and special members
        for attr, value in attributes.items():
            if (
                callable(value)
                or isinstance(value, (staticmethod, classmethod, property))
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
        return public

    def getProtectedAttributes(self) -> dict:
        """
        Retrieve all protected class attributes.

        Protected attributes are those that start with a single underscore,
        excluding dunder, public, and private attributes.

        Returns
        -------
        dict
            Dictionary mapping protected attribute names to their values.
        """
        # Return cached protected attributes if available
        if "protected_attributes" in self:
            return self["protected_attributes"]

        class_name = self.getClassName()
        attributes = self._concrete.__dict__
        protected = {}

        # Collect only protected attributes, excluding methods and special members
        for attr, value in attributes.items():
            if (
                callable(value)
                or isinstance(value, (staticmethod, classmethod, property))
            ):
                continue
            if attr.startswith("__") and attr.endswith("__"):
                continue
            if attr.startswith(f"_{class_name}"):
                continue
            if not attr.startswith("_"):
                continue
            protected[attr] = value

        self["protected_attributes"] = protected
        return protected

    def getPrivateAttributes(self) -> dict:
        """
        Retrieve all private class attributes.

        Private attributes use Python's name mangling convention (double
        underscore prefix). Excludes methods, static methods, class methods,
        and properties.

        Returns
        -------
        dict
            Dictionary mapping private attribute names (with mangling removed)
            to their values.
        """
        # Return cached private attributes if available
        if "private_attributes" in self:
            return self["private_attributes"]

        class_name = self.getClassName()
        attributes = self._concrete.__dict__
        private = {}

        # Collect only private attributes, excluding methods and special members
        for attr, value in attributes.items():
            if (
                callable(value)
                or isinstance(value, (staticmethod, classmethod, property))
            ):
                continue
            if attr.startswith(f"_{class_name}"):
                # Remove name mangling for cleaner output
                private[str(attr).replace(f"_{class_name}", "")] = value

        self["private_attributes"] = private
        return private

    def getDunderAttributes(self) -> dict:
        """
        Retrieve all dunder (magic) class attributes.

        Dunder attributes are those with names that start and end with double
        underscores, excluding standard Python dunder attributes.

        Returns
        -------
        dict
            Dictionary mapping dunder attribute names to their values, excluding
            standard Python dunder attributes.
        """
        # Return cached dunder attributes if available
        if "dunder_attributes" in self:
            return self["dunder_attributes"]

        attributes = self._concrete.__dict__
        dunder = {}
        exclude = [
            "__class__", "__delattr__", "__dir__", "__doc__", "__eq__", "__format__",
            "__ge__", "__getattribute__", "__gt__", "__hash__", "__init__",
            "__init_subclass__", "__le__", "__lt__", "__module__", "__ne__", "__new__",
            "__reduce__", "__reduce_ex__", "__repr__", "__setattr__", "__sizeof__",
            "__str__", "__subclasshook__", "__firstlineno__", "__annotations__",
            "__static_attributes__", "__dict__", "__weakref__", "__slots__", "__mro__",
            "__subclasses__", "__bases__", "__base__", "__flags__",
            "__abstractmethods__", "__code__", "__defaults__", "__kwdefaults__",
            "__closure__",
        ]

        # Collect dunder attributes, excluding methods, properties, and standard dunders
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
        return dunder

    def getMagicAttributes(self) -> dict:
        """
        Return all magic (dunder) class attributes.

        This method is an alias for `getDunderAttributes()` and provides access
        to double underscore attributes.

        Returns
        -------
        dict
            Dictionary mapping magic attribute names to their values.
        """
        return self.getDunderAttributes()

    def hasMethod(self, name: str) -> bool:
        """
        Determine if the class defines a method with the given name.

        Parameters
        ----------
        name : str
            Name of the method to check.

        Returns
        -------
        bool
            True if the method exists in the class, otherwise False.
        """
        return name in self.getMethods()

    def setMethod(self, name: str, method: Callable) -> bool:
        """
        Add a method to the reflected class.

        Validates the method name and callable before adding it to the class.
        Handles private method name mangling automatically.

        Parameters
        ----------
        name : str
            Name for the new method.
        method : Callable
            Callable object to set as a method.

        Returns
        -------
        bool
            True if the method was successfully added.

        Raises
        ------
        ValueError
            If the method name already exists, is invalid, or the object is not
            callable.
        """
        # Check if the method already exists
        if name in self.getMethods():
            error_msg = (
                f"Method '{name}' already exists in class '{self.getClassName()}'. "
                "Use a different name or remove the existing method first."
            )
            raise ValueError(error_msg)

        # Ensure the name is a valid method name
        if (
            not isinstance(name, str) or
            not name.isidentifier() or
            keyword.iskeyword(name)
        ):
            error_msg = (
                f"Invalid method name '{name}'. Must be a valid Python identifier "
                "and not a keyword."
            )
            raise ValueError(error_msg)

        # Ensure the method is callable
        if not callable(method):
            error_msg = (
                f"Cannot set method '{name}' to a non-callable value."
            )
            raise TypeError(error_msg)

        # Handle private method name mangling
        if name.startswith("__") and not name.endswith("__"):
            class_name = self.getClassName()
            name = f"_{class_name}{name}"

        # Set the method on the class itself
        setattr(self._concrete, name, method)

        # Clear cache to ensure consistency
        self.__memory_cache.clear()

        return True

    def removeMethod(self, name: str) -> bool:
        """
        Remove a method from the reflected class.

        Handles private method name mangling before removal.

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
        delattr(self._concrete, name)

        # Clear cache to maintain consistency
        self.__memory_cache.clear()

        return True

    def getMethodSignature(self, name: str) -> inspect.Signature:
        """
        Retrieve the signature of a specific method.

        Parameters
        ----------
        name : str
            Name of the method to inspect.

        Returns
        -------
        inspect.Signature
            Signature object containing parameter and return information.

        Raises
        ------
        ValueError
            If the method does not exist or is not callable.
        """
        # Return cached signature if available
        if f"method_signature_{name}" in self:
            return self[f"method_signature_{name}"]

        # Check if the method exists in the class
        if not self.hasMethod(name):
            error_msg = (
                f"Method '{name}' does not exist in class '{self.getClassName()}'."
            )
            raise ValueError(error_msg)

        # Retrieve the method from the class
        method = getattr(self._concrete, name, None)

        # Ensure the retrieved attribute is callable
        if not callable(method):
            error_msg = (
                f"'{name}' is not callable in class '{self.getClassName()}'."
            )
            raise TypeError(error_msg)

        # Cache and return the method's signature
        self[f"method_signature_{name}"] = inspect.signature(method)
        return self[f"method_signature_{name}"]

    def getMethods(self) -> list[str]:
        """
        Retrieve all method names defined in the reflected class.

        Aggregates method names from all visibility levels (public, protected,
        private) and method types (instance, class, static). The result is
        cached after the first call for efficiency.

        Returns
        -------
        list of str
            List of all method names (instance, class, and static) defined in
            the class, including public, protected, and private methods.
        """
        # Return cached methods if available
        if "methods" in self:
            return self["methods"]

        # Aggregate all method names from different categories and cache result
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
        Return all public instance method names of the reflected class.

        Retrieves method names that are callable, not static or class methods,
        not properties, and do not start with underscores.

        Returns
        -------
        list of str
            List of public instance method names.
        """
        # Return cached public methods if available
        if "public_methods" in self:
            return self["public_methods"]

        class_name = self.getClassName()
        attributes = self._concrete.__dict__
        public_methods: list[str] = []

        # Collect only public instance methods
        for attr, value in attributes.items():
            if (
                callable(value)
                and not isinstance(value, (staticmethod, classmethod))
                and not isinstance(value, property)
            ):
                if attr.startswith("__") and attr.endswith("__"):
                    continue
                if attr.startswith(f"_{class_name}"):
                    continue
                if attr.startswith("_"):
                    continue
                public_methods.append(attr)

        self["public_methods"] = public_methods
        return public_methods

    def getPublicSyncMethods(self) -> list[str]:
        """
        Return all public synchronous method names of the reflected class.

        Filters public methods to include only those that are not coroutine
        functions.

        Returns
        -------
        list of str
            List of public synchronous method names.
        """
        if "public_sync_methods" in self:
            return self["public_sync_methods"]

        # Filter out coroutine functions from public methods
        methods = self.getPublicMethods()
        sync_methods: list[str] = []
        for method in methods:
            if not inspect.iscoroutinefunction(getattr(self._concrete, method)):
                sync_methods.append(method)
        self["public_sync_methods"] = sync_methods
        return sync_methods

    def getPublicAsyncMethods(self) -> list[str]:
        """
        Return all public asynchronous method names of the reflected class.

        Filters public methods to include only coroutine functions.

        Returns
        -------
        list of str
            List of public asynchronous method names.
        """
        if "public_async_methods" in self:
            return self["public_async_methods"]

        # Collect coroutine functions among public methods
        methods = self.getPublicMethods()
        async_methods: list[str] = []
        for method in methods:
            if inspect.iscoroutinefunction(getattr(self._concrete, method)):
                async_methods.append(method)
        self["public_async_methods"] = async_methods
        return async_methods

    def getProtectedMethods(self) -> list[str]:
        """
        Return all protected instance method names.

        Protected methods start with a single underscore, are not dunder,
        and are not private (name-mangled). Excludes static, class methods,
        and properties.

        Returns
        -------
        list of str
            List of protected instance method names.
        """
        # Return cached protected methods if available
        if "protected_methods" in self:
            return self["protected_methods"]

        attributes = self._concrete.__dict__
        protected_methods: list[str] = []

        # Collect only protected instance methods
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
        return protected_methods

    def getProtectedSyncMethods(self) -> list:
        """
        Return all protected synchronous method names.

        Filters protected methods to include only those that are not coroutine
        functions.

        Returns
        -------
        list
            List of protected synchronous method names.
        """
        if "protected_sync_methods" in self:
            return self["protected_sync_methods"]

        # Filter out coroutine functions from protected methods
        methods = self.getProtectedMethods()
        sync_methods = []
        for method in methods:
            if not inspect.iscoroutinefunction(getattr(self._concrete, method)):
                sync_methods.append(method)
        self["protected_sync_methods"] = sync_methods
        return sync_methods

    def getProtectedAsyncMethods(self) -> list:
        """
        Retrieve all protected asynchronous method names.

        Filters protected methods to include only those that are coroutine
        functions.

        Returns
        -------
        list
            List of protected asynchronous method names.
        """
        # Return cached protected async methods if available
        if "protected_async_methods" in self:
            return self["protected_async_methods"]

        methods = self.getProtectedMethods()
        async_methods = []
        for method in methods:
            # Check if the method is a coroutine function
            if inspect.iscoroutinefunction(getattr(self._concrete, method)):
                async_methods.append(method)
        self["protected_async_methods"] = async_methods
        return async_methods

    def getPrivateMethods(self) -> list[str]:
        """
        Retrieve all private instance method names.

        Private methods are those using Python's name mangling convention
        (class name prefix). Name mangling is resolved in the returned names.

        Returns
        -------
        list of str
            List of private instance method names with mangling removed.
        """
        # Return cached private methods if available
        if "private_methods" in self:
            return self["private_methods"]

        class_name = self.getClassName()
        attributes = self._concrete.__dict__
        private_methods: list[str] = []

        # Collect only private instance methods, excluding static/class methods
        for attr, value in attributes.items():
            if (
                callable(value)
                and not isinstance(value, (staticmethod, classmethod))
                and not isinstance(value, property)
                and attr.startswith(f"_{class_name}")
            ):
                # Remove name mangling for cleaner output
                private_methods.append(str(attr).replace(f"_{class_name}", ""))

        self["private_methods"] = private_methods
        return private_methods

    def getPrivateSyncMethods(self) -> list[str]:
        """
        Return all private synchronous method names of the class.

        Returns
        -------
        list of str
            List of private synchronous method names.
        """
        if "private_sync_methods" in self:
            return self["private_sync_methods"]

        # Collect private methods that are not coroutine functions
        methods = self.getPrivateMethods()
        sync_methods: list[str] = []
        for method in methods:
            if not inspect.iscoroutinefunction(
                getattr(self._concrete, f"_{self.getClassName()}{method}"),
            ):
                sync_methods.append(method)
        self["private_sync_methods"] = sync_methods
        return sync_methods

    def getPrivateAsyncMethods(self) -> list[str]:
        """
        Return all private asynchronous method names of the class.

        Finds private methods (using name mangling) that are coroutine functions.

        Returns
        -------
        list of str
            List of private asynchronous method names.
        """
        if "private_async_methods" in self:
            return self["private_async_methods"]

        # Collect private methods that are coroutine functions
        methods = self.getPrivateMethods()
        async_methods: list[str] = []
        for method in methods:
            mangled_name = f"_{self.getClassName()}{method}"
            if inspect.iscoroutinefunction(getattr(self._concrete, mangled_name)):
                async_methods.append(method)
        self["private_async_methods"] = async_methods
        return async_methods

    def getPublicClassMethods(self) -> list[str]:
        """
        Return a list of public class method names.

        Public class methods are those that do not start with an underscore,
        are not dunder, and are not private (name-mangled).

        Returns
        -------
        list of str
            List of public class method names.
        """
        if "public_class_methods" in self:
            return self["public_class_methods"]

        class_name = self.getClassName()
        attributes = self._concrete.__dict__
        public_class_methods: list[str] = []

        # Collect only public class methods, excluding dunder, protected, and private
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
        return public_class_methods

    def getPublicClassSyncMethods(self) -> list[str]:
        """
        Return all public synchronous class method names.

        Returns
        -------
        list of str
            List of public synchronous class method names.
        """
        if "public_class_sync_methods" in self:
            return self["public_class_sync_methods"]

        # Filter public class methods to include only synchronous ones
        methods = self.getPublicClassMethods()
        sync_methods: list[str] = []
        for method in methods:
            if not inspect.iscoroutinefunction(getattr(self._concrete, method)):
                sync_methods.append(method)
        self["public_class_sync_methods"] = sync_methods
        return sync_methods

    def getPublicClassAsyncMethods(self) -> list[str]:
        """
        Return all public asynchronous class method names.

        Returns
        -------
        list of str
            List of public asynchronous class method names.
        """
        if "public_class_async_methods" in self:
            return self["public_class_async_methods"]

        # Collect coroutine functions among public class methods
        methods = self.getPublicClassMethods()
        async_methods: list[str] = []
        for method in methods:
            if inspect.iscoroutinefunction(getattr(self._concrete, method)):
                async_methods.append(method)
        self["public_class_async_methods"] = async_methods
        return async_methods

    def getProtectedClassMethods(self) -> list[str]:
        """
        Return a list of protected class method names.

        Protected class methods start with a single underscore, are not dunder,
        and are not private (name-mangled).

        Returns
        -------
        list of str
            List of protected class method names.
        """
        if "protected_class_methods" in self:
            return self["protected_class_methods"]

        class_name = self.getClassName()
        attributes = self._concrete.__dict__
        protected_class_methods: list[str] = []

        # Collect protected class methods, excluding dunder and private
        for attr, value in attributes.items():
            if (
                isinstance(value, classmethod)
                and attr.startswith("_")
                and not attr.startswith("__")
                and not attr.startswith(f"_{class_name}")
            ):
                protected_class_methods.append(attr)

        self["protected_class_methods"] = protected_class_methods
        return protected_class_methods

    def getProtectedClassSyncMethods(self) -> list[str]:
        """
        Return all protected synchronous class method names.

        Returns
        -------
        list of str
            List of protected synchronous class method names.
        """
        if "protected_class_sync_methods" in self:
            return self["protected_class_sync_methods"]

        # Filter protected class methods to include only synchronous ones
        methods = self.getProtectedClassMethods()
        sync_methods: list[str] = []
        for method in methods:
            if not inspect.iscoroutinefunction(getattr(self._concrete, method)):
                sync_methods.append(method)
        self["protected_class_sync_methods"] = sync_methods
        return sync_methods

    def getProtectedClassAsyncMethods(self) -> list:
        """
        Return all protected asynchronous class method names.

        Returns
        -------
        list
            List of protected asynchronous class method names.
        """
        # Return cached protected async class methods if available
        if "protected_class_async_methods" in self:
            return self["protected_class_async_methods"]

        methods = self.getProtectedClassMethods()
        async_methods = []
        for method in methods:
            # Check if the method is a coroutine function
            if inspect.iscoroutinefunction(getattr(self._concrete, method)):
                async_methods.append(method)
        self["protected_class_async_methods"] = async_methods
        return async_methods

    def getPrivateClassMethods(self) -> list[str]:
        """
        Return a list of private class method names.

        Private class methods use Python's name mangling convention and are
        defined with a double underscore prefix.

        Returns
        -------
        list of str
            List of private class method names with name mangling removed.
        """
        if "private_class_methods" in self:
            return self["private_class_methods"]

        class_name = self.getClassName()
        attributes = self._concrete.__dict__
        private_class_methods: list[str] = []

        # Collect private class methods, removing name mangling for output
        for attr, value in attributes.items():
            if (
                isinstance(value, classmethod)
                and attr.startswith(f"_{class_name}")
            ):
                private_class_methods.append(
                    str(attr).replace(f"_{class_name}", ""),
                )

        self["private_class_methods"] = private_class_methods
        return private_class_methods

    def getPrivateClassSyncMethods(self) -> list:
        """
        Return all private synchronous class method names.

        Returns
        -------
        list
            List of private synchronous class method names.
        """
        # Return cached result if available
        if "private_class_sync_methods" in self:
            return self["private_class_sync_methods"]

        methods = self.getPrivateClassMethods()
        sync_methods: list = []
        for method in methods:
            # Check if the method is not a coroutine function
            if not inspect.iscoroutinefunction(
                getattr(self._concrete, f"_{self.getClassName()}{method}"),
            ):
                sync_methods.append(method)
        self["private_class_sync_methods"] = sync_methods
        return sync_methods

    def getPrivateClassAsyncMethods(self) -> list:
        """
        Return all private asynchronous class method names.

        Finds private class methods (using name mangling) that are coroutine
        functions.

        Returns
        -------
        list
            List of private asynchronous class method names.
        """
        # Return cached result if available
        if "private_class_async_methods" in self:
            return self["private_class_async_methods"]

        methods = self.getPrivateClassMethods()
        async_methods: list = []
        for method in methods:
            # Check if the method is a coroutine function
            if inspect.iscoroutinefunction(
                getattr(self._concrete, f"_{self.getClassName()}{method}"),
            ):
                async_methods.append(method)
        self["private_class_async_methods"] = async_methods
        return async_methods

    def getPublicStaticMethods(self) -> list[str]:
        """
        Return a list of public static method names.

        Scans the class dictionary for static methods that are public, i.e.,
        do not start with underscores or use name mangling.

        Returns
        -------
        list of str
            List of public static method names.
        """
        if "public_static_methods" in self:
            return self["public_static_methods"]

        class_name = self.getClassName()
        attributes = self._concrete.__dict__
        public_static_methods: list[str] = []

        # Collect public static methods, excluding dunder, protected, and private
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
        return public_static_methods

    def getPublicStaticSyncMethods(self) -> list[str]:
        """
        Return all public synchronous static method names of the class.

        Returns
        -------
        list of str
            List of public synchronous static method names.
        """
        if "public_static_sync_methods" in self:
            return self["public_static_sync_methods"]

        # Filter public static methods to include only synchronous ones
        methods = self.getPublicStaticMethods()
        sync_methods: list[str] = []
        for method in methods:
            if not inspect.iscoroutinefunction(getattr(self._concrete, method)):
                sync_methods.append(method)
        self["public_static_sync_methods"] = sync_methods
        return sync_methods

    def getPublicStaticAsyncMethods(self) -> list:
        """
        Return all public asynchronous static method names of the class.

        Returns
        -------
        list
            List of public asynchronous static method names.
        """
        # Return cached result if available
        if "public_static_async_methods" in self:
            return self["public_static_async_methods"]

        methods = self.getPublicStaticMethods()
        async_methods = []
        # Collect coroutine functions among public static methods
        for method in methods:
            if inspect.iscoroutinefunction(getattr(self._concrete, method)):
                async_methods.append(method)
        self["public_static_async_methods"] = async_methods
        return async_methods

    def getProtectedStaticMethods(self) -> list[str]:
        """
        Return a list of protected static method names.

        Protected static methods start with a single underscore, are not dunder,
        and are not private (name-mangled).

        Returns
        -------
        list of str
            List of protected static method names.
        """
        # Return cached protected static methods if available
        if "protected_static_methods" in self:
            return self["protected_static_methods"]

        class_name = self.getClassName()
        attributes = self._concrete.__dict__
        protected_static_methods: list[str] = []

        # Collect protected static methods, excluding dunder and private
        for attr, value in attributes.items():
            if (
                isinstance(value, staticmethod)
                and attr.startswith("_")
                and not attr.startswith("__")
                and not attr.startswith(f"_{class_name}")
            ):
                protected_static_methods.append(attr)

        self["protected_static_methods"] = protected_static_methods
        return protected_static_methods

    def getProtectedStaticSyncMethods(self) -> list:
        """
        Return all protected synchronous static method names of the class.

        Returns
        -------
        list
            List of protected synchronous static method names.
        """
        # Return cached result if available
        if "protected_static_sync_methods" in self:
            return self["protected_static_sync_methods"]

        methods = self.getProtectedStaticMethods()
        sync_methods = []
        for method in methods:
            # Check if the method is not a coroutine function
            if not inspect.iscoroutinefunction(getattr(self._concrete, method)):
                sync_methods.append(method)
        self["protected_static_sync_methods"] = sync_methods
        return sync_methods

    def getProtectedStaticAsyncMethods(self) -> list:
        """
        Retrieve all protected asynchronous static method names.

        Returns
        -------
        list
            List of protected asynchronous static method names.
        """
        # Return cached result if available
        if "protected_static_async_methods" in self:
            return self["protected_static_async_methods"]

        methods = self.getProtectedStaticMethods()
        async_methods = []
        # Collect coroutine functions among protected static methods
        for method in methods:
            if inspect.iscoroutinefunction(getattr(self._concrete, method)):
                async_methods.append(method)
        self["protected_static_async_methods"] = async_methods
        return async_methods

    def getPrivateStaticMethods(self) -> list[str]:
        """
        Return the names of all private static methods of the class.

        Private static methods are those using Python's name mangling
        convention (class name prefix).

        Returns
        -------
        list of str
            List of private static method names with name mangling removed.
        """
        # Return cached private static methods if available
        if "private_static_methods" in self:
            return self["private_static_methods"]

        class_name = self.getClassName()
        attributes = self._concrete.__dict__
        private_static_methods: list[str] = []

        # Collect private static methods, removing name mangling for output
        for attr, value in attributes.items():
            if (
                isinstance(value, staticmethod)
                and attr.startswith(f"_{class_name}")
            ):
                private_static_methods.append(
                    str(attr).replace(f"_{class_name}", ""),
                )

        self["private_static_methods"] = private_static_methods
        return private_static_methods

    def getPrivateStaticSyncMethods(self) -> list:
        """
        Return all private synchronous static method names of the class.

        Returns
        -------
        list
            List of private synchronous static method names.
        """
        # Return cached result if available
        if "private_static_sync_methods" in self:
            return self["private_static_sync_methods"]

        methods = self.getPrivateStaticMethods()
        sync_methods = []
        # Collect private static methods that are not coroutine functions
        for method in methods:
            mangled_name = f"_{self.getClassName()}{method}"
            if not inspect.iscoroutinefunction(getattr(self._concrete, mangled_name)):
                sync_methods.append(method)
        self["private_static_sync_methods"] = sync_methods
        return sync_methods

    def getPrivateStaticAsyncMethods(self) -> list:
        """
        Retrieve all private asynchronous static method names of the class.

        Returns
        -------
        list
            List of private asynchronous static method names.
        """
        # Return cached result if available
        if "private_static_async_methods" in self:
            return self["private_static_async_methods"]

        methods = self.getPrivateStaticMethods()
        async_methods: list = []
        # Collect private static methods that are coroutine functions
        for method in methods:
            mangled_name = f"_{self.getClassName()}{method}"
            if inspect.iscoroutinefunction(getattr(self._concrete, mangled_name)):
                async_methods.append(method)

        # Cache the result
        self["private_static_async_methods"] = async_methods
        return async_methods

    def getDunderMethods(self) -> list[str]:
        """
        Retrieve all dunder (magic) method names from the reflected class.

        Finds callable attributes that follow the double underscore naming
        convention, excluding static, class methods, and properties.

        Returns
        -------
        list of str
            List of dunder method names available in the class.
        """
        # Return cached dunder methods if available
        if "dunder_methods" in self:
            return self["dunder_methods"]

        attributes = self._concrete.__dict__
        dunder_methods: list[str] = []
        exclude: list[str] = []

        # Collect callable dunder methods, excluding static/class methods/properties
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
        return dunder_methods

    def getMagicMethods(self) -> list[str]:
        """
        Return all magic (dunder) method names from the reflected class.

        This is an alias for ``getDunderMethods()``, providing alternative
        naming for accessing double underscore methods.

        Returns
        -------
        list of str
            List of magic method names available in the class.
        """
        return self.getDunderMethods()

    def getProperties(self) -> list[str]:
        """
        Return all property names defined in the reflected class.

        Scans the class dictionary for property objects and returns their names
        with private attribute name mangling resolved.

        Returns
        -------
        list of str
            List of all property names in the class, with name mangling removed.
        """
        # Return cached properties if available
        if "properties" in self:
            return self["properties"]

        properties: list[str] = []
        class_name = self.getClassName()
        # Iterate over class dictionary to find property objects
        for name, prop in self._concrete.__dict__.items():
            if isinstance(prop, property):
                # Remove private attribute name mangling for cleaner output
                name_prop = name.replace(f"_{class_name}", "")
                properties.append(name_prop)
        self["properties"] = properties
        return self["properties"]

    def getPublicProperties(self) -> list[str]:
        """
        Return all public property names of the reflected class.

        Properties are considered public if their names do not start with
        underscores or the class name (for name-mangled attributes).

        Returns
        -------
        list of str
            List of public property names with name mangling resolved.
        """
        if "public_properties" in self:
            return self["public_properties"]

        properties: list[str] = []
        cls_name: str = self.getClassName()
        # Iterate over class dictionary to find public property objects
        for name, prop in self._concrete.__dict__.items():
            if (
                isinstance(prop, property)
                and not name.startswith("_")
                and not name.startswith(f"_{cls_name}")
            ):
                properties.append(name.replace(f"_{cls_name}", ""))
        self["public_properties"] = properties
        return properties

    def getProtectedProperties(self) -> list[str]:
        """
        Retrieve all protected property names from the reflected class.

        Protected properties are those that start with a single underscore,
        are not private (name-mangled), and are not dunder attributes.

        Returns
        -------
        list of str
            List of protected property names.
        """
        # Return cached protected properties if available
        if "protected_properties" in self:
            return self["protected_properties"]

        properties: list[str] = []
        class_name: str = self.getClassName()
        # Iterate over class dictionary to find protected property objects
        for name, prop in self._concrete.__dict__.items():
            if (
                isinstance(prop, property)
                and name.startswith("_")
                and not name.startswith("__")
                and not name.startswith(f"_{class_name}")
            ):
                properties.append(name)
        self["protected_properties"] = properties
        return properties

    def getPrivateProperties(self) -> list[str]:
        """
        Return all private property names of the reflected class.

        Private properties use Python's name mangling convention (class name
        prefix). The returned names have name mangling removed.

        Returns
        -------
        list of str
            List of private property names with name mangling removed.
        """
        # Return cached private properties if available
        if "private_properties" in self:
            return self["private_properties"]

        properties: list[str] = []
        class_name = self.getClassName()
        # Iterate over class dictionary to find private property objects
        for name, prop in self._concrete.__dict__.items():
            if (
                isinstance(prop, property)
                and name.startswith(f"_{class_name}")
                and not name.startswith("__")
            ):
                # Remove name mangling for cleaner output
                properties.append(name.replace(f"_{class_name}", ""))
        self["private_properties"] = properties
        return properties

    def getProperty(self, name: str) -> Any:
        """
        Retrieve the value of a property from the reflected class.

        Handles private property name mangling and validates that the requested
        attribute is a property object.

        Parameters
        ----------
        name : str
            Name of the property to retrieve.

        Returns
        -------
        Any
            The current value of the property.

        Raises
        ------
        ValueError
            If the property does not exist or is not accessible.
        """
        # Handle private property name mangling for double underscore properties
        if name.startswith("__") and not name.endswith("__"):
            class_name = self.getClassName()
            name = f"_{class_name}{name}"

        if not hasattr(self._concrete, name):
            error_msg = (
                f"Property '{name}' does not exist in class '{self.getClassName()}'."
            )
            raise ValueError(error_msg)

        prop = getattr(self._concrete, name)
        if not isinstance(prop, property):
            error_msg = (
                f"'{name}' is not a property in class '{self.getClassName()}'."
            )
            raise TypeError(error_msg)

        # Call the property's getter with the class as the instance
        return prop.fget(self._concrete)

    def getPropertySignature(self, name: str) -> inspect.Signature:
        """
        Return the signature of a property's getter method.

        Parameters
        ----------
        name : str
            Name of the property to inspect.

        Returns
        -------
        inspect.Signature
            The signature object of the property's getter function.

        Raises
        ------
        ValueError
            If the property does not exist or is not accessible.
        """
        # Return cached signature if available
        if f"property_signature_{name}" in self:
            return self[f"property_signature_{name}"]

        # Handle private property name mangling for double underscore properties
        if name.startswith("__") and not name.endswith("__"):
            class_name: str = self.getClassName()
            name = f"_{class_name}{name}"

        if not hasattr(self._concrete, name):
            error_msg = (
                f"Property '{name}' does not exist in class "
                f"'{self.getClassName()}'."
            )
            raise ValueError(error_msg)

        prop = getattr(self._concrete, name)
        if not isinstance(prop, property):
            error_msg = (
                f"'{name}' is not a property in class '{self.getClassName()}'."
            )
            raise TypeError(error_msg)

        # Cache and return the signature of the property's getter function
        self[f"property_signature_{name}"] = inspect.signature(prop.fget)
        return self[f"property_signature_{name}"]

    def getPropertyDocstring(self, name: str) -> str | None:
        """
        Retrieve the docstring of a property's getter method.

        Parameters
        ----------
        name : str
            Name of the property to inspect.

        Returns
        -------
        str or None
            The docstring of the property's getter function, or None if not defined.

        Raises
        ------
        ValueError
            If the property does not exist or is not accessible.
        """
        # Return cached docstring if available
        if f"property_docstring_{name}" in self:
            return self[f"property_docstring_{name}"]

        # Handle private property name mangling
        if name.startswith("__") and not name.endswith("__"):
            class_name: str = self.getClassName()
            name = f"_{class_name}{name}"

        if not hasattr(self._concrete, name):
            error_msg = (
                f"Property '{name}' does not exist in class '{self.getClassName()}'."
            )
            raise ValueError(error_msg)

        prop = getattr(self._concrete, name)
        if not isinstance(prop, property):
            error_msg = (
                f"'{name}' is not a property in class '{self.getClassName()}'."
            )
            raise TypeError(error_msg)

        # Cache and return the docstring of the property's getter function
        self[f"property_docstring_{name}"] = prop.fget.__doc__ if prop.fget else None
        return self[f"property_docstring_{name}"]

    def getConstructorSignature(self) -> inspect.Signature:
        """
        Return the signature of the class constructor.

        Returns
        -------
        inspect.Signature
            Signature object for the __init__ method, containing parameter
            information.
        """
        # Return cached constructor signature if available
        if "constructor_signature" in self:
            return self["constructor_signature"]

        # Cache and return the signature of the __init__ method
        self["constructor_signature"] = inspect.signature(self._concrete.__init__)
        return self["constructor_signature"]

    def constructorSignature(self) -> Signature:
        """
        Analyze the constructor's dependencies.

        Analyzes the constructor parameters to identify resolved and unresolved
        dependencies using type annotations and default values.

        Returns
        -------
        Signature
            Structured representation of resolved and unresolved dependencies.
        """
        # Return cached analysis if available
        if "constructor_signature_analysis" in self:
            return self["constructor_signature_analysis"]

        # Analyze constructor dependencies and cache the result
        self["constructor_signature_analysis"] = (
            ReflectDependencies(self._concrete).constructorSignature()
        )
        return self["constructor_signature_analysis"]

    def methodSignature(self, method_name: str) -> Signature:
        """
        Analyze the dependencies of a specific method.

        Parameters
        ----------
        method_name : str
            Name of the method to analyze.

        Returns
        -------
        Signature
            Structured representation of resolved and unresolved dependencies.

        Raises
        ------
        AttributeError
            If the method does not exist in the class.
        """
        # Return cached analysis if available
        if f"method_signature_analysis_{method_name}" in self:
            return self[f"method_signature_analysis_{method_name}"]

        # Check if the method exists in the class
        if not self.hasMethod(method_name):
            error_msg = (
                f"Method '{method_name}' does not exist on '{self.getClassName()}'."
            )
            raise AttributeError(error_msg)

        # Handle name mangling for private methods
        if method_name.startswith("__") and not method_name.endswith("__"):
            class_name = self.getClassName()
            method_name = f"_{class_name}{method_name}"

        # Analyze method dependencies and cache the result
        self[f"method_signature_analysis_{method_name}"] = (
            ReflectDependencies(self._concrete).methodSignature(method_name)
        )
        return self[f"method_signature_analysis_{method_name}"]

    def clearCache(self) -> None:
        """
        Clear the internal memory cache.

        Removes all cached entries stored in the reflection instance. Subsequent
        method calls will recompute and cache results.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Clear the internal memory cache for reflection results
        self.__memory_cache.clear()
