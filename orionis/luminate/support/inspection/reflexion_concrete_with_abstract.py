from typing import Type, TypeVar
import abc

T = TypeVar('T')
ABC = TypeVar('ABC', bound=abc.ABC)


class ReflexionConcreteWithAbstract:
    """A reflection object encapsulating a concrete class and its abstract parent.

    Parameters
    ----------
    concrete : Type[T]
        The concrete class being reflected upon
    abstract : Type[ABC]
        The abstract parent class

    Attributes
    ----------
    _concrete : Type[T]
        The encapsulated concrete class
    _abstract : Type[ABC]
        The encapsulated abstract parent class
    """

    def __init__(self, concrete: Type[T], abstract: Type[ABC]) -> None:
        """Initialize with the concrete class and abstract parent."""
        self._concrete = concrete
        self._abstract = abstract


