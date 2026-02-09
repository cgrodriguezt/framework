from __future__ import annotations
import asyncio
import inspect
import threading
from collections import deque
from typing import TYPE_CHECKING, Any, ClassVar, Self
from orionis.container.context.manager import ScopeManager
from orionis.container.context.scope import ScopedContext
from orionis.container.contracts.container import IContainer
from orionis.container.entities.binding import Binding
from orionis.container.enums.lifetimes import Lifetime
from orionis.container.exceptions import CircularDependencyException
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.callables.reflection import ReflectionCallable
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.services.introspection.modules.engine import ModuleEngine
from orionis.services.introspection.reflection import Reflection

if TYPE_CHECKING:
    from collections.abc import Callable
    from orionis.container.contracts.service_provider import IServiceProvider
    from orionis.services.introspection.dependencies.entities.argument import Argument
    from orionis.services.introspection.dependencies.entities.signature import (
        SignatureArguments,
    )

class Container(IContainer):

    # ruff: noqa: RET505, ANN401, SLF001

    # Dictionary to hold singleton instances for each class
    # This allows proper inheritance of the singleton pattern
    _instances: ClassVar[dict] = {}

    # Lock for thread-safe singleton instantiation and access
    # This lock ensures that only one thread can create or access instances at a time
    _lock = threading.RLock()  # RLock allows reentrant locking

    def __new__(cls) -> Self:
        """
        Create and return a singleton instance for each class in the hierarchy.

        Ensures thread-safe singleton instantiation for each subclass of Container.
        Uses double-checked locking to avoid race conditions and optimize performance.

        Returns
        -------
        Self
            The singleton instance of the calling class.
        """
        # Fast path: check if instance already exists for the class
        if cls in cls._instances:
            return cls._instances[cls]

        # Slow path: acquire lock to ensure thread safety
        with cls._lock:
            # Double-check if instance was created while waiting for the lock
            if cls in cls._instances:
                return cls._instances[cls]

            # Create a new instance using the superclass's __new__ method
            instance = super().__new__(cls)

            # Store the instance in the class-specific dictionary
            cls._instances[cls] = instance

            # Return the newly created singleton instance
            return instance

    def __init__(self) -> None:
        """
        Initialize the internal state of the container.

        Sets up data structures for dependency injection and ensures single
        initialization per instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Prevent multiple initializations for singleton instances
        if not hasattr(self, "_Container__initialized"):
            # Track currently resolving types to detect circular dependencies
            self.__resolution_cache: set[str] = set()
            # Store service bindings
            self.__bindings: dict[Any, Binding] = {}
            # Map aliases to bindings
            self.__aliases: dict[str, Binding] = {}
            # Cache singleton instances
            self.__singleton_cache: dict[str, Any] = {}
            # Cache deferred providers already resolved
            self.__deferred_providers: dict[str, dict[str, str]]= {}
            self.__cache_resolve_deferred_providers: set[Any] = set()
            # Mark this instance as initialized
            self.__initialized = True  # NOSONAR

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
        # Validate that abstract is an abstract class
        if not Reflection.isAbstract(abstract):
            error_msg = (
                "Expected an abstract class extending 'abc.ABC' for 'abstract', but "
                f"got '{abstract.__name__}' which is not an abstract base class."
            )
            raise TypeError(error_msg)

        # Validate that instance is a valid object
        if not Reflection.isInstance(instance):
            error_msg = (
                "Expected a valid instance for 'instance', but got type "
                f"'{type(instance).__name__}' instead."
            )
            raise TypeError(error_msg)

        # Enforce decoupling or subclass relationship as specified
        self.__validateInheritanceDecoupling(
            abstract,
            instance.__class__,
            enforce_decoupling=enforce_decoupling,
        )

        # Ensure all abstract methods are implemented by the instance
        self.__validateAbstractMethodImplementation(
            abstract=abstract,
            instance=instance,
        )

        # Generate and validate the alias key
        alias = self.__generateServiceAlias(abstract, alias)

        # Remove any existing binding for this abstract or alias
        self.drop(abstract, alias)

        # Register the instance with singleton lifetime
        self.__bindings[abstract] = Binding(
            contract=abstract,
            instance=instance,
            lifetime=Lifetime.SINGLETON,
            enforce_decoupling=enforce_decoupling,
            alias=alias,
        )

        # Register the alias for lookup
        self.__aliases[alias] = self.__bindings[abstract]

        # Return True to indicate successful registration
        return True

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
        # Validate that abstract is an abstract class
        if not Reflection.isAbstract(abstract):
            error_msg = (
                f"Expected an abstract class extending 'abc.ABC' for 'abstract', but "
                f"got '{abstract.__name__}' which is not an abstract base class."
            )
            raise TypeError(error_msg)

        # Validate that concrete is a concrete class
        if not Reflection.isConcreteClass(concrete):
            error_msg = (
                f"Expected a concrete class for 'concrete', but got abstract class or "
                f"interface '{concrete.__name__}' instead."
            )
            raise TypeError(error_msg)

        # Enforce decoupling or subclass relationship
        self.__validateInheritanceDecoupling(
            abstract,
            concrete,
            enforce_decoupling=enforce_decoupling,
        )

        # Ensure all abstract methods are implemented
        self.__validateAbstractMethodImplementation(
            abstract=abstract,
            concrete=concrete,
        )

        # Generate and validate the alias key
        alias = self.__generateServiceAlias(abstract, alias)

        # Remove any existing binding for this abstract or alias
        self.drop(abstract, alias)

        # Register the service with transient lifetime
        self.__bindings[abstract] = Binding(
            contract=abstract,
            concrete=concrete,
            lifetime=Lifetime.TRANSIENT,
            enforce_decoupling=enforce_decoupling,
            alias=alias,
        )

        # Register the alias for lookup
        self.__aliases[alias] = self.__bindings[abstract]

        # Registration successful
        return True

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
        # Validate that abstract is an abstract class
        if not Reflection.isAbstract(abstract):
            error_msg = (
                "Expected an abstract class extending 'abc.ABC' for 'abstract', but "
                f"got '{abstract.__name__}' which is not an abstract base class."
            )
            raise TypeError(error_msg)

        # Validate that concrete is a concrete class
        if not Reflection.isConcreteClass(concrete):
            error_msg = (
                "Expected a concrete class for 'concrete', but got abstract class or "
                f"interface '{concrete.__name__}' instead."
            )
            raise TypeError(error_msg)

        # Enforce decoupling or subclass relationship
        self.__validateInheritanceDecoupling(
            abstract,
            concrete,
            enforce_decoupling=enforce_decoupling,
        )

        # Ensure all abstract methods are implemented
        self.__validateAbstractMethodImplementation(
            abstract=abstract,
            concrete=concrete,
        )

        # Generate and validate the alias key
        alias = self.__generateServiceAlias(abstract, alias)

        # Remove any existing binding for this abstract or alias
        self.drop(abstract, alias)

        # Register the service with singleton lifetime
        self.__bindings[abstract] = Binding(
            contract=abstract,
            concrete=concrete,
            lifetime=Lifetime.SINGLETON,
            enforce_decoupling=enforce_decoupling,
            alias=alias,
        )

        # Register the alias for lookup
        self.__aliases[alias] = self.__bindings[abstract]

        # Registration successful
        return True

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
        # Validate that abstract is an abstract class
        if not Reflection.isAbstract(abstract):
            error_msg = (
                f"Expected an abstract class extending 'abc.ABC' for 'abstract', but "
                f"got '{abstract.__name__}' which is not an abstract base class."
            )
            raise TypeError(error_msg)

        # Validate that concrete is a concrete class
        if not Reflection.isConcreteClass(concrete):
            error_msg = (
                f"Expected a concrete class for 'concrete', but got abstract class or "
                f"interface '{concrete.__name__}' instead."
            )
            raise TypeError(error_msg)

        # Enforce decoupling or subclass relationship
        self.__validateInheritanceDecoupling(
            abstract,
            concrete,
            enforce_decoupling=enforce_decoupling,
        )

        # Ensure all abstract methods are implemented
        self.__validateAbstractMethodImplementation(
            abstract=abstract,
            concrete=concrete,
        )

        # Generate and validate the alias key
        alias = self.__generateServiceAlias(abstract, alias)

        # Remove any existing binding for this abstract or alias
        self.drop(abstract, alias)

        # Register the service with scoped lifetime
        self.__bindings[abstract] = Binding(
            contract=abstract,
            concrete=concrete,
            lifetime=Lifetime.SCOPED,
            enforce_decoupling=enforce_decoupling,
            alias=alias,
        )

        # Register the alias for lookup
        self.__aliases[alias] = self.__bindings[abstract]

        # Return True to indicate successful registration
        return True

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
        # Track if any deletion occurred for abstract or alias
        deleted: bool = False

        # Remove registration by abstract type if provided
        if abstract is not None:
            deleted = self.__removeAbstractRegistration(abstract)

        # Remove registration by alias if provided
        if alias is not None:
            deleted = self.__removeAliasRegistration(alias) or deleted

        # Return True if any deletion occurred, else False
        return deleted

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
        # Validate that abstract is an abstract class
        if not Reflection.isAbstract(abstract):
            error_msg = (
                "Expected an abstract class extending 'abc.ABC' for 'abstract', but "
                f"got '{abstract.__name__}' which is not an abstract base class."
            )
            raise TypeError(error_msg)

        # Validate that instance is a valid object
        if not Reflection.isInstance(instance):
            error_msg = (
                f"Instance of type '{instance.__class__.__name__}' is not a valid "
                f"implementation of the abstract class '{abstract.__name__}'."
            )
            raise TypeError(error_msg)

        # Enforce decoupling or subclass relationship as specified
        self.__validateInheritanceDecoupling(
            abstract,
            instance.__class__,
            enforce_decoupling=enforce_decoupling,
        )

        # Ensure all abstract methods are implemented by the instance
        self.__validateAbstractMethodImplementation(
            abstract=abstract,
            instance=instance,
        )

        # Generate and validate the alias key (either provided or default)
        alias = self.__generateServiceAlias(abstract, alias)

        # Remove any existing binding for this abstract or alias
        self.drop(abstract, alias)

        # Register the instance with scoped lifetime in the container bindings
        self.__bindings[abstract] = Binding(
            contract=abstract,
            instance=instance,
            lifetime=Lifetime.SCOPED,
            enforce_decoupling=enforce_decoupling,
            alias=alias,
        )

        # Register the alias for lookup
        self.__aliases[alias] = self.__bindings[abstract]

        # Store the instance directly in the current scope, if a scope is active
        scope = ScopedContext.getCurrentScope()
        if scope:
            # Store instance under both abstract and alias keys in the scope
            scope[abstract] = instance
            scope[alias] = instance

        # Return True to indicate successful registration
        return True

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
        # Try to find the binding by abstract type in the main bindings dictionary
        binding = self.__bindings.get(abstract_or_alias)

        # If not found, try to find the binding by alias in the aliases dictionary
        if binding is None:
            binding = self.__aliases.get(abstract_or_alias)

        # Return the found binding or None
        return binding

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
        # Check existence in bindings dictionary
        in_bindings: bool = abstract_or_alias in self.__bindings

        # Check existence in aliases dictionary
        in_aliases: bool = abstract_or_alias in self.__aliases

        # Return True if found in either dictionary
        return in_bindings or in_aliases

    def __removeAbstractRegistration(
        self,
        abstract: Callable[..., Any],
    ) -> bool:
        """
        Remove all registrations and cache entries for an abstract type.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract class or interface to remove.

        Returns
        -------
        bool
            True if any registration was removed, False otherwise.

        Notes
        -----
        Cleans up bindings, aliases, singleton cache, and resolution cache for the
        abstract type.
        """
        # Track if any deletion occurred for the abstract type
        deleted: bool = False

        # Remove binding for the abstract type if present
        if abstract in self.__bindings:
            del self.__bindings[abstract]
            deleted = True

        # Remove the default alias for the abstract type if present
        abs_alias: str = ReflectionAbstract(abstract).getModuleWithClassName()
        if abs_alias in self.__aliases:
            del self.__aliases[abs_alias]
            deleted = True

        # Remove singleton cache entry for the abstract type if present
        if abstract in self.__singleton_cache:
            del self.__singleton_cache[abstract]
            deleted = True

        # Remove from resolution cache
        self.__resolution_cache.discard(abs_alias)

        # Return True if any deletion occurred, else False
        return deleted

    def __removeAliasRegistration(
        self,
        alias: str | None = None,
    ) -> bool:
        """
        Remove all registrations and cache entries for a given alias.

        Parameters
        ----------
        alias : str | None
            Alias to remove from the container.

        Returns
        -------
        bool
            True if any registration was removed, otherwise False.

        Notes
        -----
        Cleans up bindings, aliases, singleton cache, and resolution cache for
        the alias.
        """
        deleted: bool = False

        # Remove alias from aliases dictionary if present
        if alias in self.__aliases:
            del self.__aliases[alias]
            deleted = True

        # Remove binding for alias if present
        if alias in self.__bindings:
            del self.__bindings[alias]
            deleted = True

        # Remove singleton cache entry for alias if present
        if alias in self.__singleton_cache:
            del self.__singleton_cache[alias]
            deleted = True

        # Remove alias from resolution cache
        self.__resolution_cache.discard(alias)
        return deleted

    def __generateServiceAlias(
        self,
        abstract: Callable[..., Any],
        alias: str | None = None,
    ) -> str:
        """
        Generate and validate a service alias for registration.

        Parameters
        ----------
        abstract : Callable[..., Any]
            Abstract base class or interface for alias generation.
        alias : str | None, optional
            Custom alias string.

        Returns
        -------
        str
            Validated custom alias or a default alias in the format
            'module.ClassName'.

        Raises
        ------
        TypeError
            If the alias is invalid.
        """
        # Return default alias if no custom alias is provided
        if not alias:
            return f"{abstract.__module__}.{abstract.__name__}"

        # Validate alias type and content
        if not isinstance(alias, str) or not alias or alias.isspace():
            error_msg = (
                "Alias must be a non-empty string without only whitespace."
            )
            raise TypeError(error_msg)

        # Check for invalid characters in alias
        if set(alias) & set(
            ' \t\n\r\x0b\x0c!@#$%^&*()[]{};:,/<>?\\|`~"\'',
        ):
            error_msg = (
                f"Alias '{alias}' contains invalid characters."
            )
            raise TypeError(error_msg)

        # Return stripped alias
        return alias.strip()

    def __validateInheritanceDecoupling(
        self,
        abstract: Callable[..., Any],
        concrete: Callable[..., Any],
        *,
        enforce_decoupling: bool,
    ) -> None:
        """
        Validate inheritance or decoupling between abstract and concrete classes.

        Parameters
        ----------
        abstract : Callable[..., Any]
            Abstract base class or interface.
        concrete : Callable[..., Any]
            Concrete implementation class.
        enforce_decoupling : bool
            If True, concrete must not inherit from abstract. If False, concrete must
            inherit from abstract.

        Returns
        -------
        None
            Raises a TypeError if the inheritance relationship does not match the
            decoupling requirement. Otherwise, returns None.

        Raises
        ------
        TypeError
            If inheritance relationship does not match the decoupling requirement.
        """
        # Enforce decoupling: concrete must not inherit from abstract
        if enforce_decoupling:
            if issubclass(concrete, abstract):
                error_msg = (
                    "Concrete class must not inherit from the abstract class."
                )
                raise TypeError(error_msg)
        # Require inheritance: concrete must inherit from abstract
        elif not issubclass(concrete, abstract):
            error_msg = (
                "Concrete class must inherit from the abstract class."
            )
            raise TypeError(error_msg)

    def __validateAbstractMethodImplementation(
        self,
        *,
        abstract: Callable[..., Any] | None = None,
        concrete: Callable[..., Any] | None = None,
        instance: type[Any] | None = None,
    ) -> None:
        """
        Validate that all abstract methods are implemented by the target.

        Parameters
        ----------
        abstract : Callable[..., Any] | None
            Abstract base class containing abstract methods.
        concrete : Callable[..., Any] | None
            Concrete class to check for method implementation.
        instance : type[Any] | None
            Instance to check for method implementation.

        Returns
        -------
        None
            Raises an exception if required methods are not implemented.

        Raises
        ------
        ValueError
            If abstract class is not provided.
        TypeError
            If abstract class has no abstract methods or target is not provided.
            If required methods are not implemented.
        """
        # Ensure the abstract class is provided
        if abstract is None:
            error_msg = (
                "Abstract class must be provided for implementation check."
            )
            raise ValueError(error_msg)

        # Get reflection for the abstract class
        rf_abstract: ReflectionAbstract = ReflectionAbstract(abstract)

        # Get all abstract methods to be implemented
        abstract_methods: list[str] = rf_abstract.getMethods()
        if not abstract_methods:
            error_msg = (
                f"Abstract class '{abstract.__name__}' has no abstract methods."
            )
            raise TypeError(error_msg)

        # Select the target class or instance for validation
        target: Callable[..., Any] | type[Any] | None = (
            concrete if concrete is not None else instance
        )
        if target is None:
            error_msg = (
                "Either concrete class or instance must be provided for "
                "implementation check."
            )
            raise TypeError(error_msg)

        # Get the actual class type from the target
        target_class: Callable[..., Any] = (
            target if Reflection.isClass(target) else target.__class__
        )

        # Get reflection for the concrete class
        rf_class: ReflectionConcrete = ReflectionConcrete(target_class)

        # Get class names for error reporting
        target_name: str = rf_class.getClassName()
        abstract_name: str = rf_abstract.getClassName()

        # Get all methods implemented by the target class
        implemented_methods: list[str] = rf_class.getMethods()

        # Check for missing implementations
        not_implemented: list[str] = [
            method for method in abstract_methods
            if method not in implemented_methods
        ]

        # Raise exception if any abstract methods are not implemented
        if not_implemented:
            methods: str = ", ".join(not_implemented)
            error_msg = (
                f"Class '{target_name}' must implement the following abstract "
                f"methods from '{abstract_name}': {methods}"
            )
            raise TypeError(error_msg)

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
        # Instantiate and return a new ScopeManager for scoped service management
        return ScopeManager()

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
        # Compute fully qualified service path with single type check
        if isinstance(service, str):
            service_full_path: str = service
        else:
            # Assume it's a type if not string
            service_full_path: str = f"{service.__module__}.{service.__name__}"

        # Fast path: exit early if already resolved or built-in
        if (
            service_full_path in self.__cache_resolve_deferred_providers or
            service_full_path.startswith("builtins.")
        ):
            return

        # Lazy load deferred providers only when needed
        if not self.__deferred_providers:
            self.__deferred_providers = self.getDeferredProviders()

        # Attempt to retrieve provider info for the given service
        provider_metadata = self.__deferred_providers.get(service_full_path)
        if provider_metadata is None:
            return

        # Mark as resolved immediately to prevent duplicate processing
        self.__cache_resolve_deferred_providers.add(service_full_path)

        # Cache the resolved class to avoid repeated resolution
        provider_class = ModuleEngine.resolveClass(metadata=provider_metadata)

        # Build and register the provider instance
        instance: IServiceProvider = await self.build(provider_class)
        instance.register()

        # Boot the provider instance - check if coroutine function
        if asyncio.iscoroutinefunction(instance.boot):
            await instance.boot()
        else:
            instance.boot()

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
        # Resolve any deferred providers for the given type
        await self.resolveDeferredProvider(type_)

        # Check if the type can be auto-resolved by the container
        if not self.__canAutoResolveClass(type_):
            error_msg = (
                f"Type '{getattr(type_, '__name__', str(type_))}' cannot be "
                "auto-resolved by the container."
            )
            raise TypeError(error_msg)

        # Attempt to auto-resolve the type with provided arguments
        return await self.__autoResolveClass(type_, *args, **kwargs)

    async def __autoResolveClass(
        self,
        type_: Callable[..., Any],
        *args: tuple,
        **kwargs: dict,
    ) -> type[Any]:
        """
        Automatically resolve and instantiate a class, injecting dependencies.

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
            Instantiated object with dependencies resolved.

        Raises
        ------
        CircularDependencyException
            If a circular dependency is detected.
        Exception
            If the type cannot be auto-resolved.
        """
        # Create a unique key for circular dependency tracking
        type_key = f"{type_.__module__}.{type_.__name__}"

        # Check for circular dependency
        if type_key in self.__resolution_cache:
            error_msg = (
                f"Circular dependency detected while resolving argument '{type_key}'."
            )
            raise CircularDependencyException(error_msg)

        try:
            # Mark type as being resolved
            self.__resolution_cache.add(type_key)

            # Get constructor dependencies using reflection
            dependencies = ReflectionConcrete(type_).constructorSignature()

            # If no dependencies, instantiate directly
            if dependencies.hasNoDependencies():
                return type_(*args, **kwargs)

            # Resolve dependencies recursively
            final_args, final_kwargs = await self.__resolveSignature(
                dependencies, *args, **kwargs,
            )

            # Instantiate with resolved arguments
            return type_(*final_args, **final_kwargs)

        finally:

            # Clean up resolution cache
            self.__resolution_cache.discard(type_key)

    async def __resolveSignature( # NOSONAR
        self,
        arguments: SignatureArguments,
        *args: tuple,
        **kwargs: dict,
    ) -> tuple[list[Any], dict[str, Any]]:
        """
        Resolve constructor or callable arguments using provided values and container.

        Parameters
        ----------
        arguments : SignatureArguments
            Signature object containing argument metadata.
        *args : Any
            Positional arguments for the target.
        **kwargs : Any
            Keyword arguments for the target.

        Returns
        -------
        tuple[list[Any], dict[str, Any]]
            Tuple containing resolved positional and keyword arguments.
        """
        # Copy kwargs to avoid mutating the original dictionary
        remaining_kwargs: dict[str, Any] = dict(kwargs)

        # Use deque for efficient positional argument handling
        positional: deque[Any] = deque(args)

        # Prepare containers for resolved arguments
        final_args: list[Any] = []
        final_kwargs: dict[str, Any] = {}

        # Iterate over arguments in definition order
        for name, dep in arguments.items():

            # Check if the argument is keyword-only
            is_keyword_only: bool = dep.is_keyword_only

            # Handle positional or positional-or-keyword arguments
            if not is_keyword_only:

                # Resolve from container by type if bound and not provided as keyword
                if self.bound(dep.type) and name not in remaining_kwargs:
                    final_args.append(
                        await self.resolve(
                            self.getBinding(dep.type),
                        ),
                    )
                    continue

                # Resolve from container by full class path if bound and not provided
                if self.bound(dep.full_class_path) and name not in remaining_kwargs:
                    final_args.append(
                        await self.resolve(
                            self.getBinding(dep.full_class_path),
                        ),
                    )
                    continue

                # Use next positional argument if available
                if positional:
                    value = positional.popleft()
                    final_args.append(value)
                    continue

                # Use provided keyword argument if available
                if name in remaining_kwargs:
                    final_args.append(remaining_kwargs[name])
                    del remaining_kwargs[name]
                    continue

                # Fallback to automatic resolution if no explicit value
                final_args.append(
                    await self.__resolveArgument(dep),
                )

            else:

                # Use provided keyword argument if available
                if name in remaining_kwargs:
                    final_kwargs[name] = remaining_kwargs[name]
                    del remaining_kwargs[name]
                    continue

                # Resolve keyword-only argument from container by type
                if self.bound(dep.type):
                    final_kwargs[name] = await self.resolve(
                        self.getBinding(dep.type),
                    )
                    continue

                # Resolve keyword-only argument from container by full class path
                if self.bound(dep.full_class_path):
                    final_kwargs[name] = await self.resolve(
                        self.getBinding(dep.full_class_path),
                    )
                    continue

                # Fallback to automatic resolution for keyword-only argument
                final_kwargs[name] = await self.__resolveArgument(dep)

        # Append any remaining positional arguments
        final_args.extend(positional)

        # Add any remaining unused keyword arguments
        final_kwargs.update(remaining_kwargs)

        # Return resolved positional and keyword arguments
        return final_args, final_kwargs

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
        # Validate binding type
        if not isinstance(binding, Binding):
            error_msg = (
                f"Expected a Binding instance, got {type(binding).__name__}"
            )
            raise TypeError(error_msg)

        # Resolve based on the lifetime type
        if binding.lifetime == Lifetime.TRANSIENT:
            # Always create a new instance for transient lifetime
            return await self.__resolveTransient(binding, *args, **kwargs)

        if binding.lifetime == Lifetime.SINGLETON:
            # Return cached instance or create one for singleton lifetime
            return await self.__resolveSingleton(binding, *args, **kwargs)

        if binding.lifetime == Lifetime.SCOPED:
            # Return instance from current scope or create one for scoped lifetime
            return await self.__resolveScoped(binding, *args, **kwargs)

        # Raise exception for unsupported lifetime types
        error_msg = (
            f"Unsupported lifetime '{binding.lifetime}' for binding "
            f"'{binding.contract or binding.alias}'."
        )
        raise TypeError(error_msg)

    async def __resolveTransient(
        self,
        binding: Binding,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> Any:
        """
        Resolve and instantiate a service with transient lifetime.

        Parameters
        ----------
        binding : Binding
            The binding to resolve.
        *args : tuple[Any, ...]
            Positional arguments for the constructor or callable.
        **kwargs : dict[str, Any]
            Keyword arguments for the constructor or callable.

        Returns
        -------
        Any
            A new instance of the requested service.

        Raises
        ------
        TypeError
            If no concrete class or function is defined for the binding.
        """
        # Instantiate if a concrete class is defined
        if binding.concrete:
            return await self.__autoResolveClass(binding.concrete, *args, **kwargs)

        # Raise if neither is defined
        error_msg = (
            "Cannot resolve transient binding for "
            f"'{binding.contract or binding.alias}': no concrete class or "
            "function defined."
        )
        raise TypeError(error_msg)

    async def __resolveSingleton(
        self,
        binding: Binding,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> Any:
        """
        Resolve and return a singleton instance for the given binding.

        Parameters
        ----------
        binding : Binding
            The binding to resolve.
        *args : tuple[Any, ...]
            Positional arguments for the constructor, used if instance does not exist.
        **kwargs : dict[str, Any]
            Keyword arguments for the constructor, used if instance does not exist.

        Returns
        -------
        Any
            The singleton instance associated with the binding. If already cached,
            returns the cached instance. If not, creates and caches the instance.

        Raises
        ------
        TypeError
            If no concrete class, instance, or function is defined for the binding.
        """
        # Return cached singleton instance if available
        if binding.alias in self.__singleton_cache:
            return self.__singleton_cache[binding.alias]

        # Cache and return pre-registered instance if present
        if binding.instance is not None:
            self.__singleton_cache[binding.alias] = binding.instance
            return self.__singleton_cache[binding.alias]

        # Create and cache instance if concrete class is specified
        if binding.concrete:
            instance = await self.__autoResolveClass(binding.concrete, *args, **kwargs)
            self.__singleton_cache[binding.alias] = instance
            return instance

        # Raise exception if binding cannot be resolved
        error_msg = (
            f"Cannot resolve singleton binding for "
            f"'{binding.contract or binding.alias}': no concrete class or "
            "instance defined."
        )
        raise TypeError(error_msg)

    async def __resolveScoped(
        self,
        binding: Binding,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> Any:
        """
        Resolve a service registered with scoped lifetime.

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
            The resolved instance from the current scope. Raises RuntimeError if
            no scope is active, or TypeError if no implementation or instance is
            defined.

        Raises
        ------
        RuntimeError
            If there is no active scope for scoped services.
        TypeError
            If no concrete class or instance is defined for the binding.
        """
        # Retrieve the current scope context for scoped lifetime resolution
        scope = ScopedContext.getCurrentScope()

        # Raise if there is no active scope
        if scope is None:
            error_msg = (
                f"No active scope for scoped service '{binding.alias}'. "
                "Use 'with Application.beginScope()' to create a scope context."
            )
            raise RuntimeError(error_msg)

        # Return the instance if already present in the scope by contract
        if binding.contract in scope:
            return scope[binding.contract]

        # Return the instance if already present in the scope by alias
        if binding.alias in scope:
            return scope[binding.alias]

        # Create and store a new instance in the scope if not present
        if binding.concrete:
            instance = await self.__autoResolveClass(
                binding.concrete, *args, **kwargs,
            )
            scope[binding.contract] = instance
            scope[binding.alias] = instance
            return scope[binding.contract]

        # Raise if no implementation or instance is defined
        error_msg = (
            f"Cannot resolve scoped binding for '{binding.contract or binding.alias}': "
            "no implementation or instance defined."
        )
        raise TypeError(error_msg)

    async def __resolveArgument(
        self,
        argument: Argument,
    ) -> type[Any]:
        """
        Resolve a single argument dependency for auto-resolution.

        Parameters
        ----------
        argument : Argument
            The argument dependency to resolve.

        Returns
        -------
        Any
            The resolved instance or value for the argument.

        Raises
        ------
        Exception
            If the argument cannot be resolved.

        Notes
        -----
        Handles resolution from scope, container, or by default value.
        """
        # Resolve any deferred providers.
        await self.resolveDeferredProvider(argument.type)

        # List of modules that cannot be auto-resolved
        special_modules: list[str] = ["typing", "builtins"]

        # Check if argument is resolved in the current scope
        scoped = ScopedContext.getCurrentScope()
        if scoped is not None:
            if argument.type in scoped:
                return scoped[argument.type]
            elif argument.full_class_path in scoped:
                return scoped[argument.full_class_path]

        # Return default value for resolved arguments from
        # special modules or with default
        if (
            argument.default is not inspect._empty and
            ((argument.resolved and argument.module_name in special_modules)
            or (argument.resolved and argument.default is not None))
        ):
            return argument.default

        # Raise for unresolvable built-in or typing types
        if not argument.resolved and argument.module_name in special_modules:
            error_msg = (
                f"Cannot resolve '{argument.name}' of type '{argument.module_name}'. "
                "Provide a default value."
            )
            raise TypeError(error_msg)

        # Attempt resolution using the argument type if bound in container
        if self.bound(argument.type):
            return await self.resolve(
                self.getBinding(argument.type),
            )

        # Attempt resolution using the full class path if bound in container
        if self.bound(argument.full_class_path):
            return await self.resolve(
                self.getBinding(argument.full_class_path),
            )

        # Try auto-resolution if the type is eligible
        if self.__canAutoResolveClass(argument.type):
            return await self.__autoResolveClass(argument.type)

        # Raise if all resolution methods fail
        error_msg = (
            f"Cannot resolve '{argument.name}' of type '{argument.module_name}'. "
            "Provide a default value."
        )
        raise RuntimeError(error_msg)

    def __canAutoResolveClass(
        self,
        type_: Callable[..., Any],
    ) -> bool:
        """
        Check if a type can be automatically resolved by the container.

        Parameters
        ----------
        type_ : Callable[..., Any]
            The type to check for auto-resolution eligibility.

        Returns
        -------
        bool
            True if the type can be auto-resolved, False otherwise.

        Notes
        -----
        Returns True only if the type is a concrete class and not defined in
        '__main__'.
        """
        # Check if the type is a concrete class (not abstract or interface)
        if not Reflection.isConcreteClass(type_):
            return False

        # Exclude types defined in the '__main__' module from auto-resolution
        return type_.__module__ != "__main__"

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
        # Ensure the provided function is callable and not a class/type
        if not callable(fn) or isinstance(fn, type):
            error_msg = (
                f"Provided fn '{getattr(fn, '__name__', str(fn))}' must be a "
                "function or callable, not a class/type."
            )
            raise TypeError(error_msg)

        # Resolve dependencies and execute the callable
        return await self.__autoResolveCallable(fn, *args, **kwargs)

    async def __autoResolveCallable(
        self,
        type_: Callable[..., Any],
        *args: tuple,
        **kwargs: dict,
    ) -> type[Any]:
        """
        Resolve and invoke a callable, injecting dependencies.

        Parameters
        ----------
        type_ : Callable[..., Any]
            The callable to invoke.
        *args : tuple
            Positional arguments for the callable.
        **kwargs : dict
            Keyword arguments for the callable.

        Returns
        -------
        Any
            The result of the callable invocation.

        Raises
        ------
        OrionisContainerCircularDependencyException
            If a circular dependency is detected.
        Exception
            If the callable cannot be auto-resolved.
        """
        # Get callable dependencies using reflection
        dependencies = ReflectionCallable(type_).getDependencies()

        # If no dependencies, invoke directly
        if dependencies.hasNoDependencies():
            return await self.__callAndResolve(type_, *args, **kwargs)

        # Resolve dependencies recursively
        final_args, final_kwargs = await self.__resolveSignature(
            dependencies, *args, **kwargs,
        )

        # Invoke the callable with resolved arguments
        return await self.__callAndResolve(type_, *final_args, **final_kwargs)

    async def __callAndResolve(
        self,
        func: Callable[..., Any],
        *args: tuple,
        **kwargs: dict,
    ) -> Any:
        """
        Execute a function or coroutine with provided arguments.

        Parameters
        ----------
        func : Callable[..., Any]
            Function or coroutine to execute.
        *args : tuple
            Positional arguments for the function.
        **kwargs : dict
            Keyword arguments for the function.

        Returns
        -------
        Any
            Result of the function or coroutine execution.

        Raises
        ------
        RuntimeError
            If an async function is called without an event loop.
        """
        # Check if the function is a coroutine and await if necessary
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        return func(*args, **kwargs)

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
        # Resolve deferred providers for the given type if necessary
        await self.resolveDeferredProvider(type_)

        # Attempt to resolve from registered bindings
        if self.bound(type_):
            return await self.resolve(
                self.getBinding(type_),
                *args,
                **kwargs,
            )

        # Attempt auto-resolution for classes not registered
        if isinstance(type_, type):
            return await self.build(
                type_,
                *args,
                **kwargs,
            )

        # Raise if resolution fails
        error_msg = (
            f"Cannot resolve service '{getattr(type_, '__name__', str(type_))}': "
            "it is not registered in the container and cannot be auto-resolved. "
            "Please ensure the service is registered or provide all required "
            "dependencies."
        )
        raise TypeError(error_msg)

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
        # Retrieve the method from the instance by name
        method = getattr(instance, method_name, None)

        # Check if the method exists
        if method is None:
            error_msg = (
                f"Method '{method_name}' not found in instance of type "
                f"'{type(instance).__name__}'."
            )
            raise AttributeError(error_msg)

        # Ensure the attribute is callable
        if not callable(method):
            error_msg = (
                f"Attribute '{method_name}' of instance "
                f"'{type(instance).__name__}' is not callable."
            )
            raise TypeError(error_msg)

        # Invoke the method with automatic dependency resolution
        return await self.__autoResolveCallable(method, *args, **kwargs)
