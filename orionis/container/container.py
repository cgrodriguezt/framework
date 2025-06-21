from typing import Any, Callable
from orionis.container.enums.lifetimes import Lifetime
from orionis.container.exceptions.container_exception import OrionisContainerException
from orionis.container.exceptions.type_error_exception import OrionisContainerTypeError
from orionis.services.introspection.abstract.reflection_abstract import ReflectionAbstract
from orionis.services.introspection.concretes.reflection_concrete import ReflectionConcrete


class Container:

    def bind(self, abstract: Callable[..., Any] = None, concrete: Callable[..., Any] = None, lifetime: str = Lifetime.TRANSIENT) -> None:
        """
        Binds an abstract type to a concrete implementation with a specified lifetime.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract base type or alias to be bound.
        concrete : Callable[..., Any]
            The concrete implementation to associate with the abstract type.
        lifetime : str, optional
            The lifetime of the service (default is 'transient').
        """
        pass

    def transient(self, abstract: Callable[..., Any], concrete: Callable[..., Any]) -> bool:
        """
        Registers a service with a transient lifetime.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract base type or alias to be bound.
        concrete : Callable[..., Any]
            The concrete implementation to associate with the abstract type.
        """
        # Ensure that abstract is an abstract class and concrete is a concrete class
        try:
            ReflectionAbstract.ensureIsAbstractClass(abstract)
            ReflectionConcrete.ensureIsConcreteClass(concrete)
        except Exception as e:
            raise OrionisContainerTypeError(
                f"Unexpected error registering transient service: {e}"
            ) from e

        # Ensure that concrete does NOT inherit from abstract
        if issubclass(concrete, abstract):
            raise OrionisContainerException(
                "Cannot register a concrete class that is a subclass of the provided abstract class. "
                "Please ensure that the concrete class does not inherit from the specified abstract class."
            )

        # Register the service with transient lifetime
        self.bind(abstract, concrete, Lifetime.TRANSIENT)

        # Return True to indicate successful registration
        return True

    def singleton(self, abstract: Callable[..., Any], concrete: Callable[..., Any]) -> bool:
        """
        Registers a service with a singleton lifetime.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract base type or alias to be bound.
        concrete : Callable[..., Any]
            The concrete implementation to associate with the abstract type.
        """
        # Ensure that abstract is an abstract class and concrete is a concrete class
        try:
            ReflectionAbstract.ensureIsAbstractClass(abstract)
            ReflectionConcrete.ensureIsConcreteClass(concrete)
        except Exception as e:
            raise OrionisContainerTypeError(
                f"Unexpected error registering singleton service: {e}"
            ) from e

        # Ensure that concrete does NOT inherit from abstract
        if issubclass(concrete, abstract):
            raise OrionisContainerException(
                "Cannot register a concrete class that is a subclass of the provided abstract class. "
                "Please ensure that the concrete class does not inherit from the specified abstract class."
            )

        # Register the service with singleton lifetime
        self.bind(abstract, concrete, Lifetime.SINGLETON)

        # Return True to indicate successful registration
        return True

    def scoped(self, abstract: Callable[..., Any], concrete: Callable[..., Any]) -> bool:
        """
        Registers a service with a scoped lifetime.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract base type or alias to be bound.
        concrete : Callable[..., Any]
            The concrete implementation to associate with the abstract type.
        """
        # Ensure that abstract is an abstract class and concrete is a concrete class
        try:
            ReflectionAbstract.ensureIsAbstractClass(abstract)
            ReflectionConcrete.ensureIsConcreteClass(concrete)
        except Exception as e:
            raise OrionisContainerTypeError(
                f"Unexpected error registering scoped service: {e}"
            ) from e

        # Ensure that concrete does NOT inherit from abstract
        if issubclass(concrete, abstract):
            raise OrionisContainerException(
                "Cannot register a concrete class that is a subclass of the provided abstract class. "
                "Please ensure that the concrete class does not inherit from the specified abstract class."
            )

        # Register the service with scoped lifetime
        self.bind(abstract, concrete, Lifetime.SCOPED)

        # Return True to indicate successful registration
        return True