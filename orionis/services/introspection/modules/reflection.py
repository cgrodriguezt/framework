from __future__ import annotations
import importlib
import inspect
import keyword
from pathlib import Path
from orionis.services.introspection.modules.contracts.reflection import (
    IReflectionModule,
)

class ReflectionModule(IReflectionModule):

    # ruff: noqa: PERF403

    def __init__(self, module: str) -> None:
        """
        Initialize the ReflectionModule by importing the specified module.

        Parameters
        ----------
        module : str
            Name of the module to import and reflect upon.

        Raises
        ------
        TypeError
            If `module` is not a non-empty string or cannot be imported.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Validate module name and import the module
        if not isinstance(module, str) or not module.strip():
            error_msg = f"Module name must be a non-empty string, got {module!r}"
            raise TypeError(error_msg)
        try:
            self.__module = importlib.import_module(module)
        except Exception as e:
            error_msg = f"Failed to import module '{module}': {e}"
            raise TypeError(error_msg) from e
        # Initialize memory cache for storing values
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

    def getModule(self) -> object:
        """
        Return the imported module object.

        Returns
        -------
        object
            The imported module object.
        """
        return self.__module

    def hasClass(self, class_name: str) -> bool:
        """
        Check if a class with the specified name exists in the module.

        Parameters
        ----------
        class_name : str
            Name of the class to check.

        Returns
        -------
        bool
            True if the class exists in the module, otherwise False.
        """
        # Check for class existence in the module's class dictionary
        return class_name in self.getClasses()

    def getClass(self, class_name: str) -> type | None:
        """
        Retrieve a class object by its name from the module.

        Parameters
        ----------
        class_name : str
            Name of the class to retrieve.

        Returns
        -------
        type or None
            The class object if found, otherwise None.
        """
        # Get all classes from the module and return the one matching class_name
        classes = self.getClasses()
        if class_name in classes:
            return classes[class_name]
        return None

    def setClass(self, class_name: str, cls: type) -> bool:
        """
        Set a class in the module.

        Parameters
        ----------
        class_name : str
            Name of the class to set.
        cls : type
            Class object to set.

        Raises
        ------
        ValueError
            If `cls` is not a class type, if `class_name` is not a valid identifier,
            or if `class_name` is a reserved keyword.

        Returns
        -------
        bool
            True if the class was set successfully.
        """
        # Validate that cls is a class type
        if not isinstance(cls, type):
            error_msg = f"Expected a class type, got {type(cls)}"
            raise TypeError(error_msg)
        # Validate that class_name is a valid identifier
        if not class_name.isidentifier():
            error_msg = f"Invalid class name '{class_name}'. Must be a valid identifier"
            raise ValueError(error_msg)
        # Validate that class_name is not a reserved keyword
        if keyword.iskeyword(class_name):
            error_msg = f"Class name '{class_name}' is a reserved keyword."
            raise ValueError(error_msg)
        # Set the class in the module and invalidate the classes cache
        setattr(self.__module, class_name, cls)
        del self["classes"]
        return True

    def removeClass(self, class_name: str) -> bool:
        """
        Remove a class from the module.

        Parameters
        ----------
        class_name : str
            Name of the class to remove.

        Raises
        ------
        ValueError
            If `class_name` is not a valid identifier or if the class does not exist.

        Returns
        -------
        bool
            True if the class was removed successfully.
        """
        # Check if the class exists in the module
        if class_name not in self.getClasses():
            error_msg = (
                f"Class '{class_name}' does not exist "
                f"in module '{self.__module.__name__}'"
            )
            raise ValueError(error_msg)
        # Remove the class attribute from the module and invalidate cache
        delattr(self.__module, class_name)
        del self["classes"]
        return True

    def getClasses(self) -> dict:
        """
        Return a dictionary of classes defined in the module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary with class names as keys and class objects as values.
        """
        # Use cache if available to avoid recomputation
        if "classes" in self:
            return self["classes"]

        classes = {}
        # Iterate through module attributes to find classes
        for k, v in self.__module.__dict__.items():
            if isinstance(v, type) and issubclass(v, object):
                classes[k] = v

        # Cache the result for future calls
        self["classes"] = classes
        return classes

    def getPublicClasses(self) -> dict:
        """
        Return a dictionary of public classes defined in the module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary with class names as keys and class objects as values.
        """
        # Use cache if available to avoid recomputation
        if "public_classes" in self:
            return self["public_classes"]

        public_classes = {}
        # Collect classes whose names do not start with an underscore
        for k, v in self.getClasses().items():
            if not str(k).startswith("_"):
                public_classes[k] = v
        self["public_classes"] = public_classes
        return public_classes

    def getProtectedClasses(self) -> dict:
        """
        Return a dictionary of protected classes defined in the module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary with class names as keys and class objects as values.
        """
        # Use cache if available to avoid recomputation
        if "protected_classes" in self:
            return self["protected_classes"]

        protected_classes = {}
        # Collect classes whose names start with a single underscore
        for k, v in self.getClasses().items():
            if str(k).startswith("_") and not str(k).startswith("__"):
                protected_classes[k] = v

        self["protected_classes"] = protected_classes
        return protected_classes

    def getPrivateClasses(self) -> dict:
        """
        Return a dictionary of private classes defined in the module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary with class names as keys and class objects as values.
        """
        # Use cache if available to avoid recomputation
        if "private_classes" in self:
            return self["private_classes"]

        private_classes: dict = {}
        # Collect classes whose names start with double underscores and
        # do not end with them
        for k, v in self.getClasses().items():
            if str(k).startswith("__") and not str(k).endswith("__"):
                private_classes[k] = v

        self["private_classes"] = private_classes
        return private_classes

    def getConstant(self, constant_name: str) -> object | None:
        """
        Retrieve a constant value by name from the module.

        Parameters
        ----------
        constant_name : str
            Name of the constant to retrieve.

        Returns
        -------
        object or None
            Value of the constant if found, otherwise None.
        """
        # Get all constants and return the value for the given name if present
        constants = self.getConstants()
        if constant_name in constants:
            return constants[constant_name]
        return None

    def getConstants(self) -> dict:
        """
        Retrieve constants defined in the module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary with constant names as keys and their values as values.
        """
        # Use cache if available to avoid recomputation
        if "constants" in self:
            return self["constants"]

        constants: dict = {}
        # Collect uppercase, non-callable, non-keyword attributes as constants
        for k, v in self.__module.__dict__.items():
            if not callable(v) and k.isupper() and not keyword.iskeyword(k):
                constants[k] = v

        self["constants"] = constants
        return constants

    def getPublicConstants(self) -> dict:
        """
        Retrieve public constants defined in the module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary with constant names as keys and their values as values.
        """
        # Use cache if available to avoid recomputation
        if "public_constants" in self:
            return self["public_constants"]

        public_constants: dict = {}
        # Collect constants whose names do not start with an underscore
        for k, v in self.getConstants().items():
            if not str(k).startswith("_"):
                public_constants[k] = v

        self["public_constants"] = public_constants
        return public_constants

    def getProtectedConstants(self) -> dict:
        """
        Return protected constants defined in the module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary with constant names as keys and their values as values.
        """
        # Use cache if available to avoid recomputation
        if "protected_constants" in self:
            return self["protected_constants"]

        protected_constants: dict = {}
        # Collect constants whose names start with a single underscore
        for k, v in self.getConstants().items():
            if str(k).startswith("_") and not str(k).startswith("__"):
                protected_constants[k] = v

        self["protected_constants"] = protected_constants
        return protected_constants

    def getPrivateConstants(self) -> dict:
        """
        Retrieve private constants defined in the module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary with constant names as keys and their values as values.
        """
        # Use cache if available to avoid recomputation
        if "private_constants" in self:
            return self["private_constants"]

        private_constants: dict = {}
        # Collect constants whose names start with double underscores
        # and do not end with them
        for k, v in self.getConstants().items():
            if str(k).startswith("__") and not str(k).endswith("__"):
                private_constants[k] = v

        self["private_constants"] = private_constants
        return private_constants

    def getFunctions(self) -> dict:
        """
        Return a dictionary of functions defined in the module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary with function names as keys and function objects as values.
        """
        # Use cache if available to avoid recomputation
        if "functions" in self:
            return self["functions"]

        functions: dict = {}
        # Collect callable objects with a __code__ attribute as functions
        for k, v in self.__module.__dict__.items():
            if callable(v) and hasattr(v, "__code__"):
                functions[k] = v

        self["functions"] = functions
        return functions

    def getPublicFunctions(self) -> dict:
        """
        Return a dictionary of public functions defined in the module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary mapping function names to function objects.
        """
        # Use cache if available to avoid recomputation
        if "public_functions" in self:
            return self["public_functions"]

        public_functions: dict = {}
        # Collect functions whose names do not start with an underscore
        for k, v in self.getFunctions().items():
            if not str(k).startswith("_"):
                public_functions[k] = v

        self["public_functions"] = public_functions
        return public_functions

    def getPublicSyncFunctions(self) -> dict:
        """
        Return a dictionary of public synchronous functions in the module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary mapping function names to function objects.
        """
        # Use cache if available to avoid recomputation
        if "public_sync_functions" in self:
            return self["public_sync_functions"]

        sync_functions: dict = {}
        # Collect public functions that are synchronous (not async)
        for k, v in self.getPublicFunctions().items():
            if not inspect.iscoroutinefunction(v):
                sync_functions[k] = v
        self["public_sync_functions"] = sync_functions
        return sync_functions

    def getPublicAsyncFunctions(self) -> dict:
        """
        Return a dictionary of public asynchronous functions in the module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary mapping function names to function objects.
        """
        # Use cache if available to avoid recomputation
        if "public_async_functions" in self:
            return self["public_async_functions"]

        async_functions: dict = {}
        # Collect public functions that are asynchronous
        for k, v in self.getPublicFunctions().items():
            if inspect.iscoroutinefunction(v):
                async_functions[k] = v
        self["public_async_functions"] = async_functions
        return async_functions

    def getProtectedFunctions(self) -> dict:
        """
        Return a dictionary of protected functions defined in the module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary mapping protected function names to function objects.
        """
        # Use cache if available to avoid recomputation
        if "protected_functions" in self:
            return self["protected_functions"]

        protected_functions: dict = {}
        # Collect functions whose names start with a single underscore
        # and do not start with double underscores
        for k, v in self.getFunctions().items():
            if str(k).startswith("_") and not str(k).startswith("__"):
                protected_functions[k] = v

        self["protected_functions"] = protected_functions
        return protected_functions

    def getProtectedSyncFunctions(self) -> dict:
        """
        Return protected synchronous functions defined in the module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary mapping function names to function objects.
        """
        # Use cache if available to avoid recomputation
        if "protected_sync_functions" in self:
            return self["protected_sync_functions"]

        sync_functions: dict = {}
        # Collect protected functions that are synchronous
        for k, v in self.getProtectedFunctions().items():
            if not inspect.iscoroutinefunction(v):
                sync_functions[k] = v
        self["protected_sync_functions"] = sync_functions
        return sync_functions

    def getProtectedAsyncFunctions(self) -> dict:
        """
        Return protected asynchronous functions defined in the module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary mapping function names to function objects.
        """
        # Use cache if available to avoid recomputation
        if "protected_async_functions" in self:
            return self["protected_async_functions"]

        async_functions: dict = {}
        # Collect protected functions that are asynchronous
        for k, v in self.getProtectedFunctions().items():
            if inspect.iscoroutinefunction(v):
                async_functions[k] = v
        self["protected_async_functions"] = async_functions
        return async_functions

    def getPrivateFunctions(self) -> dict:
        """
        Return private functions defined in the module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary mapping function names to function objects.
        """
        # Use cache if available to avoid recomputation
        if "private_functions" in self:
            return self["private_functions"]

        private_functions: dict = {}
        # Collect functions whose names start with double underscores
        # and do not end with them
        for k, v in self.getFunctions().items():
            if str(k).startswith("__") and not str(k).endswith("__"):
                private_functions[k] = v

        self["private_functions"] = private_functions
        return private_functions

    def getPrivateSyncFunctions(self) -> dict:
        """
        Return private synchronous functions defined in the module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary with function names as keys and function objects as values.
        """
        # Use cache if available to avoid recomputation
        if "private_sync_functions" in self:
            return self["private_sync_functions"]

        sync_functions: dict = {}
        # Collect private functions that are synchronous
        for k, v in self.getPrivateFunctions().items():
            if not inspect.iscoroutinefunction(v):
                sync_functions[k] = v
        self["private_sync_functions"] = sync_functions
        return sync_functions

    def getPrivateAsyncFunctions(self) -> dict:
        """
        Return private asynchronous functions defined in the module.

        Returns
        -------
        dict
            Dictionary with function names as keys and function objects as values.
        """
        # Use cache if available to avoid recomputation
        if "private_async_functions" in self:
            return self["private_async_functions"]

        async_functions: dict = {}
        # Collect private functions that are asynchronous
        for k, v in self.getPrivateFunctions().items():
            if inspect.iscoroutinefunction(v):
                async_functions[k] = v
        self["private_async_functions"] = async_functions
        return async_functions

    def getImports(self) -> dict:
        """
        Retrieve imported modules from the module.

        Returns
        -------
        dict
            Dictionary mapping import names to module objects.
        """
        # Use cache if available to avoid recomputation
        if "imports" in self:
            return self["imports"]

        imports: dict = {}
        # Collect module-type attributes as imports
        for k, v in self.__module.__dict__.items():
            if isinstance(v, type(importlib)):
                imports[k] = v

        self["imports"] = imports
        return imports

    def getFile(self) -> str:
        """
        Return the file path of the module.

        Returns
        -------
        str
            The absolute file path of the module.
        """
        # Use inspect to retrieve the module's file path
        return inspect.getfile(self.__module)

    def getSourceCode(self) -> str:
        """
        Retrieve the source code of the module.

        Returns
        -------
        str
            The source code of the module as a string.

        Raises
        ------
        ValueError
            If the source code cannot be read from the module file.
        """
        # Return cached source code if available
        if "source_code" in self:
            return self["source_code"]

        try:
            # Read the module's source code from its file
            with Path.open(self.getFile(), encoding="utf-8") as file:
                self["source_code"] = file.read()
            return self["source_code"]
        except Exception as e:
            error_msg = (
                f"Failed to read source code for module '{self.__module.__name__}': {e}"
            )
            raise ValueError(error_msg) from e

    def clearCache(self) -> None:
        """
        Clear all cached reflection data.

        Removes all cached entries stored in the reflection instance. Forces
        fresh computation on subsequent method calls.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return a value.
        """
        # Clear the internal memory cache for reflection results
        self.__memory_cache.clear()
