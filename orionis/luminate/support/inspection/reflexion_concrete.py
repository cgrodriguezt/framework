from typing import Type, TypeVar
import abc

T = TypeVar('T')
ABC = TypeVar('ABC', bound=abc.ABC)

class ReflexionConcrete:
    """A reflection object encapsulating a concrete class.

    Parameters
    ----------
    concrete : Type[T]
        The concrete class being reflected upon

    Attributes
    ----------
    _concrete : Type[T]
        The encapsulated concrete class
    """

    def __init__(self, concrete: Type[T]) -> None:
        """Initialize with the concrete class."""
        self._concrete = concrete

