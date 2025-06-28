import inspect
from typing import Any, Type
from orionis.services.introspection.abstract.reflection_abstract import ReflectionAbstract
from orionis.services.introspection.concretes.reflection_concrete import ReflectionConcrete
from orionis.services.introspection.instances.reflection_instance import ReflectionInstance
from orionis.services.introspection.modules.reflection_module import ReflectionModule

class Reflection:
    """
    Provides static methods to create reflection objects for various Python constructs.

    This class offers factory methods to obtain specialized reflection objects for instances,
    abstract classes, concrete classes, and modules. Each method returns an object that
    encapsulates the target and provides introspection capabilities.
    """

    @staticmethod
    def instance(instance: Any) -> 'ReflectionInstance':
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
    def abstract(abstract: Type) -> 'ReflectionAbstract':
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
    def concrete(concrete: Type) -> 'ReflectionConcrete':
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
    def module(module: str) -> 'ReflectionModule':
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
    def isBuiltin(obj: Any) -> bool:
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
