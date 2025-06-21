from typing import Any, Callable
from orionis.container.enums.lifetimes import Lifetime
from orionis.container.exceptions.type_error_exception import OrionisContainerTypeError
from orionis.services.introspection.abstract.reflection_abstract import ReflectionAbstract


class Container:

    def transient(self, abstract: Callable[..., Any], concrete: Callable[..., Any]) -> None:
        """
        Registers a service with a transient lifetime.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract base type or alias to be bound.
        concrete : Callable[..., Any]
            The concrete implementation to associate with the abstract type.
        """

        try:
            ReflectionAbstract.ensureIsAbstractClass(abstract)
        except Exception as e:
            raise OrionisContainerTypeError(f"Type error while registering service: {e}")