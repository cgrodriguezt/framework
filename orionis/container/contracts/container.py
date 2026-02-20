from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from collections.abc import Callable
    from orionis.container.context.manager import ScopeManager
    from orionis.container.entities.binding import Binding

class IContainer(ABC):

    # ruff: noqa: ANN401

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

        Parameters
        ----------
        abstract : Callable[..., Any]
            Abstract class or interface to associate with the instance.
        instance : type[Any]
            Concrete instance to register.
        alias : str | None, optional
            Alias to register the instance under. If not provided, a default alias is
            generated.
        enforce_decoupling : bool, optional
            If True, instance's class must not inherit from abstract. If False, must
            inherit.

        Returns
        -------
        bool | None
            True if registration succeeds, None otherwise.

        Raises
        ------
        TypeError
            If abstract is not an abstract class or instance is not valid.
        Exception
            If decoupling check fails or abstract methods are not implemented.
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
        TypeError
            If type validation fails.
        Exception
            If decoupling or implementation checks fail.

        Notes
        -----
        Each resolution creates a new instance. Validates types, decoupling,
        and abstract method implementation. Manages aliases.
        """

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

        Parameters
        ----------
        abstract : Callable[..., Any]
            Abstract base class or interface to bind.
        concrete : Callable[..., Any]
            Concrete class to associate.
        alias : str | None, optional
            Custom alias for registration.
        enforce_decoupling : bool, optional
            If True, concrete must not inherit from abstract.

        Returns
        -------
        bool | None
            True if registration succeeds, None if an exception occurs.

        Raises
        ------
        TypeError
            If type validation fails.
        Exception
            If decoupling or implementation checks fail.

        Notes
        -----
        Validates types, enforces decoupling, and ensures abstract methods are
        implemented. Removes previous bindings for the same abstract or alias.
        Registers the concrete implementation to the abstract type with singleton
        lifetime.
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
        TypeError
            If type validation fails.
        Exception
            If decoupling or implementation checks fail.

        Notes
        -----
        Each scope context creates a new instance. Validates types, enforces
        decoupling, checks abstract method implementation, and manages aliases.
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
        abstract : Callable[..., Any] | None
            The abstract class or interface to remove from the container.
        alias : str | None
            The alias to remove from the container.

        Returns
        -------
        bool
            True if any registration was removed, otherwise False.

        Notes
        -----
        Cleans up bindings, aliases, singleton cache, and resolution cache.
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
        TypeError
            If abstract is not an abstract class or alias is invalid.
        Exception
            If instance is not valid, fails decoupling, or no scope is active.

        Notes
        -----
        Registers the instance with scoped lifetime, available only in the current
        scope. Removes any previous binding for the same abstract or alias.
        """

    @abstractmethod
    def scopedInstanceWithoutContract(
        self,
        instance: object,
        *,
        alias: str | None = None,
    ) -> bool:
        """
        Register an unbound instance with scoped lifetime.

        Parameters
        ----------
        instance : object
            Instance to register in the current scope.
        alias : str | None, optional
            Alias under which to register the instance. If None, a default alias is
            generated from the instance's module and class name.

        Returns
        -------
        bool
            True if registration succeeds, otherwise raises an exception.

        Raises
        ------
        TypeError
            If the instance is not valid or the alias is invalid.
        Exception
            If there is no active scope for registration.
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
            The abstract class, interface, or alias to look up.

        Returns
        -------
        Binding | None
            The associated binding if found, otherwise None.

        Notes
        -----
        Looks up the binding first in the main bindings dictionary, then in the
        aliases dictionary if not found.
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
            The abstract class, interface, or alias to check for registration.

        Returns
        -------
        bool
            True if the service is registered in bindings or aliases, False otherwise.

        Notes
        -----
        Checks both bindings and aliases dictionaries for existence.
        """

    @abstractmethod
    def beginScope(self) -> ScopeManager:
        """
        Begin a new scope context manager for scoped services.

        Parameters
        ----------
        self : Container
            The container instance.

        Returns
        -------
        ScopeManager
            Context manager for managing the lifecycle of scoped services.
        """

    @abstractmethod
    def getCurrentScope(self) -> dict[Any, Any] | None:
        """
        Get the current active scope context for scoped services.

        Parameters
        ----------
        self : Container
            The container instance.

        Returns
        -------
        dict[Any, Any] | None
            The current active scope context if available, otherwise None.
            The scope context is a dictionary-like object that contains
            instances of scoped services registered in the current scope.

        Notes
        -----
        Returns None if there is no active scope. Use `beginScope()` to create
        a new scope context before accessing scoped services.
        """

    @abstractmethod
    async def resolveDeferredProvider(
        self,
        service: type[Any] | str,
    ) -> None:
        """
        Resolve and register deferred service provider for a given service.

        Parameters
        ----------
        service : type[Any] | str
            The service type or fully qualified class name for which to find the
            deferred provider.

        Returns
        -------
        None
            This method does not return a value. Registers the deferred service
            provider in the application container if found.

        Notes
        -----
        Loads and registers a deferred provider for the specified service.
        Returns early if provider is already resolved or is a built-in.
        """

    @abstractmethod
    async def build(
        self,
        type_: Callable[..., Any],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> Any:
        """
        Build an instance of the specified type using auto-resolution.

        Parameters
        ----------
        type_ : Callable[..., Any]
            The class to instantiate.
        *args : tuple[Any, ...]
            Positional arguments for the constructor.
        **kwargs : dict[str, Any]
            Keyword arguments for the constructor.

        Returns
        -------
        Any
            The instantiated object of the specified type.

        Raises
        ------
        TypeError
            If the type cannot be auto-resolved by the container.

        Notes
        -----
        Resolves deferred providers before attempting instantiation.
        """

    @abstractmethod
    async def resolve(
        self,
        binding: Binding,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> Any:
        """
        Resolve an instance from a binding according to its lifetime.

        Parameters
        ----------
        binding : Binding
            The binding to resolve.
        *args : tuple[Any, ...]
            Positional arguments for the constructor.
        **kwargs : dict[str, Any]
            Keyword arguments for the constructor.

        Returns
        -------
        Any
            The resolved instance according to the binding's lifetime.

        Raises
        ------
        TypeError
            If the binding is not a Binding or the lifetime is unsupported.
        """

    @abstractmethod
    async def invoke(
        self,
        fn: Callable[..., Any],
        *args: tuple,
        **kwargs: dict,
    ) -> Any:
        """
        Invoke a callable with automatic dependency injection.

        Parameters
        ----------
        fn : Callable[..., Any]
            The callable to invoke. Must not be a class or type.
        *args : tuple
            Positional arguments for the callable.
        **kwargs : dict
            Keyword arguments for the callable.

        Returns
        -------
        Any
            The result of the callable execution with dependencies injected.

        Raises
        ------
        TypeError
            If `fn` is not a callable or is a class/type.
        """

    @abstractmethod
    async def make(
        self,
        type_: type[Any],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> Any:
        """
        Resolve and instantiate a service or type.

        Parameters
        ----------
        type_ : type[Any]
            The abstract type, class, or alias to resolve.
        *args : tuple[Any, ...]
            Positional arguments for the constructor or factory.
        **kwargs : dict[str, Any]
            Keyword arguments for the constructor or factory.

        Returns
        -------
        Any
            The resolved and instantiated object.

        Raises
        ------
        TypeError
            If the type cannot be resolved by the container.
        """

    @abstractmethod
    async def call(
        self,
        instance: object,
        method_name: str,
        *args: tuple,
        **kwargs: dict,
    ) -> Any:
        """
        Invoke a method on an object instance with automatic dependency injection.

        Parameters
        ----------
        instance : object
            The object instance containing the method.
        method_name : str
            The name of the method to invoke.
        *args : tuple
            Positional arguments for the method.
        **kwargs : dict
            Keyword arguments for the method.

        Returns
        -------
        Any
            The result of the method invocation with dependencies resolved.

        Raises
        ------
        AttributeError
            If the method is not found on the instance.
        TypeError
            If the attribute is not callable.
        """
