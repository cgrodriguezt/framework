from __future__ import annotations
import inspect
import keyword
from typing import TYPE_CHECKING, Any
from orionis.services.introspection.dependencies.reflection import ReflectDependencies
from orionis.services.introspection.instances.contracts.reflection import (
    IReflectionInstance,
)
from orionis.services.introspection.reflection import Reflection

if TYPE_CHECKING:
    from collections.abc import Callable
    from orionis.services.introspection.dependencies.entities.signature import (
        SignatureArguments,
    )

class ReflectionInstance(IReflectionInstance):

    # ruff: noqa : ANN401, PERF403

    def __init__(self, instance: Any) -> None:
        """
        Initialize the ReflectionInstance with the given object instance.

        Parameters
        ----------
        instance : Any
            The object instance to reflect.

        Raises
        ------
        TypeError
            If the provided instance is not a valid object instance or is of a
            built-in/abstract base class.
        ValueError
            If the instance is from '__main__'.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Ensure input is an object instance, not a class
        if not (isinstance(instance, object) and not isinstance(instance, type)):
            error_msg = (
                "The provided instance must be an object instance, not a class."
            )
            raise TypeError(error_msg)

        # Exclude built-in or abstract base class instances
        module: str = instance.__class__.__module__
        if module in {"builtins", "abc"}:
            error_msg = (
                "Cannot reflect on instances of built-in or abstract base classes."
            )
            raise TypeError(error_msg)

        # Validate that the instance is a proper object
        if not Reflection.isInstance(instance):
            error_msg = "The provided instance is not a valid object instance."
            raise TypeError(error_msg)

        # Prevent reflection on instances from '__main__'
        if module == "__main__":
            error_msg = "Cannot reflect on instances from '__main__'."
            raise ValueError(error_msg)

        self._instance: Any = instance
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

    def getInstance(self) -> Any:
        """
        Return the reflected object instance.

        Returns
        -------
        Any
            The object instance being reflected upon.
        """
        return self._instance

    def getClass(self) -> type:
        """
        Return the class of the instance.

        Returns
        -------
        type
            The class object of the instance.
        """
        return self._instance.__class__

    def getClassName(self) -> str:
        """
        Return the name of the instance's class.

        Returns
        -------
        str
            The name of the class.
        """
        return self._instance.__class__.__name__

    def getModuleName(self) -> str:
        """
        Return the name of the module where the class is defined.

        Returns
        -------
        str
            The module name where the class is defined.
        """
        return self._instance.__class__.__module__

    def getModuleWithClassName(self) -> str:
        """
        Return the module and class name as a single string.

        Returns
        -------
        str
            The module name and class name in the format 'module.ClassName'.
        """
        return f"{self.getModuleName()}.{self.getClassName()}"

    def getDocstring(self) -> str | None:
        """
        Return the docstring of the instance's class.

        Returns
        -------
        str or None
            The docstring of the class, or None if not available.
        """
        return self._instance.__class__.__doc__

    def getBaseClasses(self) -> tuple[type, ...]:
        """
        Return the base classes of the instance's class.

        Returns
        -------
        tuple of type
            Tuple containing the base classes of the class.
        """
        return self._instance.__class__.__bases__

    def getSourceCode(self, method: str | None = None) -> str | None:
        """
        Retrieve the source code for the class or a specific method.

        Parameters
        ----------
        method : str or None, optional
            Name of the method to retrieve source code for. If None, retrieves
            the source code of the class.

        Returns
        -------
        str or None
            The source code as a string if available, otherwise None.

        Notes
        -----
        Handles name mangling for private methods. Returns None if the source
        code cannot be retrieved (e.g., for built-in or dynamically generated
        objects).
        """
        try:
            # Return cached class source code if available
            if not method:
                if "source_code" in self:
                    return self["source_code"]
                self["source_code"] = inspect.getsource(self._instance.__class__)
                return self["source_code"]

            # Return cached method source code if available
            if f"{method}_source_code" in self:
                return self[f"{method}_source_code"]

            # Handle private method name mangling
            if method.startswith("__") and not method.endswith("__"):
                class_name = self.getClassName()
                method = f"_{class_name}{method}"

            # Check if the method exists
            if not self.hasMethod(method):
                return None

            # Retrieve and cache the source code of the specified method
            self[f"{method}_source_code"] = inspect.getsource(
                getattr(self._instance.__class__, method),
            )
            return self[f"{method}_source_code"]

        except (TypeError, OSError):
            # Return None if the source code cannot be retrieved
            return None

    def getFile(self) -> str | None:
        """
        Return the file path where the class is defined.

        Returns
        -------
        str or None
            The file path of the class definition, or None if unavailable.
        """
        # Return cached file path if available
        if "file" in self:
            return self["file"]
        try:
            # Retrieve the file path of the class definition
            self["file"] = inspect.getfile(self._instance.__class__)
            return self["file"]
        except (TypeError, OSError):
            # Return None if the file path cannot be determined
            return None

    def getAnnotations(self) -> dict[str, type]:
        """
        Retrieve type annotations of the class.

        Returns
        -------
        dict[str, type]
            Dictionary mapping attribute names to their type annotations.
        """
        # Return cached annotations if available
        if "annotations" in self:
            return self["annotations"]

        # Collect type annotations, unmangling private attribute names
        annotations: dict[str, type] = {}
        class_name = self.getClassName()
        # Use getattr to support classes without __annotations__
        class_annotations = getattr(self._instance.__class__, "__annotations__", {})
        for k, v in class_annotations.items():
            unmangled = str(k).replace(f"_{class_name}", "")
            annotations[unmangled] = v
        self["annotations"] = annotations
        return self["annotations"]

    def hasAttribute(self, name: str) -> bool:
        """
        Check if the instance has a specific attribute.

        Parameters
        ----------
        name : str
            Attribute name to check.

        Returns
        -------
        bool
            True if the attribute exists, False otherwise.
        """
        # Check attribute existence in both custom attributes and instance attributes
        return name in self.getAttributes() or hasattr(self._instance, name)

    def getAttribute(self, name: str, default: Any = None) -> Any:
        """
        Retrieve the value of an attribute by name from the instance.

        Parameters
        ----------
        name : str
            Name of the attribute to retrieve.
        default : Any, optional
            Value to return if the attribute does not exist. Defaults to None.

        Returns
        -------
        Any
            Value of the specified attribute if it exists, otherwise the provided
            `default` value.

        Raises
        ------
        AttributeError
            If the attribute does not exist and no default value is provided.

        Notes
        -----
        This method first checks the instance's attributes dictionary for the
        given name. If not found, it attempts to retrieve the attribute directly
        from the instance using `getattr`. If the attribute is still not found,
        the `default` value is returned.
        """
        # Retrieve all attributes (public, protected, private, dunder)
        attrs: dict[str, Any] = self.getAttributes()
        # Return the attribute value from the dictionary or use getattr fallback
        return attrs.get(name, getattr(self._instance, name, default))

    def setAttribute(self, name: str, value: Any) -> bool:
        """
        Set the value of an attribute on the instance.

        Parameters
        ----------
        name : str
            Name of the attribute to set.
        value : Any
            Value to assign to the attribute.

        Returns
        -------
        bool
            True if the attribute was set successfully.

        Raises
        ------
        AttributeError
            If the attribute name is invalid, is a keyword, or the value is callable.
        """
        # Validate attribute name: must be identifier and not a keyword
        if (
            not isinstance(name, str) or
            not name.isidentifier() or
            keyword.iskeyword(name)
        ):
            error_msg = (
                f"Invalid method name '{name}'. Must be a valid Python identifier "
                "and not a keyword."
            )
            raise AttributeError(error_msg)

        # Prevent setting callable values as attributes
        if callable(value):
            error_msg = (
                f"Cannot set attribute '{name}' to a callable. Use setMethod instead."
            )
            raise TypeError(error_msg)

        # Handle private attribute name mangling for correct lookup
        if name.startswith("__") and not name.endswith("__"):
            class_name = self.getClassName()
            name = f"_{class_name}{name}"

        # Set the attribute value on the instance
        setattr(self._instance, name, value)

        # Clear cache to ensure consistency after setting a new attribute
        self.__memory_cache.clear()

        # Return True to indicate the attribute was set successfully
        return True

    def removeAttribute(self, name: str) -> bool:
        """
        Remove an attribute from the instance.

        Parameters
        ----------
        name : str
            Name of the attribute to remove.

        Returns
        -------
        bool
            True if the attribute was removed successfully.

        Raises
        ------
        AttributeError
            If the attribute does not exist or is read-only.

        Notes
        -----
        Clears the memory cache after removal.
        """
        # Check if the attribute exists before attempting removal
        if self.getAttribute(name) is None:
            error_msg = (
                f"'{self.getClassName()}' object has no attribute '{name}'."
            )
            raise AttributeError(error_msg)
        # Handle private attribute name mangling for correct lookup
        if name.startswith("__") and not name.endswith("__"):
            class_name = self.getClassName()
            name = f"_{class_name}{name}"

        # Remove the attribute from the instance
        delattr(self._instance, name)

        # Clear cache to ensure consistency after removing the attribute
        self.__memory_cache.clear()

        # Return True to indicate the attribute was removed successfully
        return True

    def getAttributes(self) -> dict[str, Any]:
        """
        Aggregate all attributes of the instance.

        Combines public, protected, private, and dunder attributes into a single
        dictionary. Private attribute names are unmangled. The result is cached
        for performance.

        Returns
        -------
        dict[str, Any]
            Dictionary mapping attribute names to their values for all visibility
            levels.
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

    def getPublicAttributes(self) -> dict[str, Any]:
        """
        Return all public attributes of the instance.

        Parameters
        ----------
        self : ReflectionInstance

        Returns
        -------
        dict[str, Any]
            Dictionary mapping public attribute names to their values. Excludes
            dunder, protected, and private attributes.
        """
        # Return cached public attributes if available
        if "public_attributes" in self:
            return self["public_attributes"]

        class_name = self.getClassName()
        attributes: dict[str, Any] = vars(self._instance)
        public: dict[str, Any] = {}

        # Exclude dunder, protected, and private attributes from the result
        for attr, value in attributes.items():
            if attr.startswith("__") and attr.endswith("__"):
                continue
            if attr.startswith(f"_{class_name}"):
                continue
            if attr.startswith("_"):
                continue
            public[attr] = value

        self["public_attributes"] = public
        return public

    def getProtectedAttributes(self) -> dict[str, Any]:
        """
        Return all protected attributes of the instance.

        Parameters
        ----------
        self : ReflectionInstance

        Returns
        -------
        dict[str, Any]
            Dictionary containing protected attribute names and their values.
            Protected attributes start with a single underscore, are not dunder,
            and are not private (do not start with the class name).
        """
        # Return cached protected attributes if available
        if "protected_attributes" in self:
            return self["protected_attributes"]

        class_name = self.getClassName()
        attributes: dict[str, Any] = vars(self._instance)
        protected: dict[str, Any] = {}

        # Select protected attributes: single underscore, not dunder/private
        for attr, value in attributes.items():
            if (
                attr.startswith("_")
                and not attr.startswith("__")
                and not attr.startswith(f"_{class_name}")
            ):
                protected[attr] = value

        self["protected_attributes"] = protected
        return protected

    def getPrivateAttributes(self) -> dict[str, Any]:
        """
        Retrieve all private attributes of the instance.

        Parameters
        ----------
        self : ReflectionInstance

        Returns
        -------
        dict[str, Any]
            Dictionary mapping unmangled private attribute names to their values.
        """
        # Return cached private attributes if available
        if "private_attributes" in self:
            return self["private_attributes"]

        class_name = self.getClassName()
        attributes: dict[str, Any] = vars(self._instance)
        private: dict[str, Any] = {}

        # Select private attributes that start with the class name prefix
        for attr, value in attributes.items():
            if attr.startswith(f"_{class_name}"):
                # Unmangle the attribute name for clarity
                private[str(attr).replace(f"_{class_name}", "")] = value

        self["private_attributes"] = private
        return private

    def getDunderAttributes(self) -> dict[str, Any]:
        """
        Retrieve all dunder (double underscore) attributes of the instance.

        Parameters
        ----------
        self : ReflectionInstance

        Returns
        -------
        dict[str, Any]
            Dictionary mapping dunder attribute names to their values.
        """
        # Return cached dunder attributes if available
        if "dunder_attributes" in self:
            return self["dunder_attributes"]

        attributes: dict[str, Any] = vars(self._instance)
        dunder: dict[str, Any] = {}

        # Select dunder attributes that start and end with double underscores
        for attr, value in attributes.items():
            if attr.startswith("__") and attr.endswith("__"):
                dunder[attr] = value

        self["dunder_attributes"] = dunder
        return dunder

    def getMagicAttributes(self) -> dict[str, Any]:
        """
        Return all magic attributes of the instance.

        Returns
        -------
        dict[str, Any]
            Dictionary mapping magic attribute names to their values.
        """
        # Magic attributes are equivalent to dunder attributes in Python.
        return self.getDunderAttributes()

    def hasMethod(self, name: str) -> bool:
        """
        Determine if the instance has a specific method.

        Parameters
        ----------
        name : str
            Name of the method to check.

        Returns
        -------
        bool
            True if the method exists, otherwise False.

        Notes
        -----
        Checks the presence of the method in the aggregated method list.
        """
        return name in self.getMethods()

    def setMethod(self, name: str, method: Callable) -> bool:
        """
        Set a callable attribute as a method.

        Parameters
        ----------
        name : str
            Name of the method to set.
        method : Callable
            Callable object to assign as the method.

        Returns
        -------
        bool
            True if the method was set successfully.

        Raises
        ------
        AttributeError
            If the name is not a valid identifier, is a keyword, or the method
            is not callable.
        """
        # Validate method name: must be identifier and not a keyword
        if (
            not isinstance(name, str) or
            not name.isidentifier() or
            keyword.iskeyword(name)
        ):
            error_msg = (
                f"Invalid method name '{name}'. Must be a valid Python identifier "
                "and not a keyword."
            )
            raise AttributeError(error_msg)

        # Ensure the method is callable
        if not callable(method):
            error_msg = (
                f"Cannot set attribute '{name}' to a non-callable value."
            )
            raise TypeError(error_msg)

        # Handle private method name mangling for correct lookup
        if name.startswith("__") and not name.endswith("__"):
            class_name = self.getClassName()
            name = f"_{class_name}{name}"

        # Set the method on the instance
        setattr(self._instance, name, method)

        # Clear cached method information for consistency after setting a new method
        self.__memory_cache.clear()

        # Return True to indicate the method was set successfully
        return True

    def removeMethod(self, name: str) -> None:
        """
        Remove a method from the instance.

        Parameters
        ----------
        name : str
            Name of the method to remove.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        AttributeError
            If the method does not exist or is not callable.
        """
        # Handle private method name mangling for correct lookup
        if not self.hasMethod(name):
            error_msg = (
                f"Method '{name}' does not exist on '{self.getClassName()}'."
            )
            raise AttributeError(error_msg)

        # Remove the method from the class
        delattr(self._instance.__class__, name)

        # Clear cached method information for consistency after removal
        self.__memory_cache.clear()

    def getMethodSignature(self, name: str) -> inspect.Signature:
        """
        Retrieve the signature of a method.

        Parameters
        ----------
        name : str
            Name of the method.

        Returns
        -------
        inspect.Signature
            Signature object representing the method's parameters and return type.

        Raises
        ------
        AttributeError
            If the method does not exist or is not callable.
        """
        # Return cached method signature if available
        if f"{name}_method_signature" in self:
            return self[f"{name}_method_signature"]

        # Handle private method name mangling for correct lookup
        if name.startswith("__") and not name.endswith("__"):
            name = f"_{self.getClassName()}{name}"

        # Retrieve the method from the class and check if it is callable
        method = getattr(self._instance.__class__, name, None)
        if callable(method):
            self[f"{name}_method_signature"] = inspect.signature(method)
            return self[f"{name}_method_signature"]

        # Raise error if method is not callable
        error_msg = (
            f"Method '{name}' is not callable on '{self.getClassName()}'."
        )
        raise AttributeError(error_msg)

    def getMethodDocstring(self, name: str) -> str | None:
        """
        Retrieve the docstring of a method.

        Parameters
        ----------
        name : str
            Name of the method.

        Returns
        -------
        str | None
            The docstring of the method, or None if not available.

        Raises
        ------
        AttributeError
            If the method does not exist on the class.
        """
        # Return cached docstring if available
        if f"{name}_docstring" in self:
            return self[f"{name}_docstring"]

        # Handle private method name mangling for correct lookup
        if name.startswith("__") and not name.endswith("__"):
            class_name = self.getClassName()
            name = f"_{class_name}{name}"

        # Retrieve the method from the class and check its type
        method = getattr(self._instance.__class__, name, None)
        if callable(method):
            self[f"{name}_docstring"] = method.__doc__
            return self[f"{name}_docstring"]

        # Raise error if method does not exist
        error_msg = (
            f"Method '{name}' does not exist on '{self.getClassName()}'."
        )
        raise AttributeError(error_msg)

    def getMethods(self) -> list[str]:
        """
        Retrieve all method names associated with the instance.

        Aggregates method names from public, protected, private, class, and static
        categories by calling their respective getter methods. The result is cached
        for performance.

        Returns
        -------
        list of str
            List of all method names (instance, class, static) defined on the
            instance's class, including public, protected, and private methods.
        """
        # Return cached method names if available
        if "methods" in self:
            return self["methods"]

        # Aggregate all method names from different visibility and type categories
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
        Return all public method names of the instance.

        Parameters
        ----------
        self : ReflectionInstance
            The ReflectionInstance object.

        Returns
        -------
        list of str
            List of public method names. Public methods are not static, class,
            private, protected, or magic methods.
        """
        # Return cached public methods if available
        if "public_methods" in self:
            return self["public_methods"]

        class_name = self.getClassName()
        cls = self._instance.__class__
        public_methods: list[str] = []

        # Gather all class and static methods to exclude them from public methods
        class_methods: set[str] = set()
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, (staticmethod, classmethod)):
                class_methods.add(name)

        # Collect public instance methods (not static/class/private/protected/magic)
        for name, _ in inspect.getmembers(
            self._instance,
            predicate=inspect.ismethod,
        ):
            if (
                name not in class_methods
                and not (name.startswith("__") and name.endswith("__"))
                and not name.startswith(f"_{class_name}")
                and not (name.startswith("_") and not name.startswith(f"_{class_name}"))
            ):
                public_methods.append(name)

        self["public_methods"] = public_methods
        return public_methods

    def getPublicSyncMethods(self) -> list[str]:
        """
        Return all public synchronous method names of the instance.

        Returns
        -------
        list of str
            List of public synchronous method names.
        """
        # Return cached public sync methods if available
        if "public_sync_methods" in self:
            return self["public_sync_methods"]

        methods: list[str] = self.getPublicMethods()
        public_sync_methods: list[str] = [
            method for method in methods
            if not inspect.iscoroutinefunction(getattr(self._instance, method))
        ]
        self["public_sync_methods"] = public_sync_methods
        return public_sync_methods

    def getPublicAsyncMethods(self) -> list[str]:
        """
        Return all public asynchronous method names of the instance.

        Parameters
        ----------
        self : ReflectionInstance
            The ReflectionInstance object.

        Returns
        -------
        list of str
            List of public asynchronous method names.
        """
        # Return cached public async methods if available
        if "public_async_methods" in self:
            return self["public_async_methods"]

        methods: list[str] = self.getPublicMethods()
        public_async_methods: list[str] = [
            method for method in methods
            if inspect.iscoroutinefunction(getattr(self._instance, method))
        ]
        self["public_async_methods"] = public_async_methods
        return public_async_methods

    def getProtectedMethods(self) -> list[str]:
        """
        Return all protected method names of the instance.

        Parameters
        ----------
        self : ReflectionInstance
            The ReflectionInstance object.

        Returns
        -------
        list of str
            List of protected method names. Protected methods start with a single
            underscore, are not private (do not start with the class name), and
            are not dunder methods.
        """
        # Return cached protected methods if available
        if "protected_methods" in self:
            return self["protected_methods"]

        protected_methods: list[str] = []
        cls = self._instance.__class__

        # Collect protected instance methods (single underscore, not dunder/private)
        for name, _ in inspect.getmembers(
            self._instance, predicate=inspect.ismethod,
        ):
            attr = inspect.getattr_static(cls, name)
            # Skip static and class methods
            if isinstance(attr, (staticmethod, classmethod)):
                continue
            if (
                name.startswith("_")
                and not name.startswith("__")
                and not name.startswith(f"_{self.getClassName()}")
            ):
                protected_methods.append(name)

        self["protected_methods"] = protected_methods
        return protected_methods

    def getProtectedSyncMethods(self) -> list[str]:
        """
        Return all protected synchronous method names of the instance.

        Parameters
        ----------
        self : ReflectionInstance
            The ReflectionInstance object.

        Returns
        -------
        list of str
            List of protected synchronous method names.
        """
        # Return cached protected sync methods if available
        if "protected_sync_methods" in self:
            return self["protected_sync_methods"]

        methods: list[str] = self.getProtectedMethods()
        protected_sync_methods: list[str] = [
            method for method in methods
            if not inspect.iscoroutinefunction(getattr(self._instance, method))
        ]
        self["protected_sync_methods"] = protected_sync_methods
        return protected_sync_methods

    def getProtectedAsyncMethods(self) -> list[str]:
        """
        Retrieve all protected asynchronous method names of the instance.

        Parameters
        ----------
        self : ReflectionInstance
            The ReflectionInstance object.

        Returns
        -------
        list of str
            List of protected asynchronous method names.

        Notes
        -----
        Protected asynchronous methods start with a single underscore, are not private,
        and are coroutine functions.
        """
        # Return cached protected async methods if available
        if "protected_async_methods" in self:
            return self["protected_async_methods"]

        methods: list[str] = self.getProtectedMethods()
        protected_async_methods: list[str] = [
            method for method in methods
            if inspect.iscoroutinefunction(getattr(self._instance, method))
        ]
        self["protected_async_methods"] = protected_async_methods
        return protected_async_methods

    def getPrivateMethods(self) -> list[str]:
        """
        Return all private method names of the instance.

        Private methods are those whose names start with the class name prefix
        (name-mangled), but do not start with double underscores.

        Returns
        -------
        list of str
            List of private method names, unmangled (without class name prefix).
        """
        # Return cached private methods if available
        if "private_methods" in self:
            return self["private_methods"]

        class_name = self.getClassName()
        private_methods: list[str] = []
        cls = self._instance.__class__

        # Collect private instance methods (start with class name prefix)
        for name, _ in inspect.getmembers(
            self._instance, predicate=inspect.ismethod,
        ):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, (staticmethod, classmethod)):
                continue
            if name.startswith(f"_{class_name}") and not name.startswith("__"):
                # Unmangle the method name before appending
                private_methods.append(name.replace(f"_{class_name}", ""))

        self["private_methods"] = private_methods
        return private_methods

    def getPrivateSyncMethods(self) -> list[str]:
        """
        Retrieve all private synchronous method names of the instance.

        Returns
        -------
        list of str
            List of private synchronous method names (unmangled).
        """
        # Return cached private sync methods if available
        if "private_sync_methods" in self:
            return self["private_sync_methods"]

        class_name = self.getClassName()
        private_methods: list[str] = []
        cls = self._instance.__class__

        # Collect private sync instance methods (start with class name prefix)
        for name, method in inspect.getmembers(
            self._instance,
            predicate=inspect.ismethod,
        ):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, (staticmethod, classmethod)):
                continue
            if name.startswith(f"_{class_name}") and not name.startswith("__"):
                short_name = name.replace(f"_{class_name}", "")
                if not inspect.iscoroutinefunction(method):
                    private_methods.append(short_name)
        self["private_sync_methods"] = private_methods
        return private_methods

    def getPrivateAsyncMethods(self) -> list[str]:
        """
        Retrieve all private asynchronous method names of the instance.

        Returns
        -------
        list of str
            List of private asynchronous method names (unmangled).
        """
        # Return cached private async methods if available
        if "private_async_methods" in self:
            return self["private_async_methods"]

        class_name = self.getClassName()
        private_methods: list[str] = []
        cls = self._instance.__class__

        # Collect private async instance methods (start with class name prefix)
        for name, method in inspect.getmembers(
            self._instance,
            predicate=inspect.ismethod,
        ):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, (staticmethod, classmethod)):
                continue
            if name.startswith(f"_{class_name}") and not name.startswith("__"):
                short_name = name.replace(f"_{class_name}", "")
                if inspect.iscoroutinefunction(method):
                    private_methods.append(short_name)
        self["private_async_methods"] = private_methods
        return private_methods

    def getPublicClassMethods(self) -> list[str]:
        """
        Return all public class method names of the instance.

        Returns
        -------
        list of str
            List of public class method names.
        """
        # Return cached public class methods if available
        if "public_class_methods" in self:
            return self["public_class_methods"]

        cls = self._instance.__class__
        class_methods: list[str] = []

        # Iterate over all attributes of the class to find public class methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, classmethod) and not name.startswith("_"):
                class_methods.append(name)

        self["public_class_methods"] = class_methods
        return class_methods

    def getPublicClassSyncMethods(self) -> list[str]:
        """
        Return all public synchronous class method names of the instance.

        Returns
        -------
        list of str
            List of public synchronous class method names.
        """
        # Return cached public synchronous class methods if available
        if "public_class_sync_methods" in self:
            return self["public_class_sync_methods"]

        class_name = self.getClassName()
        cls = self._instance.__class__
        public_class_sync_methods: list[str] = []

        # Iterate over all attributes of the class to find public sync class methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, classmethod):
                func = attr.__func__
                # Public class methods do not start with an underscore and are sync
                if not inspect.iscoroutinefunction(func) and not name.startswith("_"):
                    public_class_sync_methods.append(
                        str(name).replace(f"_{class_name}", ""),
                    )

        self["public_class_sync_methods"] = public_class_sync_methods
        return public_class_sync_methods

    def getPublicClassAsyncMethods(self) -> list[str]:
        """
        Return all public asynchronous class method names of the instance.

        Returns
        -------
        list of str
            List of public asynchronous class method names.
        """
        # Return cached public async class methods if available
        if "public_class_async_methods" in self:
            return self["public_class_async_methods"]

        class_name = self.getClassName()
        cls = self._instance.__class__
        public_class_async_methods: list[str] = []

        # Iterate over all attributes of the class to find public async class methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, classmethod):
                func = attr.__func__
                # Public class methods do not start with an underscore and are async
                if inspect.iscoroutinefunction(func) and not name.startswith("_"):
                    public_class_async_methods.append(
                        str(name).replace(f"_{class_name}", ""),
                    )

        self["public_class_async_methods"] = public_class_async_methods
        return public_class_async_methods

    def getProtectedClassMethods(self) -> list[str]:
        """
        Return all protected class method names of the instance.

        Returns
        -------
        list of str
            List of protected class method names.
        """
        # Return cached protected class methods if available
        if "protected_class_methods" in self:
            return self["protected_class_methods"]

        cls = self._instance.__class__
        class_methods: list[str] = []

        # Iterate over all attributes of the class to find protected class methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            # Protected class methods start with a single underscore, not double,
            # and not with the class name (private)
            if (
                isinstance(attr, classmethod)
                and name.startswith("_")
                and not name.startswith("__")
                and not name.startswith(f"_{self.getClassName()}")
            ):
                class_methods.append(name)

        self["protected_class_methods"] = class_methods
        return class_methods

    def getProtectedClassSyncMethods(self) -> list[str]:
        """
        Return all protected synchronous class method names of the instance.

        Parameters
        ----------
        self : ReflectionInstance
            The ReflectionInstance object.

        Returns
        -------
        list of str
            List of protected synchronous class method names.
        """
        # Return cached protected synchronous class methods if available
        if "protected_class_sync_methods" in self:
            return self["protected_class_sync_methods"]

        class_name = self.getClassName()
        cls = self._instance.__class__
        protected_class_sync_methods: list[str] = []

        # Iterate over all attributes of the class to find protected sync class methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, classmethod):
                func = attr.__func__
                # Protected class methods start with a single underscore, not private,
                # and are synchronous (not coroutine functions)
                if (
                    not inspect.iscoroutinefunction(func)
                    and name.startswith("_")
                    and not name.startswith(f"_{class_name}")
                ):
                    protected_class_sync_methods.append(
                        str(name).replace(f"_{class_name}", ""),
                    )

        self["protected_class_sync_methods"] = protected_class_sync_methods
        return protected_class_sync_methods

    def getProtectedClassAsyncMethods(self) -> list[str]:
        """
        Retrieve all protected asynchronous class method names of the instance.

        Returns
        -------
        list of str
            List of protected asynchronous class method names.
        """
        # Return cached protected async class methods if available
        if "protected_class_async_methods" in self:
            return self["protected_class_async_methods"]

        class_name = self.getClassName()
        cls = self._instance.__class__
        protected_class_async_methods: list[str] = []

        # Iterate over all attributes of the class to find protected async class methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, classmethod):
                func = attr.__func__
                # Protected class methods start with a single underscore, not private
                if (
                    inspect.iscoroutinefunction(func)
                    and name.startswith("_")
                    and not name.startswith(f"_{class_name}")
                ):
                    protected_class_async_methods.append(
                        str(name).replace(f"_{class_name}", ""),
                    )

        self["protected_class_async_methods"] = protected_class_async_methods
        return protected_class_async_methods

    def getPrivateClassMethods(self) -> list[str]:
        """
        Return all private class method names of the instance.

        Returns
        -------
        list of str
            List of private class method names (unmangled).
        """
        # Return cached private class methods if available
        if "private_class_methods" in self:
            return self["private_class_methods"]

        class_name = self.getClassName()
        cls = self._instance.__class__
        private_class_methods: list[str] = []

        # Iterate over all attributes of the class to find private class methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            # Private class methods start with the class name
            if isinstance(attr, classmethod) and name.startswith(f"_{class_name}"):
                private_class_methods.append(
                    str(name).replace(f"_{class_name}", ""),
                )

        self["private_class_methods"] = private_class_methods
        return private_class_methods

    def getPrivateClassSyncMethods(self) -> list[str]:
        """
        Retrieve all private synchronous class method names of the instance.

        Returns
        -------
        list of str
            List of private synchronous class method names.
        """
        # Return cached private synchronous class methods if available
        if "private_class_sync_methods" in self:
            return self["private_class_sync_methods"]

        class_name = self.getClassName()
        cls = self._instance.__class__
        private_class_sync_methods: list[str] = []

        # Iterate over all attributes of the class to find private sync class methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, classmethod):
                func = attr.__func__
                # Private class methods start with the class name and are sync
                if (
                    not inspect.iscoroutinefunction(func)
                    and name.startswith(f"_{class_name}")
                ):
                    private_class_sync_methods.append(
                        str(name).replace(f"_{class_name}", ""),
                    )

        self["private_class_sync_methods"] = private_class_sync_methods
        return private_class_sync_methods

    def getPrivateClassAsyncMethods(self) -> list[str]:
        """
        Retrieve all private asynchronous class method names of the instance.

        Parameters
        ----------
        self : ReflectionInstance
            The ReflectionInstance object.

        Returns
        -------
        list of str
            List of private asynchronous class method names.
        """
        # Return cached private asynchronous class methods if available
        if "private_class_async_methods" in self:
            return self["private_class_async_methods"]

        class_name = self.getClassName()
        cls = self._instance.__class__
        private_class_async_methods: list[str] = []

        # Iterate over all attributes of the class to find private async class methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, classmethod):
                func = attr.__func__
                # Private class methods start with the class name and are async
                if (
                    inspect.iscoroutinefunction(func)
                    and name.startswith(f"_{class_name}")
                ):
                    private_class_async_methods.append(
                        str(name).replace(f"_{class_name}", ""),
                    )

        self["private_class_async_methods"] = private_class_async_methods
        return private_class_async_methods

    def getPublicStaticMethods(self) -> list[str]:
        """
        Return the names of all public static methods of the instance's class.

        Returns
        -------
        list of str
            List of public static method names defined on the class.
        """
        # Return cached public static methods if available
        if "public_static_methods" in self:
            return self["public_static_methods"]

        cls = self._instance.__class__
        static_methods: list[str] = []
        # Iterate over all attributes to find public static methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, staticmethod) and not name.startswith("_"):
                static_methods.append(name)
        self["public_static_methods"] = static_methods
        return static_methods

    def getPublicStaticSyncMethods(self) -> list[str]:
        """
        Return all public synchronous static method names of the instance.

        Returns
        -------
        list of str
            List of public synchronous static method names defined on the class.
        """
        # Return cached public static sync methods if available
        if "public_static_sync_methods" in self:
            return self["public_static_sync_methods"]

        class_name = self.getClassName()
        cls = self._instance.__class__
        public_static_sync_methods: list[str] = []

        # Iterate over all attributes of the class to find public sync static methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, staticmethod):
                func = attr.__func__
                # Public static methods do not start with an underscore
                if not inspect.iscoroutinefunction(func) and not name.startswith("_"):
                    public_static_sync_methods.append(
                        str(name).replace(f"_{class_name}", ""),
                    )

        self["public_static_sync_methods"] = public_static_sync_methods
        return public_static_sync_methods

    def getPublicStaticAsyncMethods(self) -> list[str]:
        """
        Retrieve all public asynchronous static method names of the instance.

        Returns
        -------
        list of str
            List of public asynchronous static method names defined on the class.
        """
        # Return cached public static async methods if available
        if "public_static_async_methods" in self:
            return self["public_static_async_methods"]

        class_name = self.getClassName()
        cls = self._instance.__class__
        public_static_async_methods: list[str] = []

        # Iterate over all attributes of the class to find public async static methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, staticmethod):
                func = attr.__func__
                # Public static methods do not start with an underscore
                if inspect.iscoroutinefunction(func) and not name.startswith("_"):
                    public_static_async_methods.append(
                        str(name).replace(f"_{class_name}", ""),
                    )

        self["public_static_async_methods"] = public_static_async_methods
        return public_static_async_methods

    def getProtectedStaticMethods(self) -> list[str]:
        """
        Return all protected static method names of the instance.

        Returns
        -------
        list of str
            List of protected static method names defined on the class.
        """
        # Return cached protected static methods if available
        if "protected_static_methods" in self:
            return self["protected_static_methods"]

        cls = self._instance.__class__
        protected_static_methods: list[str] = []

        # Iterate over all attributes of the class to find protected static methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            # Protected static methods start with a single underscore, not double,
            # and not with the class name (private)
            if (
                isinstance(attr, staticmethod)
                and name.startswith("_")
                and not name.startswith("__")
                and not name.startswith(f"_{self.getClassName()}")
            ):
                protected_static_methods.append(name)

        self["protected_static_methods"] = protected_static_methods
        return protected_static_methods

    def getProtectedStaticSyncMethods(self) -> list[str]:
        """
        Retrieve all protected synchronous static method names.

        Returns
        -------
        list of str
            List of protected synchronous static method names defined on the class.
        """
        # Return cached protected static sync methods if available
        if "protected_static_sync_methods" in self:
            return self["protected_static_sync_methods"]

        class_name = self.getClassName()
        cls = self._instance.__class__
        protected_static_sync_methods: list[str] = []

        # Iterate over all attributes of the class to find protected sync static methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, staticmethod):
                func = attr.__func__
                # Protected static methods start with a single underscore, not private
                if (
                    not inspect.iscoroutinefunction(func)
                    and name.startswith("_")
                    and not name.startswith(f"_{class_name}")
                ):
                    protected_static_sync_methods.append(
                        str(name).replace(f"_{class_name}", ""),
                    )

        self["protected_static_sync_methods"] = protected_static_sync_methods
        return protected_static_sync_methods

    def getProtectedStaticAsyncMethods(self) -> list[str]:
        """
        Retrieve all protected asynchronous static method names.

        Parameters
        ----------
        None

        Returns
        -------
        list of str
            List of protected asynchronous static method names defined on the class.
        """
        # Return cached protected static async methods if available
        if "protected_static_async_methods" in self:
            return self["protected_static_async_methods"]

        class_name = self.getClassName()
        cls = self._instance.__class__
        protected_static_async_methods: list[str] = []

        # Iterate over all attributes of the class to find
        # protected async static methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, staticmethod):
                func = attr.__func__
                # Protected static methods start with a single underscore, not private
                if (
                    inspect.iscoroutinefunction(func)
                    and name.startswith("_")
                    and not name.startswith(f"_{class_name}")
                ):
                    protected_static_async_methods.append(
                        str(name).replace(f"_{class_name}", ""),
                    )

        self["protected_static_async_methods"] = protected_static_async_methods
        return protected_static_async_methods

    def getPrivateStaticMethods(self) -> list[str]:
        """
        Return all private static method names of the instance.

        Returns
        -------
        list of str
            List of private static method names defined on the class.
        """
        # Return cached private static methods if available
        if "private_static_methods" in self:
            return self["private_static_methods"]

        class_name = self.getClassName()
        cls = self._instance.__class__
        private_static_methods: list[str] = []

        # Iterate over all attributes of the class to find private static methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, staticmethod) and name.startswith(f"_{class_name}"):
                # Unmangle the method name before appending
                private_static_methods.append(
                    str(name).replace(f"_{class_name}", ""),
                )

        self["private_static_methods"] = private_static_methods
        return private_static_methods

    def getPrivateStaticSyncMethods(self) -> list[str]:
        """
        Retrieve all private synchronous static method names of the instance.

        Returns
        -------
        list of str
            List of private synchronous static method names defined on the class.
        """
        # Return cached private static sync methods if available
        if "private_static_sync_methods" in self:
            return self["private_static_sync_methods"]

        class_name = self.getClassName()
        cls = self._instance.__class__
        private_static_sync_methods: list[str] = []

        # Iterate over all attributes of the class to find private sync static methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, staticmethod):
                func = attr.__func__
                if (
                    not inspect.iscoroutinefunction(func)
                    and name.startswith(f"_{class_name}")
                ):
                    # Unmangle the method name before appending
                    private_static_sync_methods.append(
                        str(name).replace(f"_{class_name}", ""),
                    )

        self["private_static_sync_methods"] = private_static_sync_methods
        return private_static_sync_methods

    def getPrivateStaticAsyncMethods(self) -> list[str]:
        """
        Retrieve all private asynchronous static method names of the instance.

        Returns
        -------
        list of str
            List of private asynchronous static method names defined on the class.
        """
        # Return cached private static async methods if available
        if "private_static_async_methods" in self:
            return self["private_static_async_methods"]

        class_name = self.getClassName()
        cls = self._instance.__class__
        private_static_async_methods: list[str] = []

        # Iterate over all attributes of the class to find private async static methods
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, staticmethod):
                func = attr.__func__
                if (
                    inspect.iscoroutinefunction(func)
                    and name.startswith(f"_{class_name}")
                ):
                    # Unmangle the method name before appending
                    private_static_async_methods.append(
                        str(name).replace(f"_{class_name}", ""),
                    )

        self["private_static_async_methods"] = private_static_async_methods
        return private_static_async_methods

    def getDunderMethods(self) -> list[str]:
        """
        Return all dunder (double underscore) method names of the instance.

        Returns
        -------
        list of str
            List of dunder method names defined on the instance.
        """
        # Return cached dunder methods if available
        if "dunder_methods" in self:
            return self["dunder_methods"]

        dunder_methods: list[str] = []
        exclude: list[str] = []

        # Collect dunder methods (names starting and ending with double underscores)
        for name in dir(self._instance):
            if name in exclude:
                continue
            if name.startswith("__") and name.endswith("__"):
                dunder_methods.append(name)

        self["dunder_methods"] = dunder_methods
        return dunder_methods

    def getMagicMethods(self) -> list[str]:
        """
        Return all magic method names of the instance.

        Returns
        -------
        list of str
            List of magic (dunder) method names defined on the instance.
        """
        # Magic methods are equivalent to dunder methods in Python
        return self.getDunderMethods()

    def getProperties(self) -> list[str]:
        """
        Return all property names of the instance.

        Returns
        -------
        list of str
            List of property names defined as properties on the class.
        """
        # Return cached properties if available
        if "properties" in self:
            return self["properties"]

        properties: list[str] = []
        class_name = self.getClassName()
        # Iterate over class dictionary to find all properties
        for name, prop in self._instance.__class__.__dict__.items():
            if isinstance(prop, property):
                # Unmangle private property names
                name_prop = name.replace(f"_{class_name}", "")
                properties.append(name_prop)
        self["properties"] = properties
        return properties

    def getPublicProperties(self) -> list:
        """
        Return all public properties of the instance.

        Returns
        -------
        list
            List of public property names.
        """
        # Return cached public properties if available
        if "public_properties" in self:
            return self["public_properties"]

        properties: list = []
        class_name = self.getClassName()
        # Iterate over class dictionary to find public properties
        for name, prop in self._instance.__class__.__dict__.items():
            # Public properties do not start with an underscore or class name
            if (
                isinstance(prop, property)
                and not name.startswith("_")
                and not name.startswith(f"_{class_name}")
            ):
                properties.append(name.replace(f"_{class_name}", ""))
        self["public_properties"] = properties
        return properties

    def getProtectedProperties(self) -> list:
        """
        Retrieve all protected properties of the instance.

        Returns
        -------
        list
            List of protected property names (unmangled).
        """
        # Return cached protected properties if available
        if "protected_properties" in self:
            return self["protected_properties"]

        properties: list = []
        class_name = self.getClassName()
        # Iterate over class dictionary to find protected properties
        for name, prop in self._instance.__class__.__dict__.items():
            if (
                isinstance(prop, property)
                and name.startswith("_")
                and not name.startswith("__")
                and not name.startswith(f"_{class_name}")
            ):
                properties.append(name)
        self["protected_properties"] = properties
        return properties

    def getPrivateProperties(self) -> list:
        """
        Retrieve all private properties of the instance.

        Returns
        -------
        list
            List of private property names (unmangled).
        """
        # Return cached private properties if available
        if "private_properties" in self:
            return self["private_properties"]

        properties: list = []
        class_name = self.getClassName()
        # Iterate over class dictionary to find private properties
        for name, prop in self._instance.__class__.__dict__.items():
            if (
                isinstance(prop, property) and
                name.startswith(f"_{class_name}") and
                not name.startswith("__")
            ):
                    # Unmangle the property name
                    properties.append(name.replace(f"_{class_name}", ""))
        self["private_properties"] = properties
        return properties

    def getProperty(self, name: str) -> Any:
        """
        Retrieve the value of a property from the instance.

        Parameters
        ----------
        name : str
            Name of the property to retrieve.

        Returns
        -------
        Any
            Value of the specified property.

        Raises
        ------
        AttributeError
            If the property does not exist or is not accessible.
        """
        # Check if the property name is valid and present in the class properties
        if name in self.getProperties():
            # Handle private property name mangling for correct lookup
            if name.startswith("__") and not name.endswith("__"):
                class_name = self.getClassName()
                name = f"_{class_name}{name}"
            # Retrieve and return the property value from the instance
            return getattr(self._instance, name, None)
        # Raise error if the property does not exist
        error_msg = (
            f"Property '{name}' does not exist on '{self.getClassName()}'."
        )
        raise AttributeError(error_msg)

    def getPropertySignature(self, name: str) -> inspect.Signature:
        """
        Return the signature of a property getter.

        Parameters
        ----------
        name : str
            Name of the property.

        Returns
        -------
        inspect.Signature
            Signature of the property's getter method.

        Raises
        ------
        AttributeError
            If the property does not exist on the class.
        """
        # Return cached property signature if available
        if f"property_signature_{name}" in self:
            return self[f"property_signature_{name}"]

        # Handle private property name mangling for correct lookup
        original_name = name
        if name.startswith("__") and not name.endswith("__"):
            class_name = self.getClassName()
            name = f"_{class_name}{name}"

        # Retrieve the property from the class and check its type
        prop = getattr(self._instance.__class__, name, None)
        if isinstance(prop, property):
            self[f"property_signature_{name}"] = inspect.signature(prop.fget)
            return self[f"property_signature_{name}"]

        # Raise error if property does not exist
        error_msg = (
            f"Property '{original_name}' does not exist on '{self.getClassName()}'."
        )
        raise AttributeError(error_msg)

    def getPropertyDocstring(self, name: str) -> str:
        """
        Retrieve the docstring for a property.

        Parameters
        ----------
        name : str
            Name of the property.

        Returns
        -------
        str
            The docstring of the property, or an empty string if not present.

        Raises
        ------
        AttributeError
            If the property does not exist on the class.
        """
        # Return cached docstring if available
        if f"property_docstring_{name}" in self:
            return self[f"property_docstring_{name}"]

        # Handle private property name mangling for correct lookup
        original_name = name
        if name.startswith("__") and not name.endswith("__"):
            class_name = self.getClassName()
            name = f"_{class_name}{name}"

        # Retrieve the property from the class
        prop = getattr(self._instance.__class__, name, None)
        if isinstance(prop, property):
            # Cache and return the docstring of the property's getter or an empty string
            self[f"property_docstring_{name}"] = prop.fget.__doc__ or ""
            return self[f"property_docstring_{name}"]

        # Raise error if property does not exist
        error_msg = (
            f"Property '{original_name}' does not exist on '{self.getClassName()}'."
        )
        raise AttributeError(error_msg)

    def constructorSignature(self) -> SignatureArguments:
        """
        Analyze and return constructor dependencies of the instance's class.

        Returns
        -------
        SignatureArguments
            Structured representation of the constructor dependencies. Contains:
            - resolved : dict
                Dictionary of resolved dependencies with names and values.
            - unresolved : list
                List of unresolved dependencies (parameter names without default
                values or annotations).
        """
        # Return cached constructor signature if available
        if "constructor_signature" in self:
            return self["constructor_signature"]

        # Analyze the constructor signature for dependencies
        self["constructor_signature"] = ReflectDependencies(
            self._instance.__class__,
        ).constructorSignature()
        return self["constructor_signature"]

    def methodSignature(self, method_name: str) -> SignatureArguments:
        """
        Analyze and return dependencies for a method of the instance's class.

        Parameters
        ----------
        method_name : str
            Name of the method to inspect.

        Returns
        -------
        SignatureArguments
            Structured representation of the method dependencies, including:
            - resolved: dict of resolved dependencies with names and values.
            - unresolved: list of unresolved dependencies (parameter names
              without default values or annotations).

        Raises
        ------
        AttributeError
            If the method does not exist on the class.
        """
        # Return cached signature if available
        if f"method_signature_{method_name}" in self:
            return self[f"method_signature_{method_name}"]

        # Check if the method exists on the instance
        if not self.hasMethod(method_name):
            error_msg = (
                f"Method '{method_name}' does not exist on '{self.getClassName()}'."
            )
            raise AttributeError(error_msg)

        # Handle private method name mangling for correct lookup
        if method_name.startswith("__") and not method_name.endswith("__"):
            class_name = self.getClassName()
            method_name = f"_{class_name}{method_name}"

        # Use ReflectDependencies to get method dependencies
        self[f"method_signature_{method_name}"] = (
            ReflectDependencies(self._instance).methodSignature(method_name)
        )
        return self[f"method_signature_{method_name}"]

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
