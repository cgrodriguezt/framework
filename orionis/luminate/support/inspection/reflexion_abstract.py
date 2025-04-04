from typing import Type, TypeVar
import abc

T = TypeVar('T')
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
