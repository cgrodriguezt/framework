import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, Type
from orionis.services.asynchrony.coroutines import Coroutine
from orionis.services.introspection.dependencies.entities.class_dependencies import ClassDependency
from orionis.services.introspection.dependencies.entities.method_dependencies import MethodDependency
from orionis.services.introspection.dependencies.reflect_dependencies import ReflectDependencies
from orionis.services.introspection.exceptions.reflection_attribute_error import ReflectionAttributeError
from orionis.services.introspection.exceptions.reflection_type_error import ReflectionTypeError
from orionis.services.introspection.exceptions.reflection_value_error import ReflectionValueError
from orionis.services.introspection.instances.entities.class_attributes import ClassAttributes
from orionis.services.introspection.instances.entities.class_method import ClassMethod
from orionis.services.introspection.instances.entities.class_property import ClassProperty

class ReflectionInstance:

    def __init__(self, instance: Any) -> None:
        """
        Initialize the ReflectionInstance with a given object instance.

        Parameters
        ----------
        instance : Any
            The object instance to be reflected upon.

        Raises
        ------
        ReflectionTypeError
            If the provided instance is not a valid object instance.
        ReflectionValueError
            If the instance belongs to a built-in, abstract base class, or '__main__' module.
        """
        if not (isinstance(instance, object) and not isinstance(instance, type)):
            raise ReflectionTypeError(
                f"Expected an object instance, got {type(instance).__name__!r}: {instance!r}"
            )
        module = type(instance).__module__
        if module in {'builtins', 'abc'}:
            raise ReflectionValueError(
                f"Instance of type '{type(instance).__name__}' belongs to disallowed module '{module}'."
            )
        if module == '__main__':
            raise ReflectionValueError(
                "Instance originates from '__main__'; please provide an instance from an importable module."
            )
        self._instance = instance

    def getClass(self) -> Type:
        """
        Get the class of the instance.

        Returns
        -------
        Type
            The class object of the instance
        """
        return self._instance.__class__

    def getClassName(self) -> str:
        """
        Get the name of the instance's class.

        Returns
        -------
        str
            The name of the class
        """
        return self._instance.__class__.__name__

    def getModuleName(self) -> str:
        """
        Get the name of the module where the class is defined.

        Returns
        -------
        str
            The module name
        """
        return self._instance.__class__.__module__

    def getModuleWithClassName(self) -> str:
        """
        Get the name of the module where the class is defined.

        Returns
        -------
        str
            The module name
        """
        return f"{self._instance.__class__}.{self._instance.__class__.__module__}"

    def getAttributes(self) -> Dict[str, Any]:
        """
        Get all attributes of the instance, including public, private, protected, and dunder attributes.

        Returns
        -------
        Dict[str, Any]
            Dictionary of all attribute names and their values
        """
        return {
            **self.getPublicAttributes(),
            **self.getProtectedAttributes(),
            **self.getPrivateAttributes(),
            **self.getDunderAttributes()
        }

    def getPublicAttributes(self) -> Dict[str, Any]:
        """
        Get all public attributes of the instance.

        Returns
        -------
        Dict[str, Any]
            Dictionary of public attribute names and their values
        """
        class_name = self.getClassName()
        attributes = vars(self._instance)
        public = {}

        # Exclude dunder, protected, and private attributes
        for attr, value in attributes.items():
            if attr.startswith("__") and attr.endswith("__"):
                continue
            if attr.startswith(f"_{class_name}"):
                continue
            if attr.startswith("_"):
                continue
            public[attr] = value

        return public

    def getProtectedAttributes(self) -> Dict[str, Any]:
        """
        Get all Protected attributes of the instance.

        Returns
        -------
        Dict[str, Any]
            Dictionary of Protected attribute names and their values
        """
        class_name = self.getClassName()
        attributes = vars(self._instance)
        protected = {}

        # Select protected attributes that start with a single underscore
        for attr, value in attributes.items():
            if attr.startswith("_") and not attr.startswith("__") and not attr.startswith(f"_{class_name}"):
                protected[attr] = value

        return protected

    def getPrivateAttributes(self) -> Dict[str, Any]:
        """
        Get all private attributes of the instance.

        Returns
        -------
        Dict[str, Any]
            Dictionary of private attribute names and their values
        """
        class_name = self.getClassName()
        attributes = vars(self._instance)
        private = {}

        # Select private attributes that start with the class name
        for attr, value in attributes.items():
            if attr.startswith(f"_{class_name}"):
                private[str(attr).replace(f"_{class_name}", "")] = value

        return private

    def getDunderAttributes(self) -> Dict[str, Any]:
        """
        Get all dunder (double underscore) attributes of the instance.

        Returns
        -------
        Dict[str, Any]
            Dictionary of dunder attribute names and their values
        """
        attributes = vars(self._instance)
        dunder = {}

        # Select dunder attributes that start and end with double underscores
        for attr, value in attributes.items():
            if attr.startswith("__") and attr.endswith("__"):
                dunder[attr] = value

        return dunder

    def getPublicMethods(self) -> List[str]:
        """
        Get all public method names of the instance.

        Returns
        -------
        List[str]
            List of public method names
        """
        class_name = self.getClassName()
        cls = self._instance.__class__
        public_methods = []

        # Gather all class methods to exclude them
        class_methods = set()
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, classmethod):
                class_methods.add(name)

        # Collect public instance methods (not static, not class, not private/protected/magic)
        for name, method in inspect.getmembers(self._instance, predicate=inspect.ismethod):
            if (
                name not in class_methods and
                not (name.startswith("__") and name.endswith("__")) and
                not name.startswith(f"_{class_name}") and
                not (name.startswith("_") and not name.startswith(f"_{class_name}"))
            ):
                public_methods.append(name)

        return public_methods

    def getPublicSyncMethods(self) -> List[str]:
        """
        Get all public synchronous method names of the instance.

        Returns
        -------
        List[str]
            List of public synchronous method names
        """
        methods = self.getPublicMethods()
        return [method for method in methods if not inspect.iscoroutinefunction(getattr(self._instance, method))]

    def getPublicAsyncMethods(self) -> List[str]:
        """
        Get all public asynchronous method names of the instance.

        Returns
        -------
        List[str]
            List of public asynchronous method names
        """
        methods = self.getPublicMethods()
        return [method for method in methods if inspect.iscoroutinefunction(getattr(self._instance, method))]

    def getProtectedMethods(self) -> List[str]:
        """
        Get all protected method names of the instance.

        Returns
        -------
        List[str]
            List of protected method names
        """
        protected_methods = []

        # Collect protected instance methods (starting with a single underscore)
        for name, method in inspect.getmembers(self._instance, predicate=inspect.ismethod):
            if name.startswith("_") and not name.startswith("__") and not name.startswith(f"_{self.getClassName()}"):
                protected_methods.append(name)

        return protected_methods

    def getProtectedSyncMethods(self) -> List[str]:
        """
        Get all protected synchronous method names of the instance.

        Returns
        -------
        List[str]
            List of protected synchronous method names
        """
        methods = self.getProtectedMethods()
        return [method for method in methods if not inspect.iscoroutinefunction(getattr(self._instance, method))]

    def getProtectedAsyncMethods(self) -> List[str]:
        """
        Get all protected asynchronous method names of the instance.

        Returns
        -------
        List[str]
            List of protected asynchronous method names
        """
        methods = self.getProtectedMethods()
        return [method for method in methods if inspect.iscoroutinefunction(getattr(self._instance, method))]

    def getPrivateMethods(self) -> List[str]:
        """
        Get all private method names of the instance.

        Returns
        -------
        List[str]
            List of private method names
        """
        class_name = self.getClassName()
        private_methods = []

        # Collect private instance methods (starting with class name)
        for name, method in inspect.getmembers(self._instance, predicate=inspect.ismethod):
            if name.startswith(f"_{class_name}") and not name.startswith("__"):
                private_methods.append(name.replace(f"_{class_name}", ""))

        # Return private methods without the class name prefix
        return private_methods

    def getPrivateSyncMethods(self) -> List[str]:
        """
        Get all private synchronous method names of the instance.

        Returns
        -------
        List[str]
            List of private synchronous method names
        """
        class_name = self.getClassName()
        private_methods = []
        for name, method in inspect.getmembers(self._instance, predicate=inspect.ismethod):
            if name.startswith(f"_{class_name}") and not name.startswith("__"):
                # Remove the class name prefix for the returned name
                short_name = name.replace(f"_{class_name}", "")
                if not inspect.iscoroutinefunction(method):
                    private_methods.append(short_name)
        return private_methods

    def getPrivateAsyncMethods(self) -> List[str]:
        """
        Get all private asynchronous method names of the instance.

        Returns
        -------
        List[str]
            List of private asynchronous method names
        """
        class_name = self.getClassName()
        private_methods = []
        for name, method in inspect.getmembers(self._instance, predicate=inspect.ismethod):
            if name.startswith(f"_{class_name}") and not name.startswith("__"):
                # Remove the class name prefix for the returned name
                short_name = name.replace(f"_{class_name}", "")
                if inspect.iscoroutinefunction(method):
                    private_methods.append(short_name)
        return private_methods

    def getPublicClassMethods(self) -> List[str]:
        """
        Get all class method names of the instance.

        Returns
        -------
        List[str]
            List of class method names
        """
        cls = self._instance.__class__
        class_methods = []

        # Iterate over all attributes of the class
        for name in dir(cls):

            # Get the attribute using getattr_static to avoid triggering property getters
            attr = inspect.getattr_static(cls, name)

            # Check if the attribute is a class method
            if isinstance(attr, classmethod):

                # Check not private or protected methods
                if not name.startswith(f"_"):
                    class_methods.append(name)

        # Return the list of public class method
        return class_methods

    def getPublicClassSyncMethods(self) -> List[str]:
        """
        Get all public synchronous class method names of the instance.

        Returns
        -------
        List[str]
            List of public synchronous class method names
        """
        class_name = self.getClassName()
        cls = self._instance.__class__
        public_class_sync_methods = []

        # Iterate over all attributes of the class
        for name in dir(cls):

            # Get the attribute using getattr_static to avoid triggering property getters
            attr = inspect.getattr_static(cls, name)

            # Check if the attribute is a class method
            if isinstance(attr, classmethod):

                # Get the underlying function
                func = attr.__func__

                # Check if it's NOT a coroutine function (i.e., synchronous)
                if not inspect.iscoroutinefunction(func) and not name.startswith(f"_"):
                    public_class_sync_methods.append(str(name).replace(f"_{class_name}", ""))

        # Return the list of public synchronous class method names
        return public_class_sync_methods

    def getPublicClassAsyncMethods(self) -> List[str]:
        """
        Get all public asynchronous class method names of the instance.

        Returns
        -------
        List[str]
            List of public asynchronous class method names
        """
        class_name = self.getClassName()
        cls = self._instance.__class__
        public_class_async_methods = []

        # Iterate over all attributes of the class
        for name in dir(cls):

            # Get the attribute using getattr_static to avoid triggering property getters
            attr = inspect.getattr_static(cls, name)

            # Check if the attribute is a class method
            if isinstance(attr, classmethod):

                # Get the underlying function
                func = attr.__func__

                # Check if it's a coroutine function (i.e., asynchronous)
                if inspect.iscoroutinefunction(func) and not name.startswith(f"_"):
                    public_class_async_methods.append(str(name).replace(f"_{class_name}", ""))

        # Return the list of public asynchronous class method names
        return public_class_async_methods




























    def getProtectedClassMethods(self) -> List[str]:
        """
        Get all protected class method names of the instance.

        Returns
        -------
        List[str]
            List of protected class method names
        """
        class_name = self.getClassName()
        cls = self._instance.__class__
        protected_class_methods = []

        # Iterate over all attributes of the class
        for name in dir(cls):

            # Get the attribute using getattr_static to avoid triggering property getters
            attr = inspect.getattr_static(cls, name)

            # Check if the attribute is a class method
            if isinstance(attr, classmethod):

                # Get the underlying function
                func = attr.__func__

                # Check if it's NOT a coroutine function (i.e., synchronous)
                if not inspect.iscoroutinefunction(func) and name.startswith(f"_") and not name.startswith("__") and not name.startswith(f"_{class_name}"):
                    protected_class_methods.append(str(name).replace(f"_{class_name}", ""))

        # Return the list of protected class method names
        return protected_class_methods

    def getPrivateClassMethods(self) -> List[str]:
        """
        Get all private class method names of the instance.

        Returns
        -------
        List[str]
            List of private class method names
        """
        class_name = self.getClassName()
        cls = self._instance.__class__
        private_class_methods = []

        # Iterate over all attributes of the class
        for name in dir(cls):

            # Get the attribute using getattr_static to avoid triggering property getters
            attr = inspect.getattr_static(cls, name)

            # Check if the attribute is a class method
            if isinstance(attr, classmethod):

                # Get the underlying function
                func = attr.__func__

                # Check if it's NOT a coroutine function (i.e., synchronous)
                if not inspect.iscoroutinefunction(func) and name.startswith(f"_{class_name}"):
                    private_class_methods.append(str(name).replace(f"_{class_name}", ""))

        # Return the list of protected class method names
        return private_class_methods

















    def getClassSyncMethods(self) -> List[str]:
        """
        Get all synchronous class method names of the instance.

        Returns
        -------
        List[str]
            List of synchronous class method names
        """
        class_name = self.getClassName()
        cls = self._instance.__class__
        class_sync_methods = []

        # Iterate over all attributes of the class
        for name in dir(cls):

            # Get the attribute using getattr_static to avoid triggering property getters
            attr = inspect.getattr_static(cls, name)

            # Check if the attribute is a class method
            if isinstance(attr, classmethod):

                # Get the underlying function
                func = attr.__func__

                # Check if it's NOT a coroutine function (i.e., synchronous)
                if not inspect.iscoroutinefunction(func):
                    class_sync_methods.append(str(name).replace(f"_{class_name}", ""))

        # Return the list of synchronous class method names
        return class_sync_methods

    def getClassAsyncMethods(self) -> List[str]:
        """
        Get all asynchronous class method names of the instance.

        Returns
        -------
        List[str]
            List of asynchronous class method names
        """
        class_name = self.getClassName()
        cls = self._instance.__class__
        class_async_methods = []

        # Iterate over all attributes of the class
        for name in dir(cls):

            # Get the attribute using getattr_static to avoid triggering property getters
            attr = inspect.getattr_static(cls, name)

            # Check if the attribute is a class method
            if isinstance(attr, classmethod):

                # Get the underlying function
                func = attr.__func__

                # Check if it's a coroutine function (i.e., asynchronous)
                if inspect.iscoroutinefunction(func):
                    class_async_methods.append(str(name).replace(f"_{class_name}", ""))

        # Return the list of asynchronous class method names
        return class_async_methods
































    def getDunderMethods(self) -> List[str]:
        """
        Get all dunder (double underscore) method names of the instance.

        Returns
        -------
        List[str]
            List of dunder method names
        """
        dunder_methods = []

        # Collect dunder methods (starting and ending with double underscores)
        for name in dir(self._instance):
            if name.startswith("__") and name.endswith("__"):
                dunder_methods.append(name)

        return dunder_methods

    def getMagicMethods(self) -> List[str]:
        """
        Get all magic method names of the instance.

        Returns
        -------
        List[str]
            List of magic method names
        """
        return self.getDunderMethods()

    

    def getStaticMethods(self) -> List[str]:
        """
        Get all static method names of the instance.

        Returns
        -------
        List[str]
            List of static method names
        """
        class_name = self.getClassName()
        cls = self._instance.__class__
        static_methods = []
        for name in dir(cls):
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, staticmethod):
                static_methods.append(str(name).replace(f"_{class_name}", ""))
        return static_methods

    def getStaticSyncMethods(self) -> List[str]:
        """
        Get all synchronous static method names of the instance.

        Returns
        -------
        List[str]
            List of synchronous static method names
        """
        class_name = self.getClassName()
        cls = self._instance.__class__
        static_sync_methods = []

        # Iterate over all attributes of the class
        for name in dir(cls):

            # Get the attribute using getattr_static to avoid triggering property getters
            attr = inspect.getattr_static(cls, name)

            # Check if the attribute is a static method
            if isinstance(attr, staticmethod):

                # Get the underlying function
                func = attr.__func__

                # Check if it's NOT a coroutine function (i.e., synchronous)
                if not inspect.iscoroutinefunction(func):
                    static_sync_methods.append(str(name).replace(f"_{class_name}", ""))

        # Return the list of synchronous static method names
        return static_sync_methods

    def getStaticAsyncMethods(self) -> List[str]:
        """
        Get all asynchronous static method names of the instance.

        Returns
        -------
        List[str]
            List of asynchronous static method names
        """
        class_name = self.getClassName()
        cls = self._instance.__class__
        static_async_methods = []

        # Iterate over all attributes of the class
        for name in dir(cls):

            # Get the attribute using getattr_static to avoid triggering property getters
            attr = inspect.getattr_static(cls, name)

            # Check if the attribute is a static method
            if isinstance(attr, staticmethod):

                # Get the underlying function
                func = attr.__func__

                # Check if it's a coroutine function (i.e., asynchronous)
                if inspect.iscoroutinefunction(func):
                    static_async_methods.append(str(name).replace(f"_{class_name}", ""))

        # Return the list of asynchronous static method names
        return static_async_methods

    # def getMethodDocstring(self, method_name: str) -> Optional[str]:
    #     """
    #     Get the docstring of a method.

    #     Parameters
    #     ----------
    #     method_name : str
    #         Name of the method

    #     Returns
    #     -------
    #     Optional[str]
    #         The docstring of the method, or None if not available
    #     """
    #     # Handle private method name mangling
    #     if method_name in self.getPrivateMethods() or method_name in self.getClass
    #         method_name = f"_{self.getClassName()}{method_name}"
        
    #     print(f"Getting docstring for method: {method_name} in class: {self.getPrivateMethods()}")

    #     # Try to get the method from the instance first
    #     method = getattr(self._instance, method_name, None)
    #     if method is None:
    #         # Try to get the method from the class if not found on the instance
    #         method = getattr(self._instance.__class__, method_name, None)
    #         if method is None:
    #             return None

    #     # If it's a staticmethod or classmethod, get the underlying function
    #     if isinstance(method, (staticmethod, classmethod)):
    #         method = method.__func__

    #     # Return the docstring if available
    #     return getattr(method, "__doc__", None) or ""

    # def getMethodSignature(self, method_name: str) -> inspect.Signature:
    #     """
    #     Get the signature of a method.

    #     Parameters
    #     ----------
    #     method_name : str
    #         Name of the method

    #     Returns
    #     -------
    #     inspect.Signature
    #         The method signature

    #     Raises
    #     ------
    #     ReflectionAttributeError
    #         If the method does not exist on the instance
    #     """
    #     if method_name in self.getPrivateMethods():
    #         method_name = f"_{self.getClassName()}{method_name}"

    #     method = getattr(self._instance, method_name, None)
    #     if method is None or not callable(method):
    #         raise ReflectionAttributeError(f"Method '{method_name}' not found in '{self.getClassName()}'.")

    #     return inspect.signature(method)

















































































    def getProperties(self) -> Dict[str, ClassProperty]:
        """
        Get all properties of the instance.

        Returns
        -------
        List[str]
            List of property names
        """

        properties = {}
        for name, prop in self._instance.__class__.__dict__.items():
            if isinstance(prop, property):
                properties[name] = ClassProperty(
                    name=name,
                    value=getattr(self._instance, name, None),
                    signature=inspect.signature(prop.fget) if prop.fget else None,
                    doc=prop.__doc__ or ""
                )
        return properties

    def getPropertyNames(self) -> List[str]:
        """
        Get all property names of the instance.

        Returns
        -------
        List[str]
            List of property names
        """
        return self.getProperties().keys()

    def getProperty(self, property_name: str) -> Any:
        """
        Get the value of a property.

        Parameters
        ----------
        property_name : str
            Name of the property

        Returns
        -------
        Any
            The value of the property

        Raises
        ------
        AttributeError
            If the property doesn't exist or is not a property
        """
        all_prop = self.getProperties()
        if property_name not in all_prop:
            raise ReflectionValueError(f"Property '{property_name}' not found.")
        return all_prop[property_name].value

    def getPropertySignature(self, property_name: str) -> inspect.Signature:
        """
        Get the signature of a property.

        Parameters
        ----------
        property_name : str
            Name of the property

        Returns
        -------
        inspect.Signature
            The property signature

        Raises
        ------
        AttributeError
            If the property doesn't exist or is not a property
        """
        all_prop = self.getProperties()
        if property_name not in all_prop:
            raise ReflectionValueError(f"Property '{property_name}' not found.")
        return all_prop[property_name].signature

    def getPropertyDoc(self, property_name: str) -> str:
        """
        Get the docstring of a property.

        Parameters
        ----------
        property_name : str
            Name of the property

        Returns
        -------
        str
            The docstring of the property

        Raises
        ------
        AttributeError
            If the property doesn't exist or is not a property
        """
        all_prop = self.getProperties()
        if property_name not in all_prop:
            raise ReflectionValueError(f"Property '{property_name}' not found.")
        return all_prop[property_name].doc









































    def callMethod(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        """
        Call a method on the instance.

        Parameters
        ----------
        method_name : str
            Name of the method to call
        *args : Any
            Positional arguments for the method
        **kwargs : Any
            Keyword arguments for the method

        Returns
        -------
        Any
            The result of the method call

        Raises
        ------
        AttributeError
            If the method does not exist on the instance
        TypeError
            If the method is not callable
        """

        if method_name in self.getPrivateMethods():
            method_name = f"_{self.getClassName()}{method_name}"

        method = getattr(self._instance, method_name, None)

        if method is None:
            raise AttributeError(f"'{self.getClassName()}' object has no method '{method_name}'.")
        if not callable(method):
            raise TypeError(f"'{method_name}' is not callable on '{self.getClassName()}'.")

        if inspect.iscoroutinefunction(method):
            return Coroutine(method(*args, **kwargs)).run()

        return method(*args, **kwargs)

    def getMethodSignature(self, method_name: str) -> inspect.Signature:
        """
        Get the signature of a method.

        Parameters
        ----------
        method_name : str
            Name of the method

        Returns
        -------
        inspect.Signature
            The method signature
        """
        if method_name in self.getPrivateMethods():
            method_name = f"_{self.getClassName()}{method_name}"

        method = getattr(self._instance, method_name)
        if callable(method):
            return inspect.signature(method)

    def getDocstring(self) -> Optional[str]:
        """
        Get the docstring of the instance's class.

        Returns
        -------
        Optional[str]
            The class docstring, or None if not available
        """
        return self._instance.__class__.__doc__

    def getBaseClasses(self) -> Tuple[Type, ...]:
        """
        Get the base classes of the instance's class.

        Returns
        -------
        Tuple[Type, ...]
            Tuple of base classes
        """
        return self._instance.__class__.__bases__

    def isInstanceOf(self, cls: Type) -> bool:
        """
        Check if the instance is of a specific class.

        Parameters
        ----------
        cls : Type
            The class to check against

        Returns
        -------
        bool
            True if the instance is of the specified class
        """
        return isinstance(self._instance, cls)

    def getSourceCode(self) -> Optional[str]:
        """
        Get the source code of the instance's class.

        Returns
        -------
        Optional[str]
            The source code if available, None otherwise
        """
        try:
            return inspect.getsource(self._instance.__class__)
        except (TypeError, OSError):
            return None

    def getFileLocation(self) -> Optional[str]:
        """
        Get the file location where the class is defined.

        Returns
        -------
        Optional[str]
            The file path if available, None otherwise
        """
        try:
            return inspect.getfile(self._instance.__class__)
        except (TypeError, OSError):
            return None

    def getAnnotations(self) -> Dict[str, Any]:
        """
        Get type annotations of the class.

        Returns
        -------
        Dict[str, Any]
            Dictionary of attribute names and their type annotations
        """
        return self._instance.__class__.__annotations__

    def hasAttribute(self, name: str) -> bool:
        """
        Check if the instance has a specific attribute.

        Parameters
        ----------
        name : str
            The attribute name to check

        Returns
        -------
        bool
            True if the attribute exists
        """
        return hasattr(self._instance, name)

    def getAttribute(self, name: str) -> Any:
        """
        Get an attribute value by name.

        Parameters
        ----------
        name : str
            The attribute name

        Returns
        -------
        Any
            The attribute value

        Raises
        ------
        AttributeError
            If the attribute doesn't exist
        """
        attrs = self.getAttributes()
        return attrs.get(name, getattr(self._instance, name, None))

    def setAttribute(self, name: str, value: Any) -> None:
        """
        Set an attribute value.

        Parameters
        ----------
        name : str
            The attribute name
        value : Any
            The value to set

        Raises
        ------
        AttributeError
            If the attribute is read-only
        """
        if callable(value):
            raise AttributeError(f"Cannot set attribute '{name}' to a callable. Use setMacro instead.")
        setattr(self._instance, name, value)

    def removeAttribute(self, name: str) -> None:
        """
        Remove an attribute from the instance.

        Parameters
        ----------
        name : str
            The attribute name to remove

        Raises
        ------
        AttributeError
            If the attribute doesn't exist or is read-only
        """
        if not hasattr(self._instance, name):
            raise AttributeError(f"'{self.getClassName()}' object has no attribute '{name}'.")
        delattr(self._instance, name)

    def setMacro(self, name: str, value: Callable) -> None:
        """
        Set a callable attribute value.

        Parameters
        ----------
        name : str
            The attribute name
        value : Callable
            The callable to set

        Raises
        ------
        AttributeError
            If the value is not callable
        """
        if not callable(value):
            raise AttributeError(f"The value for '{name}' must be a callable.")
        setattr(self._instance, name, value)

    def removeMacro(self, name: str) -> None:
        """
        Remove a callable attribute from the instance.

        Parameters
        ----------
        name : str
            The attribute name to remove

        Raises
        ------
        AttributeError
            If the attribute doesn't exist or is not callable
        """
        if not hasattr(self._instance, name) or not callable(getattr(self._instance, name)):
            raise AttributeError(f"'{self.getClassName()}' object has no callable macro '{name}'.")
        delattr(self._instance, name)

    def getConstructorDependencies(self) -> ClassDependency:
        """
        Get the resolved and unresolved dependencies from the constructor of the instance's class.

        Returns
        -------
        ClassDependency
            A structured representation of the constructor dependencies, containing:
            - resolved: Dictionary of resolved dependencies with their names and values.
            - unresolved: List of unresolved dependencies (parameter names without default values or annotations).
        """
        return ReflectDependencies(self._instance.__class__).getConstructorDependencies()

    def getMethodDependencies(self, method_name: str) -> MethodDependency:
        """
        Get the resolved and unresolved dependencies from a method of the instance's class.

        Parameters
        ----------
        method_name : str
            The name of the method to inspect

        Returns
        -------
        MethodDependency
            A structured representation of the method dependencies, containing:
            - resolved: Dictionary of resolved dependencies with their names and values.
            - unresolved: List of unresolved dependencies (parameter names without default values or annotations).
        """
        return ReflectDependencies(self._instance).getMethodDependencies(method_name)
