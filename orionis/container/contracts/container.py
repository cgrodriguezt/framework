from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from collections.abc import Callable
    from orionis.container.context.manager import ScopeManager
    from orionis.container.entities.binding import Binding

class IContainer(ABC):

    @abstractmethod
    def singleton(
        self,
        abstract: Callable[..., Any],
        concrete: Callable[..., Any],
        *,
        alias: str | None = None,
        enforce_decoupling: bool = False,
    ) -> bool | None:
        """
        Register a service with singleton lifetime.

        Validate the abstract type and concrete class, enforce decoupling if specified,
        and ensure all abstract methods are implemented. Remove any previous binding
        for the same abstract or alias. Register the concrete implementation to the
        abstract type with singleton lifetime.

        Parameters
        ----------
        abstract : Callable[..., Any]
            Abstract base class or interface to bind.
        concrete : Callable[..., Any]
            Concrete class to associate.
        alias : str, optional
            Custom alias for registration.
        enforce_decoupling : bool, optional
            If True, concrete must not inherit from abstract.

        Returns
        -------
        bool or None
            True if registration succeeds, None if an exception occurs.

        Raises
        ------
        OrionisContainerTypeError
            If type validation fails.
        OrionisContainerException
            If decoupling or implementation checks fail.
        """

    @abstractmethod
    def transient(
        self,
        abstract: Callable[..., Any],
        concrete: Callable[..., Any],
        *,
        alias: str | None = None,
        enforce_decoupling: bool = False,
    ) -> bool | None:
        """
        Register a service with transient lifetime.

        Bind a concrete implementation to an abstract base type or interface. Each
        resolution creates a new instance. Validate types, enforce decoupling, check
        abstract method implementation, and manage aliases.

        Parameters
        ----------
        abstract : Callable[..., Any]
            Abstract class or interface to bind.
        concrete : Callable[..., Any]
            Concrete class to associate.
        alias : str, optional
            Custom alias for registration.
        enforce_decoupling : bool, optional
            If True, concrete must not inherit from abstract.

        Returns
        -------
        bool or None
            True if registration succeeds, None if an exception occurs.

        Raises
        ------
        OrionisContainerTypeError
            If type validation fails.
        OrionisContainerException
            If decoupling or implementation checks fail.
        """

    @abstractmethod
    def scoped(
        self,
        abstract: Callable[..., Any],
        concrete: Callable[..., Any],
        *,
        alias: str | None = None,
        enforce_decoupling: bool = False,
    ) -> bool | None:
        """
        Register a service with scoped lifetime.

        Bind a concrete implementation to an abstract base type or interface. Each
        scope context creates a new instance. Validate types, enforce decoupling,
        check abstract method implementation, and manage aliases.

        Parameters
        ----------
        abstract : Callable[..., Any]
            Abstract class or interface to bind.
        concrete : Callable[..., Any]
            Concrete class to associate.
        alias : str | None, optional
            Custom alias for registration.
        enforce_decoupling : bool, optional
            If True, concrete must not inherit from abstract.

        Returns
        -------
        bool or None
            True if registration succeeds, None if an exception occurs.

        Raises
        ------
        OrionisContainerTypeError
            If type validation fails.
        OrionisContainerException
            If decoupling or implementation checks fail.
        """

    @abstractmethod
    def scopedInstance(
        self,
        abstract: Callable[..., Any],
        instance: type[Any],
        *,
        alias: str | None = None,
        enforce_decoupling: bool = False,
    ) -> bool | None:
        """
        Register an instance with scoped lifetime for an abstract type or interface.

        Parameters
        ----------
        abstract : Callable[..., Any]
            Abstract class or interface to associate with the instance.
        instance : type[Any]
            Instance to register.
        alias : str | None, optional
            Alias for registration. If not provided, a default alias is generated.
        enforce_decoupling : bool, optional
            If True, instance's class must not inherit from abstract.

        Returns
        -------
        bool or None
            True if registration succeeds, None otherwise.

        Raises
        ------
        OrionisContainerTypeError
            If abstract is not an abstract class or alias is invalid.
        OrionisContainerException
            If instance is not valid, fails decoupling, or no scope is active.

        Notes
        -----
        Register the instance with scoped lifetime, available only in the current
        scope. Remove any previous binding for the same abstract or alias.
        """

    @abstractmethod
    def instance(
        self,
        abstract: Callable[..., Any],
        instance: type[Any],
        *,
        alias: str | None = None,
        enforce_decoupling: bool = False,
    ) -> bool | None:
        """
        Register an instance with singleton lifetime for an abstract type or interface.

        Validate the abstract type and instance, enforce decoupling if specified, and
        ensure all abstract methods are implemented. Register the instance under both
        the abstract and alias.

        Parameters
        ----------
        abstract : Callable[..., Any]
            Abstract class or interface to associate with the instance.
        instance : Any
            Concrete instance to register.
        alias : str, optional
            Alias to register the instance under. If not provided, a default alias is
            generated.
        enforce_decoupling : bool, optional
            If True, instance's class must not inherit from abstract. If False, must
            inherit.

        Returns
        -------
        bool or None
            Returns True if registration succeeds, None otherwise.

        Raises
        ------
        OrionisContainerTypeError
            If abstract is not an abstract class or instance is not valid.
        OrionisContainerException
            If decoupling check fails or abstract methods are not implemented.
        """

    @abstractmethod
    def callable(
        self,
        fn: Callable[..., Any],
        *,
        alias: str,
    ) -> bool | None:
        """
        Register a callable under a unique alias with transient lifetime.

        Parameters
        ----------
        fn : Callable[..., Any]
            The function or factory to register.
        alias : str
            The alias to register the function under.

        Returns
        -------
        bool or None
            True if registration succeeds, None if an exception occurs.

        Raises
        ------
        OrionisContainerTypeError
            If the alias is invalid or fn is not callable.
        OrionisContainerException
            If registration fails unexpectedly.

        Notes
        -----
        Registers the function with transient lifetime. Removes any previous
        registration under the same alias.
        """

    @abstractmethod
    def bound(
        self,
        abstract_or_alias: type[Any],
    ) -> bool:
        """
        Check if a service is registered in the container.

        Parameters
        ----------
        abstract_or_alias : type[Any]
            Abstract class, interface, or alias to check.

        Returns
        -------
        bool
            True if the service is registered, False otherwise.

        Notes
        -----
        Validate both bindings and aliases.
        """

    @abstractmethod
    def getBinding(
        self,
        abstract_or_alias: type[Any],
    ) -> Binding | None:
        """
        Retrieve the binding for an abstract type or alias.

        Parameters
        ----------
        abstract_or_alias : type[Any]
            Abstract class, interface, or alias to look up.

        Returns
        -------
        Binding or None
            Returns the associated binding if found, otherwise None.

        Notes
        -----
        Looks up the binding first in the main bindings dictionary, then in the
        aliases dictionary if not found.
        """

    @abstractmethod
    def drop(
        self,
        abstract: Callable[..., Any] | None = None,
        alias: str | None = None,
    ) -> bool:
        """
        Remove a service registration by abstract type or alias.

        Parameters
        ----------
        abstract : Callable[..., Any], optional
            Abstract class or interface to remove.
        alias : str, optional
            Alias to remove.

        Returns
        -------
        bool
            True if any registration was removed, False otherwise.

        Notes
        -----
        Cleans up bindings, aliases, singleton cache, and resolution cache.
        """

    @abstractmethod
    def createScope(self) -> ScopeManager:
        """
        Create a new scope context manager for scoped services.

        Returns
        -------
        ScopeManager
            A context manager that manages the lifecycle of scoped services.
        """

    @abstractmethod
    def make(
        self,
        type_: type[Any],
        *args: tuple,
        **kwargs: dict,
    ) -> type[Any]:
        """
        Resolve and instantiate a service or type.

        Parameters
        ----------
        type_ : Any
            Abstract type, class, or alias to resolve.
        *args : tuple
            Positional arguments for the constructor or factory.
        **kwargs : dict
            Keyword arguments for the constructor or factory.

        Returns
        -------
        Any
            The resolved and instantiated object.

        Raises
        ------
        OrionisContainerException
            If the type cannot be resolved.
        """

    @abstractmethod
    def resolve(
        self,
        binding: Binding,
        *args: tuple,
        **kwargs: dict,
    ) -> type[Any]:
        """
        Resolve an instance from a binding according to its lifetime.

        Parameters
        ----------
        binding : Binding
            The binding to resolve.
        *args : tuple
            Positional arguments for the constructor.
        **kwargs : dict
            Keyword arguments for the constructor.

        Returns
        -------
        Any
            The resolved instance according to the binding's lifetime.

        Raises
        ------
        OrionisContainerTypeError
            If the binding is not a Binding or the lifetime is unsupported.
        """

    @abstractmethod
    def build(
        self,
        type_: Callable[..., Any],
        *args: tuple,
        **kwargs: dict,
    ) -> type[Any]:
        """
        Build an instance of the given type using auto-resolution.

        Parameters
        ----------
        type_ : Callable[..., Any]
            The class to instantiate.
        *args : tuple
            Positional arguments for the constructor.
        **kwargs : dict
            Keyword arguments for the constructor.

        Returns
        -------
        Any
            The instantiated object.

        Raises
        ------
        OrionisContainerException
            If the type cannot be auto-resolved.

        Notes
        -----
        Returns the created instance if successful. Raises an exception otherwise.
        """

    @abstractmethod
    def call(
        self,
        instance: object,
        method_name: str,
        *args: tuple,
        **kwargs: dict,
    ) -> type[Any]:
        """
        Invoke a method on an instance with automatic dependency injection.

        Parameters
        ----------
        instance : object
            Object instance containing the method.
        method_name : str
            Name of the method to invoke.
        *args : tuple
            Positional arguments for the method.
        **kwargs : dict
            Keyword arguments for the method.

        Returns
        -------
        Any
            Result of the method invocation with dependencies resolved.

        Raises
        ------
        OrionisContainerException
            If the method is not found on the instance.
        OrionisContainerTypeError
            If the attribute is not callable.
        """

    @abstractmethod
    def invoke(
        self,
        fn: Callable,
        *args: tuple,
        **kwargs: dict,
    ) -> type[Any]:
        """
        Invoke a callable with automatic dependency injection.

        Parameters
        ----------
        fn : Callable
            The callable to invoke. Must not be a class or type.
        *args : tuple
            Positional arguments for the callable.
        **kwargs : dict
            Keyword arguments for the callable.

        Returns
        -------
        Any
            Returns the result of the callable execution with dependencies injected.

        Raises
        ------
        OrionisContainerTypeError
            If `fn` is not a callable or is a class/type.
        """

    @abstractmethod
    def resolveDeferredProvider(
        self,
        service: type | str,
    ) -> None:
        """
        Resolve and register the deferred service provider for a given service.

        Parameters
        ----------
        service : type | str
            The service type or fully qualified class name for which to find the
            deferred provider.

        Returns
        -------
        None
            This method does not return any value. Registers the deferred service
            provider in the application container if found.

        Raises
        ------
        TypeError
            If the service parameter is not a type or string.
        """
