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

    Methods
    -------
    instance(instance: Any) -> ReflectionInstance
        Create a reflection object for a class instance.
    abstract(abstract: Type) -> ReflectionAbstract
        Create a reflection object for an abstract class.
    concrete(concrete: Type) -> ReflectionConcrete
        Create a reflection object for a concrete class.
    module(module: str) -> ReflectionModule
        Create a reflection object for a module.
    """

    @staticmethod
    def instance(instance: Any) -> 'ReflectionInstance':
        """
        Create a reflection object for a class instance.

        Parameters
        ----------
        instance : Any
            The instance to reflect upon.

        Returns
        -------
        ReflectionInstance
            A reflection object encapsulating the instance.
        """
        return ReflectionInstance(instance)

    @staticmethod
    def abstract(abstract: Type) -> 'ReflectionAbstract':
        """Create a reflection object for an abstract class.

        Parameters
        ----------
        abstract : Type
            The abstract class to reflect upon

        Returns
        -------
        ReflectionAbstract
            A reflection object encapsulating the abstract class
        """
        return ReflectionAbstract(abstract)

    @staticmethod
    def concrete(concrete: Type) -> 'ReflectionConcrete':
        """Create a reflection object for a concrete class.

        Parameters
        ----------
        concrete : Type
            The concrete class to reflect upon

        Returns
        -------
        ReflectionConcrete
            A reflection object encapsulating the concrete class
        """
        return ReflectionConcrete(concrete)

    @staticmethod
    def module(module: str) -> 'ReflectionModule':
        """Create a reflection object for a module.

        Parameters
        ----------
        module : str
            The module name to reflect upon

        Returns
        -------
        ReflectionModule
            A reflection object encapsulating the module
        """
        return ReflectionModule(module)
