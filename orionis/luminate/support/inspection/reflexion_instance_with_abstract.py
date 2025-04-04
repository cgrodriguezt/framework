from typing import Any, Type, Dict, List, Tuple, Callable, Optional, Set, TypeVar
import inspect
import abc

T = TypeVar('T')
ABC = TypeVar('ABC', bound=abc.ABC)

class ReflexionInstanceWithAbstract:
    """A reflection object encapsulating a class instance and its abstract parent.

    This class provides methods to inspect both the concrete instance and its
    abstract parent class, including their relationships and implementations.

    Parameters
    ----------
    instance : Any
        The instance being reflected upon
    abstract : Type[ABC]
        The abstract parent class

    Attributes
    ----------
    _instance : Any
        The encapsulated instance
    _abstract : Type[ABC]
        The encapsulated abstract parent class
    """

    def __init__(self, instance: Any, abstract: Type[ABC]) -> None:
        """Initialize with the instance and abstract parent."""
        self._instance = instance
        self._abstract = abstract

    def getClassName(self) -> str:
        """Get the name of the instance's class.

        Returns
        -------
        str
            The name of the concrete class
        """
        return self._instance.__class__.__name__

    def getAbstractClassName(self) -> str:
        """Get the name of the abstract parent class.

        Returns
        -------
        str
            The name of the abstract class
        """
        return self._abstract.__name__

    def getImplementationStatus(self) -> Dict[str, bool]:
        """Check which abstract methods are implemented.

        Returns
        -------
        Dict[str, bool]
            Dictionary mapping abstract method names to implementation status
        """
        abstract_methods = getattr(self._abstract, '__abstractmethods__', set())
        return {
            method: method in dir(self._instance)
            for method in abstract_methods
        }

    def getMissingImplementations(self) -> Set[str]:
        """Get abstract methods not implemented by the concrete class.

        Returns
        -------
        Set[str]
            Set of abstract method names not implemented
        """
        abstract_methods = getattr(self._abstract, '__abstractmethods__', set())
        return abstract_methods - set(dir(self._instance))

    def isProperImplementation(self) -> bool:
        """Check if the instance properly implements all abstract methods.

        Returns
        -------
        bool
            True if all abstract methods are implemented, False otherwise
        """
        return len(self.getMissingImplementations()) == 0

    def getAbstractMethods(self) -> Set[str]:
        """Get all abstract methods from the parent class.

        Returns
        -------
        Set[str]
            Set of abstract method names
        """
        return getattr(self._abstract, '__abstractmethods__', set())

    def getConcreteMethods(self) -> List[str]:
        """Get all concrete methods of the instance.

        Returns
        -------
        List[str]
            List of method names implemented by the instance
        """
        return [name for name, _ in inspect.getmembers(
            self._instance,
            predicate=inspect.ismethod
        )]

    def getOverriddenMethods(self) -> Dict[str, Tuple[Type, Type]]:
        """Get methods that override abstract ones with their signatures.

        Returns
        -------
        Dict[str, Tuple[Type, Type]]
            Dictionary mapping method names to tuples of
            (abstract_signature, concrete_signature)
        """
        overridden = {}
        abstract_methods = self.getAbstractMethods()

        for method in abstract_methods:
            if hasattr(self._instance, method):
                abstract_sig = inspect.signature(getattr(self._abstract, method))
                concrete_sig = inspect.signature(getattr(self._instance, method))
                overridden[method] = (abstract_sig, concrete_sig)

        return overridden

    def checkSignatureCompatibility(self) -> Dict[str, bool]:
        """Check if implemented methods match abstract signatures.

        Returns
        -------
        Dict[str, bool]
            Dictionary mapping method names to compatibility status
        """
        compatibility = {}
        overridden = self.getOverriddenMethods()

        for method, (abstract_sig, concrete_sig) in overridden.items():
            compatibility[method] = (
                abstract_sig.parameters == concrete_sig.parameters and
                abstract_sig.return_annotation == concrete_sig.return_annotation
            )

        return compatibility

    def getAbstractProperties(self) -> Set[str]:
        """Get all abstract properties from the parent class.

        Returns
        -------
        Set[str]
            Set of abstract property names
        """
        return {
            name for name, member in inspect.getmembers(
                self._abstract,
                lambda x: isinstance(x, property) and 
                name in getattr(self._abstract, '__abstractmethods__', set())
            )
        }

    def getInstanceAttributes(self) -> Dict[str, Any]:
        """Get all attributes of the concrete instance.

        Returns
        -------
        Dict[str, Any]
            Dictionary of attribute names and their values
        """
        return vars(self._instance)

    def getAbstractClassDocstring(self) -> Optional[str]:
        """Get the docstring of the abstract parent class.

        Returns
        -------
        Optional[str]
            The abstract class docstring, or None if not available
        """
        return self._abstract.__doc__

    def getConcreteClassDocstring(self) -> Optional[str]:
        """Get the docstring of the concrete instance's class.

        Returns
        -------
        Optional[str]
            The concrete class docstring, or None if not available
        """
        return self._instance.__class__.__doc__

    def getAbstractClassModule(self) -> str:
        """Get the module name where the abstract class is defined.

        Returns
        -------
        str
            The module name of the abstract class
        """
        return self._abstract.__module__

    def getConcreteClassModule(self) -> str:
        """Get the module name where the concrete class is defined.

        Returns
        -------
        str
            The module name of the concrete class
        """
        return self._instance.__class__.__module__

    def isDirectSubclass(self) -> bool:
        """Check if the concrete class directly inherits from the abstract class.

        Returns
        -------
        bool
            True if direct subclass, False otherwise
        """
        return self._abstract in self._instance.__class__.__bases__

    def getAbstractClassHierarchy(self) -> List[Type]:
        """Get the inheritance hierarchy of the abstract class.

        Returns
        -------
        List[Type]
            List of classes in the inheritance hierarchy
        """
        return inspect.getmro(self._abstract)

    def getConcreteClassHierarchy(self) -> List[Type]:
        """Get the inheritance hierarchy of the concrete class.

        Returns
        -------
        List[Type]
            List of classes in the inheritance hierarchy
        """
        return inspect.getmro(self._instance.__class__)

    def getCommonBaseClasses(self) -> List[Type]:
        """Get base classes common to both abstract and concrete classes.

        Returns
        -------
        List[Type]
            List of common base classes
        """
        abstract_bases = set(inspect.getmro(self._abstract))
        concrete_bases = set(inspect.getmro(self._instance.__class__))
        return list(abstract_bases & concrete_bases - {self._abstract, object})

    def getAbstractClassSource(self) -> Optional[str]:
        """Get the source code of the abstract class.

        Returns
        -------
        Optional[str]
            The source code if available, None otherwise
        """
        try:
            return inspect.getsource(self._abstract)
        except (TypeError, OSError):
            return None

    def getConcreteClassSource(self) -> Optional[str]:
        """Get the source code of the concrete class.

        Returns
        -------
        Optional[str]
            The source code if available, None otherwise
        """
        try:
            return inspect.getsource(self._instance.__class__)
        except (TypeError, OSError):
            return None

    def getAbstractClassFile(self) -> Optional[str]:
        """Get the file location of the abstract class definition.

        Returns
        -------
        Optional[str]
            The file path if available, None otherwise
        """
        try:
            return inspect.getfile(self._abstract)
        except (TypeError, OSError):
            return None

    def getConcreteClassFile(self) -> Optional[str]:
        """Get the file location of the concrete class definition.

        Returns
        -------
        Optional[str]
            The file path if available, None otherwise
        """
        try:
            return inspect.getfile(self._instance.__class__)
        except (TypeError, OSError):
            return None