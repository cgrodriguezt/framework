from __future__ import annotations
import asyncio
import concurrent.futures
import threading
from collections import deque
from typing import Any, Callable, TYPE_CHECKING, ClassVar, Self
from orionis.container.context.manager import ScopeManager
from orionis.container.context.scope import ScopedContext
from orionis.container.contracts.container import IContainer
from orionis.container.entities.binding import Binding
from orionis.container.enums.lifetimes import Lifetime
from orionis.container.exceptions import (
    OrionisContainerCircularDependencyException,
    OrionisContainerException,
)
from orionis.container.exceptions.container import OrionisContainerTypeError
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.callables.reflection import ReflectionCallable
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.services.introspection.reflection import Reflection
if TYPE_CHECKING:
    from orionis.services.introspection.dependencies.entities.argument import Argument
    from orionis.services.introspection.dependencies.entities.signature import (
        SignatureArguments,
    )

class Container(IContainer):

    # Dictionary to hold singleton instances for each class
    # This allows proper inheritance of the singleton pattern
    _instances: ClassVar[dict] = {}

    # Lock for thread-safe singleton instantiation and access
    # This lock ensures that only one thread can create or access instances at a time
    _lock = threading.RLock()  # RLock allows reentrant locking

    def __new__(cls) -> Self:
        """
        Create and return a singleton instance for each class in the hierarchy.

        This method ensures thread-safe singleton instantiation for each subclass
        of Container. It uses double-checked locking to avoid race conditions and
        optimize performance.

        Returns
        -------
        Container
            The singleton instance of the calling class.

        Notes
        -----
        - Thread-safe implementation using reentrant lock.
        - Each subclass maintains its own singleton instance.
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
        Initialize internal state for the container.

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
            self.__resolution_cache = set()
            # Store service bindings
            self.__bindings = {}
            # Map aliases to bindings
            self.__aliases = {}
            # Cache singleton instances
            self.__singleton_cache = {}
            # Mark this instance as initialized
            self.__initialized = True  # NOSONAR

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
        # Check if the type can be auto-resolved by the container
        if not self.__canAutoResolveClass(type_):
            error_msg = (
                f"Type '{getattr(type_, '__name__', str(type_))}' cannot be "
                "auto-resolved by the container."
            )
            raise OrionisContainerException(error_msg)

        # Attempt to auto-resolve the type with provided arguments
        return self.__autoResolveClass(type_, *args, **kwargs)

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
        # Ensure the provided function is callable and not a class/type
        if not callable(fn) or isinstance(fn, type):
            error_msg = (
                f"Provided fn '{getattr(fn, '__name__', str(fn))}' must be a "
                "function or callable, not a class/type."
            )
            raise OrionisContainerTypeError(error_msg)

        # Resolve dependencies and execute the callable
        return self.__autoResolveCallable(fn, *args, **kwargs)

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
            Abstract class, interface, or alias to check.

        Returns
        -------
        bool
            True if the service is registered, False otherwise.

        Notes
        -----
        Validate both bindings and aliases.
        """
        # Check existence in bindings dictionary
        in_bindings = abstract_or_alias in self.__bindings
        # Check existence in aliases dictionary
        in_aliases = abstract_or_alias in self.__aliases
        # Return True if found in either
        return in_bindings or in_aliases

    def drop( # NOSONAR
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
        # Track if any deletion occurred
        deleted = False

        # Remove by abstract type if provided
        if abstract:
            # Remove binding for abstract type
            if abstract in self.__bindings:
                del self.__bindings[abstract]
                deleted = True

            # Remove default alias for abstract type
            abs_alias = ReflectionAbstract(abstract).getModuleWithClassName()
            if abs_alias in self.__aliases:
                del self.__aliases[abs_alias]
                deleted = True

            # Remove singleton cache entry for abstract type
            if abstract in self.__singleton_cache:
                del self.__singleton_cache[abstract]
                deleted = True

            # Remove from resolution cache
            self.__resolution_cache.discard(abs_alias)

        # Remove by custom alias if provided
        if alias:
            # Remove alias from aliases dictionary
            if alias in self.__aliases:
                del self.__aliases[alias]
                deleted = True

            # Remove binding for alias
            if alias in self.__bindings:
                del self.__bindings[alias]
                deleted = True

            # Remove singleton cache entry for alias
            if alias in self.__singleton_cache:
                del self.__singleton_cache[alias]
                deleted = True

            # Remove from resolution cache
            self.__resolution_cache.discard(alias)

        # Return True if any deletion occurred, else False
        return deleted

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
        # Validate that abstract is an abstract class
        if not Reflection.isAbstract(abstract):
            error_msg = (
                f"Expected an abstract class extending 'abc.ABC' for 'abstract', but "
                f"got '{abstract.__name__}' which is not an abstract base class."
            )
            raise OrionisContainerTypeError(error_msg)

        # Validate that concrete is a concrete class
        if not Reflection.isConcreteClass(concrete):
            error_msg = (
                f"Expected a concrete class for 'concrete', but got abstract class or "
                f"interface '{concrete.__name__}' instead."
            )
            raise OrionisContainerTypeError(error_msg)

        # Enforce decoupling or subclass relationship
        self.__decouplingCheck(
            abstract,
            concrete,
            enforce_decoupling=enforce_decoupling,
        )

        # Ensure all abstract methods are implemented
        self.__implementsAbstractMethods(
            abstract=abstract,
            concrete=concrete,
        )

        # Generate and validate the alias key
        alias = self.__makeAliasKey(abstract, alias)

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
        # Validate that abstract is an abstract class
        if not Reflection.isAbstract(abstract):
            error_msg = (
                f"Expected an abstract class extending 'abc.ABC' for 'abstract', but "
                f"got '{abstract.__name__}' which is not an abstract base class."
            )
            raise OrionisContainerTypeError(error_msg)

        # Validate that instance is a valid object
        if not Reflection.isInstance(instance):
            error_msg = (
                f"Expected a valid instance for 'instance', but got type "
                f"'{type(instance).__name__}' instead."
            )
            raise OrionisContainerTypeError(error_msg)

        # Enforce decoupling or subclass relationship as specified
        self.__decouplingCheck(
            abstract,
            instance.__class__,
            enforce_decoupling=enforce_decoupling,
        )

        # Ensure all abstract methods are implemented by the instance
        self.__implementsAbstractMethods(
            abstract=abstract,
            instance=instance,
        )

        # Generate and validate the alias key
        alias = self.__makeAliasKey(abstract, alias)

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
        # Validate that abstract is an abstract class
        if not Reflection.isAbstract(abstract):
            error_msg = (
                "Expected an abstract class extending 'abc.ABC' for 'abstract', but "
                f"got '{abstract.__name__}' which is not an abstract base class."
            )
            raise OrionisContainerTypeError(error_msg)

        # Validate that concrete is a concrete class
        if not Reflection.isConcreteClass(concrete):
            error_msg = (
                "Expected a concrete class for 'concrete', but got abstract class or "
                f"interface '{concrete.__name__}' instead."
            )
            raise OrionisContainerTypeError(error_msg)

        # Enforce decoupling or subclass relationship
        self.__decouplingCheck(
            abstract,
            concrete,
            enforce_decoupling=enforce_decoupling,
        )

        # Ensure all abstract methods are implemented
        self.__implementsAbstractMethods(
            abstract=abstract,
            concrete=concrete,
        )

        # Generate and validate the alias key
        alias = self.__makeAliasKey(abstract, alias)

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
        # Validate that abstract is an abstract class
        if not Reflection.isAbstract(abstract):
            error_msg = (
                f"Expected an abstract class extending 'abc.ABC' for 'abstract', but "
                f"got '{abstract.__name__}' which is not an abstract base class."
            )
            raise OrionisContainerTypeError(error_msg)

        # Validate that concrete is a concrete class
        if not Reflection.isConcreteClass(concrete):
            error_msg = (
                f"Expected a concrete class for 'concrete', but got abstract class or "
                f"interface '{concrete.__name__}' instead."
            )
            raise OrionisContainerTypeError(error_msg)

        # Enforce decoupling or subclass relationship
        self.__decouplingCheck(
            abstract,
            concrete,
            enforce_decoupling=enforce_decoupling,
        )

        # Ensure all abstract methods are implemented
        self.__implementsAbstractMethods(
            abstract=abstract,
            concrete=concrete,
        )

        # Generate and validate the alias key
        alias = self.__makeAliasKey(abstract, alias)

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
        # Validate that abstract is an abstract class
        if not Reflection.isAbstract(abstract):
            error_msg = (
                f"Expected an abstract class extending 'abc.ABC' for 'abstract', but "
                f"got '{abstract.__name__}' which is not an abstract base class."
            )
            raise OrionisContainerTypeError(error_msg)

        # Validate that instance is a valid object
        if not Reflection.isInstance(instance):
            error_msg = (
                f"Instance of type '{instance.__class__.__name__}' is not a valid "
                f"implementation of the abstract class '{abstract.__name__}'."
            )
            raise OrionisContainerException(error_msg)

        # Enforce decoupling or subclass relationship as specified
        self.__decouplingCheck(
            abstract,
            instance.__class__,
            enforce_decoupling=enforce_decoupling,
        )

        # Ensure all abstract methods are implemented by the instance
        self.__implementsAbstractMethods(
            abstract=abstract,
            instance=instance,
        )

        # Generate and validate the alias key (either provided or default)
        alias = self.__makeAliasKey(abstract, alias)

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
            scope[alias] = scope[abstract]

        # Return True to indicate successful registration
        return True

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
        # Validate and normalize the alias using the internal alias key generator
        alias = self.__makeAliasKey(lambda: None, alias)

        # Ensure the provided fn is actually callable
        if not callable(fn):
            error_msg = (
                f"Expected a callable type, but got {type(fn).__name__} instead."
            )
            raise OrionisContainerTypeError(error_msg)

        # Remove any existing registration under this alias
        self.drop(None, alias)

        # Register the function in the bindings dictionary with transient lifetime
        self.__bindings[alias] = Binding(
            function=fn,
            lifetime=Lifetime.TRANSIENT,
            alias=alias,
        )

        # Register the alias for lookup in the aliases dictionary
        self.__aliases[alias] = self.__bindings[alias]

        # Return True to indicate successful registration
        return True

    def createScope(self) -> ScopeManager:
        """
        Create a new scope context manager for scoped services.

        Returns
        -------
        ScopeManager
            A context manager that manages the lifecycle of scoped services.
        """
        # Instantiate and return a new ScopeManager for scoped service management
        return ScopeManager()

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
        # Resolve deferred providers first
        self.resolveDeferredProvider(type_)

        # Try to resolve from registered bindings first
        if self.bound(type_):
            # Resolve using the container's binding and lifetime rules
            return self.resolve(
                self.getBinding(type_),
                *args,
                **kwargs,
            )

        # If not registered, try auto-resolution for classes
        if isinstance(type_, type):
            # Attempt to construct the class and resolve its dependencies recursively
            return self.build(
                type_,
                *args,
                **kwargs,
            )

        # If all attempts fail, raise an exception indicating resolution failure
        error_msg = (
            f"Cannot resolve service '{getattr(type_, '__name__', str(type_))}': "
            "it is not registered in the container and cannot be auto-resolved. "
            "Please ensure the service is registered or provide all required "
            "dependencies."
        )
        raise OrionisContainerException(error_msg)

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
        # Ensure the binding is a valid Binding instance
        if not isinstance(binding, Binding):
            error_msg = (
                f"Expected a Binding instance, got {type(binding).__name__}"
            )
            raise OrionisContainerTypeError(error_msg)

        # Resolve based on the lifetime type
        if binding.lifetime == Lifetime.TRANSIENT:
            # Always create a new instance for transient lifetime
            return self.__resolveTransient(binding, *args, **kwargs)

        if binding.lifetime == Lifetime.SINGLETON:
            # Return cached instance or create one for singleton lifetime
            return self.__resolveSingleton(binding, *args, **kwargs)

        if binding.lifetime == Lifetime.SCOPED:
            # Return instance from current scope or create one for scoped lifetime
            return self.__resolveScoped(binding, *args, **kwargs)

        # Raise exception for unsupported lifetime types
        error_msg = (
            f"Unsupported lifetime '{binding.lifetime}' for binding "
            f"'{binding.contract or binding.alias}'."
        )
        raise OrionisContainerTypeError(error_msg)

    def __resolveTransient(
        self,
        binding: Binding,
        *args: tuple,
        **kwargs: dict,
    ) -> type[Any]:
        """
        Resolve a service registered with transient lifetime.

        Parameters
        ----------
        binding : Binding
            The binding to resolve.
        *args : tuple
            Positional arguments for the constructor or callable.
        **kwargs : dict
            Keyword arguments for the constructor or callable.

        Returns
        -------
        Any
            Returns a new instance of the requested service.

        Raises
        ------
        OrionisContainerException
            If no concrete class or function is defined for the binding.
        """
        # Resolve and instantiate if a concrete class is defined
        if binding.concrete:
            return self.__autoResolveClass(binding.concrete, *args, **kwargs)

        # Resolve and invoke if a function is defined
        if binding.function:
            return self.__autoResolveCallable(binding.function, *args, **kwargs)

        # Raise exception if neither is defined
        error_msg = (
            "Cannot resolve transient binding for "
            f"'{binding.contract or binding.alias}': no concrete class or "
            "function defined."
        )
        raise OrionisContainerException(error_msg)

    def __resolveSingleton(
        self,
        binding: Binding,
        *args: tuple,
        **kwargs: dict,
    ) -> type[Any]:
        """
        Resolve a service registered with singleton lifetime.

        Parameters
        ----------
        binding : Binding
            The binding to resolve.
        *args : tuple
            Positional arguments for the constructor, used if instance does not exist.
        **kwargs : dict
            Keyword arguments for the constructor, used if instance does not exist.

        Returns
        -------
        Any
            The singleton instance associated with the binding.

        Raises
        ------
        OrionisContainerException
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
            instance = self.__autoResolveClass(binding.concrete, *args, **kwargs)
            self.__singleton_cache[binding.alias] = instance
            return instance

        # Raise exception if binding cannot be resolved
        error_msg = (
            f"Cannot resolve singleton binding for "
            f"'{binding.contract or binding.alias}': no concrete class or "
            "instance defined."
        )
        raise OrionisContainerException(error_msg)

    def __resolveScoped(
        self,
        binding: Binding,
        *args: tuple,
        **kwargs: dict,
    ) -> type[Any]:
        """
        Resolve a service registered with scoped lifetime.

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
            The resolved instance from the current scope, or raises an exception
            if no scope is active or no implementation is defined.

        Raises
        ------
        OrionisContainerException
            If there is no active scope.
            If no implementation or instance is defined for the binding.
        """
        # Get the current scope context
        scope = ScopedContext.getCurrentScope()

        # Raise if there is no active scope
        if scope is None:
            error_msg = (
                f"No active scope for scoped service '{binding.alias}'. "
                "Use 'with app.createScope()'."
            )
            raise OrionisContainerException(error_msg)

        # Return the instance if already present in the scope by contract
        if binding.contract in scope:
            return scope[binding.contract]

        # Return the instance if already present in the scope by alias
        if binding.alias in scope:
            return scope[binding.alias]

        # Create and store a new instance in the scope if not present
        if binding.concrete:
            instance = self.__autoResolveClass(binding.concrete, *args, **kwargs)
            scope[binding.contract] = instance
            scope[binding.alias] = instance
            return scope[binding.contract]

        # Raise if no implementation or instance is defined
        error_msg = (
            f"Cannot resolve scoped binding for '{binding.contract or binding.alias}': "
            "no implementation or instance defined."
        )
        raise OrionisContainerException(error_msg)

    def __makeAliasKey(
        self,
        abstract: Callable[..., Any],
        alias: str | None = None,
    ) -> str:
        """
        Generate a unique alias key for service registration.

        Parameters
        ----------
        abstract : Callable[..., Any]
            Abstract base class or interface for alias generation.
        alias : str | None, optional
            Custom alias string.

        Returns
        -------
        str
            Returns a validated custom alias or a default alias in the format
            'module.ClassName'.

        Raises
        ------
        OrionisContainerTypeError
            Raised if the alias is invalid.
        """
        # Set of forbidden characters for alias strings
        invalid_chars = set(
            ' \t\n\r\x0b\x0c!@#$%^&*()[]{};:,/<>?\\|`~"\'',
        )

        # Validate custom alias if provided
        if alias:
            # Check for None, empty, or whitespace-only alias
            if alias is None or alias == "" or str(alias).isspace():
                error_msg = (
                    "Alias cannot be None, empty, or whitespace only."
                )
                raise OrionisContainerTypeError(error_msg)

            # Ensure alias is a string
            if not isinstance(alias, str):
                error_msg = (
                    f"Expected a string type for alias, but got "
                    f"{type(alias).__name__} instead."
                )
                raise OrionisContainerTypeError(error_msg)

            # Check for invalid characters in alias
            if any(char in invalid_chars for char in alias):
                error_msg = (
                    f"Alias '{alias}' contains invalid characters."
                )
                raise OrionisContainerTypeError(error_msg)

            # Return validated custom alias
            return alias

        # Generate default alias from abstract class module and name
        return f"{abstract.__module__}.{abstract.__name__}"

    def __autoResolveClass(
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
        OrionisContainerCircularDependencyException
            If a circular dependency is detected.
        OrionisContainerException
            If the type cannot be auto-resolved.
        """
        # Create a unique key for circular dependency tracking
        type_key = f"{type_.__module__}.{type_.__name__}"

        # Check for circular dependency
        if type_key in self.__resolution_cache:
            error_msg = (
                f"Circular dependency detected while resolving argument '{type_key}'."
            )
            raise OrionisContainerCircularDependencyException(error_msg)

        try:
            # Mark type as being resolved
            self.__resolution_cache.add(type_key)

            # Get constructor dependencies using reflection
            dependencies = ReflectionConcrete(type_).constructorSignature()

            # If no dependencies, instantiate directly
            if dependencies.hasNoDependencies():
                return type_(*args, **kwargs)

            # Resolve dependencies recursively
            final_args, final_kwargs = self.__resolveSignature(
                dependencies, *args, **kwargs,
            )

            # Instantiate with resolved arguments
            return type_(*final_args, **final_kwargs)

        finally:

            # Clean up resolution cache
            self.__resolution_cache.discard(type_key)

    def __autoResolveCallable(
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
        OrionisContainerException
            If the callable cannot be auto-resolved.
        """
        # Get callable dependencies using reflection
        dependencies = ReflectionCallable(type_).getDependencies()

        # If no dependencies, invoke directly
        if dependencies.hasNoDependencies():
            return self.__callAndResolve(type_, *args, **kwargs)

        # Resolve dependencies recursively
        final_args, final_kwargs = self.__resolveSignature(
            dependencies, *args, **kwargs,
        )

        # Invoke the callable with resolved arguments
        return self.__callAndResolve(type_, *final_args, **final_kwargs)

    def __callAndResolve(
        self,
        func: Callable[..., Any],
        *args: tuple,
        **kwargs: dict,
    ) -> type[Any]:
        """
        Execute a function and handle both synchronous and asynchronous results.

        Parameters
        ----------
        func : Callable[..., Any]
            The function to execute, which may be synchronous or asynchronous.
        *args : tuple
            Positional arguments to pass to the function.
        **kwargs : dict
            Keyword arguments to pass to the function.

        Returns
        -------
        Any
            The result of the function execution. If the function returns a coroutine,
            the coroutine is awaited and its result is returned.
        """
        # Execute the function with provided arguments
        result = func(*args, **kwargs)

        # Return immediately if the result is not a coroutine
        if not asyncio.iscoroutine(result):
            return result

        # Handle asynchronous result
        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()

            # If the loop is running, execute the coroutine in a new thread
            if loop.is_running():

                # Function to run the coroutine in a new event loop
                def run_coroutine() -> type[Any]:
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(result)
                    finally:
                        new_loop.close()

                # Use ThreadPoolExecutor to run the coroutine in a separate thread
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_coroutine)
                    return future.result()

            # If the loop exists but is not running, run the coroutine directly
            else:
                return loop.run_until_complete(result)

        except RuntimeError:

            # If no event loop exists, use asyncio.run to execute the coroutine
            return asyncio.run(result)

    def __resolveSignature( # NOSONAR
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

            # Resolve deferred providers first
            self.resolveDeferredProvider(dep.type)

            # Handle positional or positional-or-keyword arguments
            if not is_keyword_only:

                # Resolve from container by type if bound and not provided as keyword
                if self.bound(dep.type) and name not in remaining_kwargs:
                    final_args.append(self.resolve(self.getBinding(dep.type)))
                    continue

                # Resolve from container by full class path if bound and not provided
                if self.bound(dep.full_class_path) and name not in remaining_kwargs:
                    final_args.append(self.resolve(self.getBinding(dep.full_class_path)))
                    continue

                # Use next positional argument if available
                if positional:
                    value: Any = positional.popleft()
                    final_args.append(value)
                    continue

                # Use provided keyword argument if available
                if name in remaining_kwargs:
                    final_args.append(remaining_kwargs[name])
                    del remaining_kwargs[name]
                    continue

                # Fallback to automatic resolution if no explicit value
                final_args.append(self.__resolveArgument(dep))

            else:

                # Use provided keyword argument if available
                if name in remaining_kwargs:
                    final_kwargs[name] = remaining_kwargs[name]
                    del remaining_kwargs[name]
                    continue

                # Resolve keyword-only argument from container by type
                if self.bound(dep.type):
                    final_kwargs[name] = self.resolve(
                        self.getBinding(dep.type),
                    )
                    continue

                # Resolve keyword-only argument from container by full class path
                if self.bound(dep.full_class_path):
                    final_kwargs[name] = self.resolve(
                        self.getBinding(dep.full_class_path),
                    )
                    continue

                # Fallback to automatic resolution for keyword-only argument
                final_kwargs[name] = self.__resolveArgument(dep)

        # Append any remaining positional arguments
        final_args.extend(positional)

        # Add any remaining unused keyword arguments
        final_kwargs.update(remaining_kwargs)

        # Return resolved positional and keyword arguments
        return final_args, final_kwargs

    def __resolveArgument(
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
        OrionisContainerCircularDependencyException
            If a circular dependency is detected.
        OrionisContainerException
            If the argument cannot be resolved.

        Notes
        -----
        Handles resolution from scope, container, or by default value.
        """
        # List of modules that cannot be auto-resolved
        special_modules: list[str] = ["typing", "builtins"]

        # Check if argument is resolved in the current scope
        scoped = ScopedContext.getCurrentScope()
        if scoped and (argument.type in scoped or argument.full_class_path in scoped):
            # Prefer type over full_class_path for resolution
            # ruff: noqa: RET505
            if argument.type in scoped:
                return scoped[argument.type]
            else:
                return scoped[argument.full_class_path]

        # Return default value for resolved arguments from
        # special modules or with default
        if (
            (argument.resolved and argument.module_name in special_modules)
            or (argument.resolved and argument.default is not None)
        ):
            return argument.default

        # Raise for unresolvable built-in or typing types
        if not argument.resolved and argument.module_name in special_modules:
            error_msg = (
                f"Cannot resolve '{argument.name}' of type '{argument.module_name}'. "
                "Provide a default value."
            )
            raise OrionisContainerException(error_msg)

        # Attempt resolution using the argument type if bound in container
        if self.bound(argument.type):
            return self.resolve(self.getBinding(argument.type))

        # Attempt resolution using the full class path if bound in container
        if self.bound(argument.full_class_path):
            return self.resolve(self.getBinding(argument.full_class_path))

        # Try auto-resolution if the type is eligible
        if self.__canAutoResolveClass(argument.type):
            return self.__autoResolveClass(argument.type)

        # Raise if all resolution methods fail
        error_msg = (
            f"Cannot resolve '{argument.name}' of type '{argument.module_name}'. "
            "Provide a default value."
        )
        raise OrionisContainerException(error_msg)

    def __canAutoResolveClass(
        self,
        type_: Callable[..., Any],
    ) -> bool:
        """
        Determine if a type is eligible for automatic resolution by the container.

        Parameters
        ----------
        type_ : Callable[..., Any]
            The type to check for auto-resolution eligibility.

        Returns
        -------
        bool
            True if the type can be auto-resolved, otherwise False.

        Notes
        -----
        Returns True only if the type is a concrete class and not defined in '__main__'.
        """
        # Check if the type is a concrete class (not abstract or interface)
        if not Reflection.isConcreteClass(type_):
            return False

        # Exclude types defined in the '__main__' module from auto-resolution
        return type_.__module__ != "__main__"

    def __decouplingCheck(
        self,
        abstract: Callable[..., Any],
        concrete: Callable[..., Any],
        *,
        enforce_decoupling: bool,
    ) -> None:
        """
        Validate the inheritance relationship between abstract and concrete classes.

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
            This method does not return any value.

        Raises
        ------
        OrionisContainerException
            If inheritance relationship does not match the decoupling requirement.
        """
        # If decoupling is enforced, concrete must not inherit from abstract
        if enforce_decoupling:

            # Raise exception if concrete inherits from abstract
            if issubclass(concrete, abstract):
                error_msg = (
                    "Concrete class must not inherit from the abstract class."
                )
                raise OrionisContainerTypeError(error_msg)

        # If inheritance is required, concrete must inherit from abstract
        elif not issubclass(concrete, abstract):
            error_msg = (
                "Concrete class must inherit from the abstract class."
            )
            raise OrionisContainerTypeError(error_msg)

    def __implementsAbstractMethods(
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
        abstract : Callable[..., Any]
            Abstract base class containing abstract methods.
        concrete : Callable[..., Any], optional
            Concrete class to check for method implementation.
        instance : Any, optional
            Instance to check for method implementation.

        Returns
        -------
        None
            Raises an exception if validation fails.

        Raises
        ------
        OrionisContainerException
            If required methods are not implemented or validation fails.
        """
        # Ensure the abstract class is provided
        if abstract is None:
            error_msg = (
                "Abstract class must be provided for implementation check."
            )
            raise OrionisContainerException(error_msg)

        # Get reflection for the abstract class
        rf_abstract = ReflectionAbstract(abstract)

        # Get all abstract methods to be implemented
        abstract_methods = rf_abstract.getMethods()
        if not abstract_methods:
            error_msg = (
                f"Abstract class '{abstract.__name__}' has no abstract methods."
            )
            raise OrionisContainerException(error_msg)

        # Select the target class or instance for validation
        target = concrete if concrete is not None else instance
        if target is None:
            error_msg = (
                "Either concrete class or instance must be provided for "
                "implementation check."
            )
            raise OrionisContainerException(error_msg)

        # Get the actual class type from the target
        target_class = target if Reflection.isClass(target) else target.__class__

        # Get reflection for the concrete class
        rf_class = ReflectionConcrete(target_class)

        # Get class names for error reporting
        target_name = rf_class.getClassName()
        abstract_name = rf_abstract.getClassName()

        # Get all methods implemented by the target class
        implemented_methods = rf_class.getMethods()

        # Check for missing implementations
        # ruff: noqa: PERF401
        not_implemented = []
        for method in abstract_methods:
            if method not in implemented_methods:
                not_implemented.append(method)

        # Raise exception if any abstract methods are not implemented
        if not_implemented:
            methods = ", ".join(not_implemented)
            error_msg = (
                f"Class '{target_name}' must implement the following abstract "
                f"methods from '{abstract_name}': {methods}"
            )
            raise OrionisContainerException(error_msg)

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
        # Retrieve the method from the instance by name
        method = getattr(instance, method_name)

        # Check if the method exists
        if method is None:
            error_msg = (
                f"Method '{method_name}' not found in instance of type "
                f"'{type(instance).__name__}'."
            )
            raise OrionisContainerException(error_msg)

        # Ensure the attribute is callable
        if not callable(method):
            error_msg = (
                f"Attribute '{method_name}' of instance "
                f"'{type(instance).__name__}' is not callable."
            )
            raise OrionisContainerTypeError(error_msg)

        # Invoke the method with automatic dependency resolution
        return self.__autoResolveCallable(method, *args, **kwargs)
