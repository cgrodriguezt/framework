from __future__ import annotations
import importlib
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
from orionis.services.introspection.callables.reflection import ReflectionCallable
from orionis.services.introspection.concretes.reflection import ReflectionConcrete

if TYPE_CHECKING:
    from collections.abc import Callable
    from orionis.container.contracts.service_provider import IServiceProvider
    from orionis.services.introspection.dependencies.entities.argument import Argument
    from orionis.services.introspection.dependencies.entities.signature import Signature

class Container(IContainer):

    # ruff: noqa: ANN401, SLF001, FBT001

    # Dictionary to hold singleton instances for each class
    # This allows proper inheritance of the singleton pattern
    _instances: ClassVar[dict] = {}

    # Lock for thread-safe singleton instantiation and access
    # This lock ensures that only one thread can create or access instances at a time
    _lock = threading.RLock()  # RLock allows reentrant locking

    def __new__(cls, *args, **kwargs) -> Self:
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

        Sets up internal data structures for dependency injection and ensures
        single initialization per instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Prevent multiple initializations for singleton instances
        if not hasattr(self, "_Container__initialized"):
            # Deferred providers for lazy loading
            self._deferred_providers: dict[str, dict[str, str]] = {}
            # Cache for singleton instances
            self.__singleton_cache: dict[str, Any] = {}
            # Aliases mapping for service resolution
            self.__aliases: dict[str, type] = {}
            # Tracks currently resolving dependencies to detect cycles
            self.__resolution_cache: set[str] = set()
            # Registered bindings for services
            self.__bindings: dict[Any, Binding] = {}
            # Tracks resolved deferred providers
            self.__cache_resolve_deferred_providers: set[Any] = set()
            # Mark as initialized to prevent re-initialization
            self._Container__initialized = True

    def __aliasService(
        self,
        alias: str | None,
    ) -> str | None:
        """
        Validate and normalize a service alias string.

        Parameters
        ----------
        alias : str | None
            The alias string to validate and normalize.

        Returns
        -------
        str | None
            The validated and normalized alias string, or None if not provided.

        Raises
        ------
        TypeError
            If the alias is not a string.
        ValueError
            If the alias is empty after stripping.
        """
        # Return None if alias is not provided
        if alias is None:
            return None

        # Ensure alias is a string
        if not isinstance(alias, str):
            error_msg = "alias must be a string."
            raise TypeError(error_msg)

        alias = alias.strip()

        # Ensure alias is not empty after stripping
        if not alias:
            error_msg = "Alias cannot be empty."
            raise ValueError(error_msg)

        return alias

    def __ensureCanOverrideScope(
        self,
        override: bool,
        abstract: type[Any],
        scope: dict[Any, Any],
    ) -> None:
        """
        Ensure that a service can be overridden in the current scope.

        Parameters
        ----------
        override : bool
            Whether to allow overriding existing registrations.
        abstract : type[Any]
            The abstract contract type to check.
        scope : dict[Any, Any]
            The current scope dictionary.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        ValueError
            If the service already exists in the current scope and
            override is False.
        """
        # Allow override if specified
        if override:
            return

        # Raise if the abstract contract already exists in the scope
        if abstract in scope:
            error_msg = "Service already exists in current scope."
            raise ValueError(error_msg)

    def __ensureCanOverrideGlobal(
        self,
        override: bool,
        abstract: type[Any],
        alias: str | None,
    ) -> None:
        """
        Ensure that a service or alias can be overridden globally.

        Parameters
        ----------
        override : bool
            Whether to allow overriding existing registrations.
        abstract : type[Any]
            The abstract contract type to check.
        alias : str | None
            The alias to check for conflicts.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        ValueError
            If the service or alias already exists globally and override is False.
        """
        # Allow override if specified
        if override:
            return

        # Raise if the abstract contract already exists in global bindings
        if abstract in self.__bindings:
            error_msg = "Service already registered for this contract."
            raise ValueError(error_msg)

        # Raise if the alias already exists in global aliases
        if alias is not None and alias in self.__aliases:
            error_msg = "Service already registered for this alias."
            raise ValueError(error_msg)

    def __ensureInstanceImplements(
        self,
        abstract: type[Any],
        instance: object,
    ) -> None:
        """
        Ensure that an instance implements the specified abstract class.

        Parameters
        ----------
        abstract : type[Any]
            The abstract class type to check against.
        instance : object
            The object instance to validate.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If `abstract` is not a class type or `instance` does not implement it.
        """
        # Check that the abstract argument is a class type
        if not inspect.isclass(abstract):
            error_msg = "abstract must be a class type."
            raise TypeError(error_msg)

        # Ensure the instance implements the abstract class
        if not isinstance(instance, abstract):
            error_msg = (
                f"{type(instance).__name__} must implement {abstract.__name__}"
            )
            raise TypeError(error_msg)

    def __ensureConcreteImplements(
        self,
        abstract: type[Any],
        concrete: type[Any],
    ) -> None:
        """
        Ensure that a concrete class implements the specified abstract class.

        Parameters
        ----------
        abstract : type[Any]
            The abstract class type to check against.
        concrete : type[Any]
            The concrete class type to validate.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If `abstract` or `concrete` is not a class type, or if `concrete`
            does not implement `abstract`.
        """
        # Validate that abstract is a class type
        if not inspect.isclass(abstract):
            error_msg = "abstract must be a class type."
            raise TypeError(error_msg)

        # Validate that concrete is a class type
        if not inspect.isclass(concrete):
            error_msg = "concrete must be a class type."
            raise TypeError(error_msg)

        # Ensure concrete implements abstract
        if not issubclass(concrete, abstract):
            error_msg = (
                f"{concrete.__name__} must implement {abstract.__name__}"
            )
            raise TypeError(error_msg)

    def __bind(
        self,
        lifetime: Lifetime,
        abstract: type[Any] | None,
        concrete: type[Any],
        *,
        alias: str | None,
        override: bool,
    ) -> bool:
        """
        Bind a concrete implementation to an abstract contract with a given lifetime.

        Parameters
        ----------
        lifetime : Lifetime
            The lifetime of the binding (singleton, scoped, or transient).
        abstract : type[Any] | None
            The abstract contract class to associate with the concrete class,
            or None to use the concrete class as the contract.
        concrete : type[Any]
            The concrete class to register.
        alias : str | None
            An optional alias for the registration.
        override : bool
            If True, override any existing registration.

        Returns
        -------
        bool
            True if the binding was registered successfully.

        Raises
        ------
        TypeError
            If the concrete is not a class type or type validation fails.
        ValueError
            If the alias is invalid or already registered, or if the contract is
            already registered and override is False.
        """
        # Validate the contract if provided
        if abstract is not None:
            self.__ensureConcreteImplements(abstract, concrete)
        else:
            if not inspect.isclass(concrete):
                error_msg = "concrete must be a class type."
                raise TypeError(error_msg)
            abstract = concrete

        # Validate the alias if provided
        if alias is not None:
            alias = self.__aliasService(alias)

        # Enforce override rules for service registration
        self.__ensureCanOverrideGlobal(override, abstract, alias)

        # Register the binding in the container
        binding = Binding(
            contract=abstract,
            concrete=concrete,
            lifetime=lifetime,
            alias=alias,
        )
        self.__bindings[abstract] = binding
        if alias is not None:
            self.__aliases[alias] = abstract

        # Registration successful
        return True

    def instance(
        self,
        abstract: type[Any] | None,
        instance: object,
        *,
        alias: str | None = None,
        override: bool = False,
    ) -> bool:
        """
        Register an object instance as a singleton in the container.

        Parameters
        ----------
        abstract : type[Any] | None
            The abstract contract class to associate with the instance, or None.
        instance : object
            The initialized object to register.
        alias : str | None, optional
            An optional alias for the registration.
        override : bool, optional
            If True, override any existing registration.

        Returns
        -------
        bool
            True if the instance was registered successfully.

        Raises
        ------
        TypeError
            If the instance is a class, or if type validation fails.
        ValueError
            If the alias is invalid or already registered, or if the contract is
            already registered and override is False.
        """
        # Ensure the provided instance is not a class type
        if isinstance(instance, type):
            error_msg = "instance() expects an initialized object, not a class."
            raise TypeError(error_msg)

        # Validate the contract if provided
        if abstract is not None:
            self.__ensureInstanceImplements(abstract, instance)
        else:
            abstract = type(instance)

        # Validate the alias if provided
        if alias is not None:
            alias = self.__aliasService(alias)

        # Get the current scope for registration
        scope: dict[Any, Any] | None = self.getCurrentScope()

        # Enforce override rules for service registration
        if scope is not None:
            self.__ensureCanOverrideScope(override, abstract, scope)
        else:
            self.__ensureCanOverrideGlobal(override, abstract, alias)

        if scope is not None:
            if alias is not None:
                msg_error = "Alias registration is only allowed globally."
                raise ValueError(msg_error)
            # Register instance in the current scope
            scope[abstract] = instance
        else:
            # Register as singleton in the container
            binding = Binding(
                contract=abstract,
                concrete=type(instance),
                lifetime=Lifetime.SINGLETON,
                alias=alias,
            )
            self.__bindings[abstract] = binding
            self.__singleton_cache[abstract] = instance
            if alias is not None:
                self.__aliases[alias] = abstract

        # Registration successful
        return True

    def transient(
        self,
        abstract: type[Any] | None,
        concrete: type[Any],
        *,
        alias: str | None = None,
        override: bool = False,
    ) -> bool:
        """
        Register a transient service binding.

        Parameters
        ----------
        abstract : type[Any] | None
            The abstract contract type to bind, or None to use the concrete type.
        concrete : type[Any]
            The concrete implementation type to register.
        alias : str | None, optional
            An optional alias for the service.
        override : bool, optional
            Whether to override an existing registration.

        Returns
        -------
        bool
            True if the binding was registered successfully.
        """
        # Register the binding with transient lifetime
        return self.__bind(
            lifetime=Lifetime.TRANSIENT,
            abstract=abstract,
            concrete=concrete,
            alias=alias,
            override=override,
        )

    def singleton(
        self,
        abstract: type[Any] | None,
        concrete: type[Any],
        *,
        alias: str | None = None,
        override: bool = False,
    ) -> bool:
        """
        Register a singleton service binding.

        Parameters
        ----------
        abstract : type[Any] | None
            The abstract contract type to bind, or None to use the concrete type.
        concrete : type[Any]
            The concrete implementation type to register.
        alias : str | None, optional
            An optional alias for the service.
        override : bool, optional
            Whether to override an existing registration.

        Returns
        -------
        bool
            True if the binding was registered successfully.
        """
        # Register the binding with singleton lifetime
        return self.__bind(
            lifetime=Lifetime.SINGLETON,
            abstract=abstract,
            concrete=concrete,
            alias=alias,
            override=override,
        )

    def scoped(
        self,
        abstract: type[Any] | None,
        concrete: type[Any],
        *,
        alias: str | None = None,
        override: bool = False,
    ) -> bool:
        """
        Register a scoped service binding.

        Parameters
        ----------
        abstract : type[Any] | None
            The abstract contract type to bind, or None to use the concrete type.
        concrete : type[Any]
            The concrete implementation type to register.
        alias : str | None, optional
            An optional alias for the service.
        override : bool, optional
            Whether to override an existing registration.

        Returns
        -------
        bool
            True if the binding was registered successfully.
        """
        # Register the binding with scoped lifetime
        return self.__bind(
            lifetime=Lifetime.SCOPED,
            abstract=abstract,
            concrete=concrete,
            alias=alias,
            override=override,
        )

    def bound(
        self,
        key: type[Any] | str,
    ) -> bool:
        """
        Determine if a key is bound in the container or current scope.

        Parameters
        ----------
        key : type[Any] | str
            The abstract type or alias to check for binding.

        Returns
        -------
        bool
            True if the key is bound in the current scope or container,
            otherwise False.
        """
        # Resolve alias to abstract type if key is a string
        if isinstance(key, str):
            abstract = self.__aliases.get(key)
            if abstract is None:
                return False
        else:
            abstract = key

        # Check if the abstract type is present in the current scope
        scope: dict[Any, Any] | None = self.getCurrentScope()
        if scope is not None and abstract in scope:
            return True

        # Check if the abstract type is registered in the container bindings
        return (
            abstract in self.__bindings or
            abstract in self.__singleton_cache
        )

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
        # Return the current active scope context from ScopedContext
        return ScopedContext.getCurrentScope()

    async def __resolveDeferredProvider(
        self,
        key: type[Any] | str,
    ) -> None:
        """
        Resolve and register a deferred service provider for a given service.

        Parameters
        ----------
        key : type[Any] | str
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
        Returns early if the provider is already resolved or is a built-in.
        """
        # Return early if there are no deferred providers to resolve
        if not self._deferred_providers:
            return

        # Convert class type to fully qualified class name string if necessary
        if isinstance(key, type):
            key = f"{key.__module__}.{key.__name__}"

        # Return early if there are no deferred providers or already resolved
        if key in self.__cache_resolve_deferred_providers:
            return

        # Return early if the key is not registered as a deferred provider
        if key not in self._deferred_providers:
            return

        # Retrieve provider metadata for the given key
        provider_metadata = self._deferred_providers.get(key)

        # Mark as resolved to prevent duplicate processing
        module = importlib.import_module(provider_metadata["module"])
        provider_class = getattr(module, provider_metadata["class"], None)

        # Build and register the provider instance
        instance: IServiceProvider = await self.build(provider_class)
        instance.register()

        # Boot the provider instance, supporting async and sync methods
        if inspect.iscoroutinefunction(instance.boot):
            await instance.boot()
        else:
            instance.boot()

        # Cache the resolved service to prevent redundant resolution
        self.__cache_resolve_deferred_providers.add(key)

    async def make(
        self,
        key: type[Any] | str,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> Any:
        """
        Resolve and return a service instance by key.

        Parameters
        ----------
        key : type[Any] | str
            The abstract type or alias to resolve.
        *args : tuple[Any, ...]
            Positional arguments for instantiation.
        **kwargs : dict[str, Any]
            Keyword arguments for instantiation.

        Returns
        -------
        Any
            The resolved service instance.

        Raises
        ------
        ValueError
            If the service is not registered and cannot be auto-resolved.
        """
        # Resolve deferred providers if the key is not already bound
        if not self.bound(key):
            await self.__resolveDeferredProvider(key)

        # Check again if the key is bound after resolving deferred providers
        if not self.bound(key):

            # If the key is a class type, attempt to auto-resolve it directly
            if isinstance(key, type):
                return await self.build(key, *args, **kwargs)

            # If the key is a string, raise an error for unregistered service
            error_msg = f"Service '{key}' is not registered."
            raise ValueError(error_msg)

        # Resolve alias to abstract type if key is a string
        abstract = self.__aliases.get(key) if isinstance(key, str) else key

        # Check if the abstract type is available in the current scope
        scope: dict[Any, Any] | None = self.getCurrentScope()
        if scope is not None and abstract in scope:
            return scope[abstract]

        # Check if the abstract type is available in the singleton cache
        if abstract in self.__singleton_cache:
            return self.__singleton_cache[abstract]

        # Retrieve and resolve the binding for the abstract type
        return await self.__resolve(self.__bindings[abstract], *args, **kwargs)

    async def __resolve(
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
        RuntimeError
            If there is no active scope for scoped services.
        """
        # Handle transient lifetime: always create a new instance
        if binding.lifetime == Lifetime.TRANSIENT:
            return await self.__autoResolveClass(binding.concrete, *args, **kwargs)

        # Handle singleton lifetime: cache and reuse the instance
        if binding.lifetime == Lifetime.SINGLETON:
            if binding.contract not in self.__singleton_cache:
                instance = await self.__autoResolveClass(
                    binding.concrete, *args, **kwargs,
                )
                self.__singleton_cache[binding.contract] = instance
            return self.__singleton_cache[binding.contract]

        # Handle scoped lifetime: store instance in the current scope
        if binding.lifetime == Lifetime.SCOPED:
            scope: dict[Any, Any] | None = ScopedContext.getCurrentScope()
            if scope is None:
                error_msg = (
                    "No active scope for scoped service. "
                    "Use 'beginScope()' to create a scope."
                )
                raise RuntimeError(error_msg)

            if binding.contract in scope:
                return scope[binding.contract]

            instance = await self.__autoResolveClass(
                binding.concrete, *args, **kwargs,
            )
            scope[binding.contract] = instance
            return instance

        # This line should never be reached due to the enum handling
        return None

    async def __autoResolveClass(
        self,
        type_: Callable[..., Any],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> Any:
        """
        Automatically instantiate a class with injected dependencies.

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
            The instantiated object with dependencies resolved.

        Raises
        ------
        CircularDependencyException
            If a circular dependency is detected.
        Exception
            If the type cannot be auto-resolved.
        """
        # Create a unique key for circular dependency tracking
        type_key = f"{type_.__module__}.{type_.__name__}"

        # Detect circular dependencies
        if type_key in self.__resolution_cache:
            error_msg = (
                f"Circular dependency detected while resolving argument '{type_key}'."
            )
            raise CircularDependencyException(error_msg)

        try:
            # Mark type as being resolved to prevent recursion
            self.__resolution_cache.add(type_key)

            # Get constructor dependencies using reflection
            signature = ReflectionConcrete(type_).constructorSignature()

            # If no dependencies, instantiate directly
            if signature.noArgumentsRequired():
                return type_(*args, **kwargs)

            # Resolve dependencies recursively
            final_args, final_kwargs = await self.__resolveSignature(
                signature, *args, **kwargs,
            )

            # Instantiate with resolved arguments
            return type_(*final_args, **final_kwargs)

        finally:
            # Remove type from resolution cache after instantiation
            self.__resolution_cache.discard(type_key)

    async def build(
        self,
        type_: Callable[..., Any],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> Any:
        """
        Build and return an instance of the specified type.

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
            Instantiated object of the specified type.

        Raises
        ------
        TypeError
            If the type cannot be auto-resolved by the container.

        Notes
        -----
        Resolves deferred providers before attempting instantiation.
        """
        # Resolve deferred providers for the given type if not already bound
        if not self.bound(type_):
            await self.__resolveDeferredProvider(type_)

        # Ensure the provided type is a class
        if not inspect.isclass(type_):
            error_msg = "build() expects a class type to instantiate."
            raise TypeError(error_msg)

        # Auto-resolve and instantiate the class with provided arguments
        return await self.__autoResolveClass(type_, *args, **kwargs)

    async def invoke(
        self,
        fn: Callable[..., Any],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> Any:
        """
        Invoke a callable with automatic dependency injection.

        Parameters
        ----------
        fn : Callable[..., Any]
            The callable to invoke. Must not be a class or type.
        *args : tuple[Any, ...]
            Positional arguments for the callable.
        **kwargs : dict[str, Any]
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
            error_msg = "invoke() expects a non-class callable as the first argument."
            raise TypeError(error_msg)

        # Resolve dependencies and execute the callable
        return await self.__autoResolveCallable(fn, *args, **kwargs)

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
                f"Method '{method_name}' not found on instance of type "
                f"'{type(instance).__name__}'."
            )
            raise AttributeError(error_msg)

        # Ensure the attribute is callable
        if not callable(method):
            error_msg = (
                f"Attribute '{method_name}' on instance of type "
                f"'{type(instance).__name__}' is not callable."
            )
            raise TypeError(error_msg)

        # Invoke the method with automatic dependency resolution
        return await self.__autoResolveCallable(method, *args, **kwargs)

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
        signature = ReflectionCallable(type_).getDependencies()

        # If no dependencies, invoke directly
        if signature.noArgumentsRequired():
            if inspect.iscoroutinefunction(type_):
                return await type_(*args, **kwargs)
            return type_(*args, **kwargs)

        # Resolve dependencies recursively
        final_args, final_kwargs = await self.__resolveSignature(
            signature, *args, **kwargs,
        )

        # Invoke the callable with resolved arguments
        if inspect.iscoroutinefunction(type_):
            return await type_(*final_args, **final_kwargs)
        return type_(*final_args, **final_kwargs)

    async def __resolveSignature(
        self,
        signature: Signature,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> tuple[list[Any], dict[str, Any]]:
        """
        Resolve arguments for a callable signature using dependency injection.

        Parameters
        ----------
        signature : Signature
            The signature object containing argument metadata.
        *args : tuple[Any, ...]
            Positional arguments to pass to the callable.
        **kwargs : dict[str, Any]
            Keyword arguments to pass to the callable.

        Returns
        -------
        tuple[list[Any], dict[str, Any]]
            A tuple containing the resolved positional and keyword arguments.
        """
        # Copy kwargs to avoid mutating the original dictionary
        remaining_kwargs: dict[str, Any] = dict(kwargs)

        # Use deque for efficient positional argument handling
        positional: deque[Any] = deque(args)

        # Prepare containers for resolved arguments
        final_args: list[Any] = []
        final_kwargs: dict[str, Any] = {}

        # Iterate over arguments in definition order
        for name, argument in signature.arguments():

            # Resolve deferred providers for the argument type if necessary
            if argument.full_class_path in self._deferred_providers:
                await self.__resolveDeferredProvider(argument.full_class_path)

            # Determine if the argument is keyword-only
            is_keyword_only = argument.is_keyword_only

            # Handle positional or positional-or-keyword arguments
            if not is_keyword_only:

                # Resolve from container by type if bound and not provided as keyword
                if self.bound(argument.type) and name not in remaining_kwargs:
                    resolved = await self.make(argument.type)
                    final_args.append(resolved)
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
                resolved = await self.__resolveArgument(argument)
                final_args.append(resolved)

            else:

                # Use provided keyword argument if available
                if name in remaining_kwargs:
                    final_kwargs[name] = remaining_kwargs[name]
                    del remaining_kwargs[name]
                    continue

                # Resolve keyword-only argument from container by type
                if self.bound(argument.type):
                    resolved = await self.make(argument.type)
                    final_kwargs[name] = resolved
                    continue

                # Fallback to automatic resolution for keyword-only argument
                resolved = await self.__resolveArgument(argument)
                final_kwargs[name] = resolved

        # Append any remaining positional arguments
        final_args.extend(positional)

        # Add any remaining unused keyword arguments
        final_kwargs.update(remaining_kwargs)

        # Return resolved positional and keyword arguments
        return final_args, final_kwargs

    async def __resolveArgument(
        self,
        argument: Argument,
    ) -> Any:
        """
        Resolve a single argument for dependency injection.

        Parameters
        ----------
        argument : Argument
            The argument metadata to resolve.

        Returns
        -------
        Any
            The resolved value for the argument.

        Raises
        ------
        TypeError
            If the argument cannot be resolved or is a built-in type.
        """
        # Prefer the default value if it exists
        if argument.default is not inspect._empty:
            return argument.default

        # Fail fast if the argument type is not resolved or not a class
        if not argument.resolved or not inspect.isclass(argument.type):
            error_msg = (
                f"Cannot resolve parameter '{argument.name}'. "
                "Provide a default value or register the dependency."
            )
            raise TypeError(error_msg)

        # Do not auto-resolve built-in or typing types
        if argument.module_name in ("builtins", "typing"):
            error_msg = (
                f"Cannot auto-resolve built-in type '{argument.type.__name__}' "
                f"for parameter '{argument.name}'. Provide a default value."
            )
            raise TypeError(error_msg)

        # Resolve from container or auto-resolve
        return await self.make(argument.type)
