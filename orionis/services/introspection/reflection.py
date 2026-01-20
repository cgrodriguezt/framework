import abc
import inspect
from typing import Any, Type
import typing
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.callables.reflection import ReflectionCallable
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.services.introspection.instances.reflection import ReflectionInstance
from orionis.services.introspection.modules.reflection import ReflectionModule

class Reflection:
    """
    Provides static methods to create reflection objects for various Python constructs.

    This class offers factory methods to obtain specialized reflection objects for instances,
    abstract classes, concrete classes, and modules. Each method returns an object that
    encapsulates the target and provides introspection capabilities.
    """

    @staticmethod
    def instance(instance: Any) -> "ReflectionInstance":
        """
        Create a ReflectionInstance for the given object instance.

        Parameters
        ----------
        instance : Any
            The object instance to reflect.

        Returns
        -------
        ReflectionInstance
            A reflection object for the given instance.
        """
        return ReflectionInstance(instance)

    @staticmethod
    def abstract(abstract: Type) -> "ReflectionAbstract":
        """
        Create a ReflectionAbstract for the given abstract class.

        Parameters
        ----------
        abstract : Type
            The abstract class to reflect.

        Returns
        -------
        ReflectionAbstract
            A reflection object for the given abstract class.
        """
        return ReflectionAbstract(abstract)

    @staticmethod
    def concrete(concrete: Type) -> "ReflectionConcrete":
        """
        Create a ReflectionConcrete for the given concrete class.

        Parameters
        ----------
        concrete : Type
            The concrete class to reflect.

        Returns
        -------
        ReflectionConcrete
            A reflection object for the given concrete class.
        """
        return ReflectionConcrete(concrete)

    @staticmethod
    def module(module: str) -> "ReflectionModule":
        """
        Create a ReflectionModule for the given module name.

        Parameters
        ----------
        module : str
            The name of the module to reflect.

        Returns
        -------
        ReflectionModule
            A reflection object for the given module.
        """
        return ReflectionModule(module)

    @staticmethod
    def callable(fn: callable) -> "ReflectionCallable":
        """
        Create a ReflectionCallable instance for the given callable function.

        Parameters
        ----------
        fn : callable
            The function or method to wrap in a ReflectionCallable.

        Returns
        -------
        ReflectionCallable
            A reflection object that encapsulates the provided callable.
        """
        return ReflectionCallable(fn)

    @staticmethod
    def isAbstract(obj: Any) -> bool:
        """
        Check if the object is an abstract base class.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is abstract, False otherwise.
        """
        return inspect.isabstract(obj)

    @staticmethod
    def isConcreteClass(obj: Any) -> bool:
        """
        Determines whether the provided object is a concrete (non-abstract, non-interface, non-builtin) class.

        This method checks if the given object is a user-defined class that is neither a built-in type nor an abstract/interface class.

        Parameters
        ----------
        obj : Any
            The object to check for concreteness.

        Returns
        -------
        bool
            Returns True if the object is a concrete class; otherwise, returns False.
        """
        # Ensure the object is a class type
        if not isinstance(obj, type):
            return False

        # Exclude built-in or primitive types
        if Reflection.isBuiltIn(obj):
            return False

        # Check if the class is abstract
        if Reflection.isAbstract(obj):
            return False

        # Check if the type is a generic type (e.g., List[T], Dict[K, V])
        if Reflection.isGeneric(obj):
            return False

        # Check if the type is a protocol (typing.Protocol or similar)
        if Reflection.isProtocol(obj):
            return False

        # Check if the type is a typing construct (e.g., Union, Optional)
        if Reflection.isTypingConstruct(obj):
            return False

        # Check for ABC inheritance to identify interfaces
        if abc.ABC in obj.__bases__:
            return False

        # Ensure the class has an __init__ method
        if not hasattr(obj, "__init__"):
            return False

        # If all checks pass, the class is concrete
        return True

    @staticmethod
    def isAsyncGen(obj: Any) -> bool:
        """
        Check if the object is an asynchronous generator.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is an async generator, False otherwise.
        """
        return inspect.isasyncgen(obj)

    @staticmethod
    def isAsyncGenFunction(obj: Any) -> bool:
        """
        Check if the object is an asynchronous generator function.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is an async generator function, False otherwise.
        """
        return inspect.isasyncgenfunction(obj)

    @staticmethod
    def isAwaitable(obj: Any) -> bool:
        """
        Check if the object can be awaited.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is awaitable, False otherwise.
        """
        return inspect.isawaitable(obj)

    @staticmethod
    def isBuiltIn(obj: Any) -> bool:
        """
        Check if the object is a built-in function or method.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is a built-in, False otherwise.
        """
        return inspect.isbuiltin(obj)

    @staticmethod
    def isClass(obj: Any) -> bool:
        """
        Check if the object is a class.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is a class, False otherwise.
        """
        return inspect.isclass(obj)

    @staticmethod
    def isCode(obj: Any) -> bool:
        """
        Check if the object is a code object.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is a code object, False otherwise.
        """
        return inspect.iscode(obj)

    @staticmethod
    def isCoroutine(obj: Any) -> bool:
        """
        Check if the object is a coroutine.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is a coroutine, False otherwise.
        """
        return inspect.iscoroutine(obj)

    @staticmethod
    def isCoroutineFunction(obj: Any) -> bool:
        """
        Check if the object is a coroutine function.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is a coroutine function, False otherwise.
        """
        return inspect.iscoroutinefunction(obj)

    @staticmethod
    def isDataDescriptor(obj: Any) -> bool:
        """
        Check if the object is a data descriptor.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is a data descriptor, False otherwise.
        """
        return inspect.isdatadescriptor(obj)

    @staticmethod
    def isFrame(obj: Any) -> bool:
        """
        Check if the object is a frame object.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is a frame object, False otherwise.
        """
        return inspect.isframe(obj)

    @staticmethod
    def isFunction(obj: Any) -> bool:
        """
        Check if the object is a Python function.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is a function, False otherwise.
        """
        return inspect.isfunction(obj)

    @staticmethod
    def isGenerator(obj: Any) -> bool:
        """
        Check if the object is a generator.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is a generator, False otherwise.
        """
        return inspect.isgenerator(obj)

    @staticmethod
    def isGeneratorFunction(obj: Any) -> bool:
        """
        Check if the object is a generator function.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is a generator function, False otherwise.
        """
        return inspect.isgeneratorfunction(obj)

    @staticmethod
    def isGetSetDescriptor(obj: Any) -> bool:
        """
        Check if the object is a getset descriptor.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is a getset descriptor, False otherwise.
        """
        return inspect.isgetsetdescriptor(obj)

    @staticmethod
    def isMemberDescriptor(obj: Any) -> bool:
        """
        Check if the object is a member descriptor.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is a member descriptor, False otherwise.
        """
        return inspect.ismemberdescriptor(obj)

    @staticmethod
    def isMethod(obj: Any) -> bool:
        """
        Check if the object is a method.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is a method, False otherwise.
        """
        return inspect.ismethod(obj)

    @staticmethod
    def isMethodDescriptor(obj: Any) -> bool:
        """
        Check if the object is a method descriptor.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is a method descriptor, False otherwise.
        """
        return inspect.ismethoddescriptor(obj)

    @staticmethod
    def isModule(obj: Any) -> bool:
        """
        Check if the object is a module.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is a module, False otherwise.
        """
        return inspect.ismodule(obj)

    @staticmethod
    def isRoutine(obj: Any) -> bool:
        """
        Check if the object is a user-defined or built-in function or method.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is a routine, False otherwise.
        """
        return inspect.isroutine(obj)

    @staticmethod
    def isTraceback(obj: Any) -> bool:
        """
        Check if the object is a traceback object.

        Parameters
        ----------
        obj : Any
            The object to check.

        Returns
        -------
        bool
            True if the object is a traceback object, False otherwise.
        """
        return inspect.istraceback(obj)

    @staticmethod
    def isGeneric(obj: Any) -> bool:
        """
        Checks if a type is a generic type (e.g., List[T], Dict[K,V]).

        Parameters
        ----------
        obj : Any
            The type to check.

        Returns
        -------
        bool
            True if the type is generic, False otherwise.
        """
        # Check for generic alias (Python 3.7+)
        if hasattr(typing, "get_origin") and typing.get_origin(obj) is not None:
            return True

        # Check for older style generic types
        if hasattr(obj, "__origin__"):
            return True

        # Check if it's a typing construct
        if hasattr(typing, "_GenericAlias") and isinstance(obj, typing._GenericAlias):
            return True

        # Check for type variables
        if hasattr(typing, "TypeVar") and isinstance(obj, typing.TypeVar):
            return True

        # If none of the checks matched, it's not a generic type
        return False

    @staticmethod
    def isProtocol(obj: Any) -> bool:
        """
        Determines whether the provided object is a subclass of `typing.Protocol`, indicating it is a protocol type.

        Parameters
        ----------
        obj : Any
            The object or type to evaluate.

        Returns
        -------
        bool
            True if `obj` is a class that is a subclass of `typing.Protocol` (but not `Protocol` itself), otherwise False.
        """
        # Retrieve the Protocol base class from the typing module, if available
        protocol = getattr(typing, "Protocol", None)

        # Protocol is not available in this Python version
        if protocol is None:
            return False

        # Check if obj is a class, is a subclass of Protocol, and is not Protocol itself
        if isinstance(obj, type) and issubclass(obj, protocol) and obj is not protocol:
            return True

        # If none of the conditions are met, obj is not a Protocol
        return False

    @staticmethod
    def isInstance(obj: Any) -> bool:
        """
        Determines if the given object is an instance of a user-defined class.

        Parameters
        ----------
        obj : Any
            Object to evaluate.

        Returns
        -------
        bool
            True if the object is an instance of a user-defined class, False otherwise.
        """
        # Check if obj is an object and not a class type
        if not (isinstance(obj, object) and not isinstance(obj, type)):
            return False

        # Exclude instances of built-in or abstract base classes
        module = type(obj).__module__
        if module in {"builtins", "abc"}:
            return False

        # Object is a valid instance
        return True

    @staticmethod
    def isTypingConstruct(obj: Any) -> bool:
        """
        Determines if the provided object is a construct from the `typing` module.

        This method checks whether the given object corresponds to any of the recognized constructs
        defined in Python's `typing` module, such as `Union`, `Optional`, or `TypeVar`.

        Parameters
        ----------
        obj : Any
            The object to evaluate.

        Returns
        -------
        bool
            True if `obj` is a recognized typing construct; otherwise, False.
        """
        # List of known typing constructs to check against
        typing_constructs = [
            "Any", "Union", "Optional", "List", "Dict", "Set", "Tuple",
            "Callable", "TypeVar", "Generic", "Protocol", "Literal",
            "Final", "TypedDict", "NewType", "Deque", "DefaultDict",
            "Counter", "ChainMap",
        ]

        # Get the class name of the object and check if it matches any known typing construct
        obj_type_name = type(obj).__name__

        # Return True if the object's type name is in the list of typing constructs
        if obj_type_name in typing_constructs:
            return True

        # Return False if no match is found
        return False
