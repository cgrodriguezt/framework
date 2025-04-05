from typing import Any, Type, Dict, List, Tuple, Callable, Optional, TypeVar, Set
import inspect
import abc
from functools import wraps

ABC = TypeVar('ABC', bound=abc.ABC)

class ReflexionAbstract:
    """A reflection object encapsulating an abstract class.

    Parameters
    ----------
    abstract : Type[ABC]
        The abstract class being reflected upon

    Attributes
    ----------
    _abstract : Type[ABC]
        The encapsulated abstract class
    """

    def __init__(self, abstract: Type[ABC]) -> None:
        """Initialize with the abstract class."""
        self._abstract = abstract

    def getClassName(self) -> str:
        """Get the name of the abstract class.

        Returns
        -------
        str
            The name of the abstract class
        """
        return self._abstract.__name__

    def getModuleName(self) -> str:
        """Get the name of the module where the abstract class is defined.

        Returns
        -------
        str
            The module name
        """
        return self._abstract.__module__

    def getAbstractMethods(self) -> Set[str]:
        """Get all abstract method names required by the class.

        Returns
        -------
        Set[str]
            Set of abstract method names
        """
        return {name for name, _ in self._abstract.__abstractmethods__}

    def getConcreteMethods(self) -> Dict[str, Callable]:
        """Get all concrete methods implemented in the abstract class.

        Returns
        -------
        Dict[str, Callable]
            Dictionary of method names and their implementations
        """
        return {
            name: member for name, member in inspect.getmembers(
                self._abstract,
                predicate=inspect.isfunction
            ) if not name.startswith('_') and name not in self.getAbstractMethods()
        }

    def getStaticMethods(self) -> List[str]:
        """Get all static method names of the abstract class.

        Returns
        -------
        List[str]
            List of static method names
        """
        return [
            name for name in dir( self._abstract)
            if not name.startswith('_') and
            isinstance(inspect.getattr_static( self._abstract, name), staticmethod)
        ]

    def getClassMethods(self) -> List[str]:
        """Get all class method names of the abstract class.

        Returns
        -------
        List[str]
            List of class method names
        """
        return [
            name for name, member in inspect.getmembers(
                self._abstract,
                predicate=lambda x: isinstance(x, classmethod))
            if not name.startswith('_')
        ]

    def getProperties(self) -> List[str]:
        """Get all property names of the abstract class.

        Returns
        -------
        List[str]
            List of property names
        """
        return [
            name for name, member in inspect.getmembers(
                self._abstract,
                predicate=lambda x: isinstance(x, property))
            if not name.startswith('_')
        ]

    def getMethodSignature(self, methodName: str) -> inspect.Signature:
        """Get the signature of a method.

        Parameters
        ----------
        methodName : str
            Name of the method

        Returns
        -------
        inspect.Signature
            The method signature

        Raises
        ------
        AttributeError
            If the method doesn't exist
        """
        method = getattr(self._abstract, methodName)
        return inspect.signature(method)

    def getDocstring(self) -> Optional[str]:
        """Get the docstring of the abstract class.

        Returns
        -------
        Optional[str]
            The class docstring
        """
        return self._abstract.__doc__

    def getBaseAbstractClasses(self) -> Tuple[Type[ABC], ...]:
        """Get the abstract base classes.

        Returns
        -------
        Tuple[Type[ABC], ...]
            Tuple of abstract base classes
        """
        return tuple(
            base for base in self._abstract.__bases__
            if inspect.isabstract(base)
        )

    def getInterfaceMethods(self) -> Dict[str, inspect.Signature]:
        """Get all abstract methods with their signatures.

        Returns
        -------
        Dict[str, inspect.Signature]
            Dictionary of method names and their signatures
        """
        return {
            name: inspect.signature(getattr(self._abstract, name))
            for name in self.getAbstractMethods()
        }

    def isSubclassOf(self, abstract_class: Type[ABC]) -> bool:
        """Check if the abstract class inherits from another abstract class.

        Parameters
        ----------
        abstract_class : Type[ABC]
            The abstract class to check against

        Returns
        -------
        bool
            True if this is a subclass
        """
        return issubclass(self._abstract, abstract_class)

    def getSourceCode(self) -> Optional[str]:
        """Get the source code of the abstract class.

        Returns
        -------
        Optional[str]
            The source code if available
        """
        try:
            return inspect.getsource(self._abstract)
        except (TypeError, OSError):
            return None

    def getFileLocation(self) -> Optional[str]:
        """Get the file location where the abstract class is defined.

        Returns
        -------
        Optional[str]
            The file path if available
        """
        try:
            return inspect.getfile(self._abstract)
        except (TypeError, OSError):
            return None

    def getAnnotations(self) -> Dict[str, Any]:
        """Get type annotations of the abstract class.

        Returns
        -------
        Dict[str, Any]
            Dictionary of attribute names and their type annotations
        """
        return self._abstract.__annotations__

    def getDecorators(self, method_name: str) -> List[Callable]:
        """Get decorators applied to a method.

        Parameters
        ----------
        method_name : str
            Name of the method

        Returns
        -------
        List[Callable]
            List of decorator functions
        """
        method = getattr(self._abstract, method_name)
        decorators = []

        if hasattr(method, '__wrapped__'):
            # Unwrap decorated functions
            while hasattr(method, '__wrapped__'):
                decorators.append(method)
                method = method.__wrapped__

        return decorators

    def isProtocol(self) -> bool:
        """Check if the abstract class is a Protocol.

        Returns
        -------
        bool
            True if this is a Protocol class
        """
        return hasattr(self._abstract, '_is_protocol') and self._abstract._is_protocol

    def getRequiredAttributes(self) -> Set[str]:
        """For Protocol classes, get required attributes.

        Returns
        -------
        Set[str]
            Set of required attribute names
        """
        if not self.isProtocol():
            return set()

        return {
            name for name in dir(self._abstract)
            if not name.startswith('_') and not inspect.isfunction(getattr(self._abstract, name))
        }