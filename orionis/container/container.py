import asyncio
import threading
from collections import deque
from typing import Any, Callable, Dict, List, Optional, Tuple
from orionis.container.context.manager import ScopeManager
from orionis.container.context.scope import ScopedContext
from orionis.container.contracts.container import IContainer
from orionis.container.entities.binding import Binding
from orionis.container.enums.lifetimes import Lifetime
from orionis.container.exceptions import OrionisContainerException, OrionisContainerCircularDependencyException
from orionis.container.exceptions.container import OrionisContainerTypeError
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.callables.reflection import ReflectionCallable
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.services.introspection.dependencies.entities.argument import Argument
from orionis.services.introspection.dependencies.entities.signature import SignatureArguments
from orionis.services.introspection.reflection import Reflection

class Container(IContainer):

    # Dictionary to hold singleton instances for each class
    # This allows proper inheritance of the singleton pattern
    _instances = {}

    # Lock for thread-safe singleton instantiation and access
    # This lock ensures that only one thread can create or access instances at a time
    _lock = threading.RLock()  # RLock allows reentrant locking

    def __new__(
        cls
    ) -> 'Container':
        """
        Creates and returns a singleton instance for each specific class in the inheritance hierarchy.

        This method implements a thread-safe singleton pattern that ensures each class
        in the Container inheritance hierarchy maintains its own singleton instance.
        Uses double-checked locking to prevent race conditions while maintaining
        performance through optimized access patterns.

        Returns
        -------
        Container
            The singleton instance of the requesting class.

        Notes
        -----
        - Thread-safe implementation prevents race conditions across multiple threads
        - Each class in the inheritance hierarchy maintains its own singleton instance
        - Double-checked locking optimizes performance for concurrent access
        - Memory visibility is guaranteed through proper synchronization
        """

        # Fast path: check if instance exists without acquiring lock for performance
        if cls in cls._instances:
            return cls._instances[cls]

        # Slow path: acquire lock for thread-safe instance creation
        with cls._lock:

            # Double-check pattern: verify instance wasn't created by another thread
            # while waiting for lock acquisition
            if cls in cls._instances:
                return cls._instances[cls]

            # Create new instance using parent's __new__ method to maintain inheritance
            instance = super(Container, cls).__new__(cls)

            # Store instance in class-specific dictionary with memory barrier protection
            cls._instances[cls] = instance

            # Return the newly created singleton instance
            return instance

    def __init__(
        self
    ) -> None:
        """
        Initialize the container's internal state.

        Sets up the main data structures for dependency injection and ensures
        initialization occurs only once per instance.

        Returns
        -------
        None
            No return value.
        """

        # Prevent multiple initializations for singleton instances
        if not hasattr(self, '_Container__initialized'):

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
        *args,
        **kwargs
    ) -> Any:
        """
        Builds an instance of the provided type using auto-resolution.

        Parameters
        ----------
        type_ : Callable[..., Any]
            The class to instantiate.
        *args : tuple
            Positional arguments to pass to the constructor.
        **kwargs : dict
            Keyword arguments to pass to the constructor.

        Returns
        -------
        Any
            The instantiated object.

        Raises
        ------
        OrionisContainerException
            If the type cannot be auto-resolved.
        """

        # Check if the type can be auto-resolved by the container
        if not self.__canAutoResolveClass(type_):

            # Raise an exception if the type cannot be auto-resolved
            raise OrionisContainerException(
                f"Type '{getattr(type_, '__name__', str(type_))}' cannot be auto-resolved by the container."
            )

        # Attempt to auto-resolve the type with provided arguments
        return self.__autoResolveClass(type_, *args, **kwargs)

    def invoke(
        self,
        fn: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Invokes a callable with automatic dependency injection and handles both sync and async callables.

        Parameters
        ----------
        fn : Callable
            The callable to invoke. Must not be a class/type.
        *args : tuple
            Positional arguments for the callable.
        **kwargs : dict
            Keyword arguments for the callable.

        Returns
        -------
        Any
            The result of the callable execution, with dependencies injected.
        """

        # Validate that fn is a callable and not a class/type
        if not callable(fn) or isinstance(fn, type):
            raise OrionisContainerException(
                f"Provided fn '{getattr(fn, '__name__', str(fn))}' must be a function or callable, not a class/type."
            )

        # Automatically resolve dependencies and execute the callable
        return self.__autoResolveCallable(fn, *args, **kwargs)

    def getBinding(
        self,
        abstract_or_alias: Any
    ) -> Optional[Binding]:
        """
        Retrieve the binding for a given abstract type or alias.

        Parameters
        ----------
        abstract_or_alias : Any
            Abstract class, interface, or alias to look up.

        Returns
        -------
        Optional[Binding]
            The associated binding if found, otherwise None.
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
        abstract_or_alias: Any,
    ) -> bool:
        """
        Check if a service is registered in the container.

        Parameters
        ----------
        abstract_or_alias : Any
            Abstract class, interface, or alias to check.

        Returns
        -------
        bool
            True if the service is registered, False otherwise.

        Notes
        -----
        Validates both bindings and aliases.
        """

        # Check if the abstract type or alias exists in bindings or aliases
        return abstract_or_alias in self.__bindings or abstract_or_alias in self.__aliases

    def drop( #NOSONAR
        self,
        abstract: Callable[..., Any] = None,
        alias: str = None
    ) -> bool:
        """
        Removes a service registration from the container by abstract type or alias.

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
        alias: str = None,
        enforce_decoupling: bool = False
    ) -> Optional[bool]:
        """
        Registers a service with transient lifetime.

        Binds a concrete implementation to an abstract base type or interface. Each request
        creates a new instance. Validates types, enforces decoupling, checks abstract method
        implementation, and manages aliases.

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
            raise OrionisContainerTypeError(
                f"Expected an abstract class extending 'abc.ABC' for 'abstract', but got '{abstract.__name__}' which is not an abstract base class."
            )

        # Validate that concrete is a concrete class
        if not Reflection.isConcreteClass(concrete):
            raise OrionisContainerTypeError(
                f"Expected a concrete class for 'concrete', but got abstract class or interface '{concrete.__name__}' instead."
            )

        # Enforce decoupling or subclass relationship
        self.__decouplingCheck(abstract, concrete, enforce_decoupling)

        # Ensure all abstract methods are implemented
        self.__implementsAbstractMethods(
            abstract=abstract,
            concrete=concrete
        )

        # Generate and validate the alias key
        alias = self.__makeAliasKey(abstract, alias)

        # Remove any existing binding for this abstract or alias
        self.drop(abstract, alias)

        # Register the service with transient lifetime
        self.__bindings[abstract] = Binding(
            contract = abstract,
            concrete = concrete,
            lifetime = Lifetime.TRANSIENT,
            enforce_decoupling = enforce_decoupling,
            alias = alias
        )

        # Register the alias for lookup
        self.__aliases[alias] = self.__bindings[abstract]

        # Registration successful
        return True

    def instance(
        self,
        abstract: Callable[..., Any],
        instance: Any,
        *,
        alias: str = None,
        enforce_decoupling: bool = False
    ) -> Optional[bool]:
        """
        Registers an instance with singleton lifetime for an abstract type or interface.

        Validates the abstract type and instance, enforces decoupling if specified, and ensures
        all abstract methods are implemented. Registers the instance under both the abstract and alias.

        Parameters
        ----------
        abstract : Callable[..., Any]
            Abstract class or interface to associate with the instance.
        instance : Any
            Concrete instance to register.
        alias : str, optional
            Alias to register the instance under. If not provided, a default alias is generated.
        enforce_decoupling : bool, optional
            If True, instance's class must not inherit from abstract. If False, must inherit.

        Returns
        -------
        bool or None
            True if registration succeeds, None if an exception occurs.

        Raises
        ------
        OrionisContainerTypeError
            If abstract is not an abstract class or instance is not valid.
        OrionisContainerException
            If decoupling check fails or abstract methods are not implemented.
        """

        # Validate that abstract is an abstract class
        if not Reflection.isAbstract(abstract):
            raise OrionisContainerTypeError(
                f"Expected an abstract class extending 'abc.ABC' for 'abstract', but got '{abstract.__name__}' which is not an abstract base class."
            )

        # Validate that instance is a valid object
        if not Reflection.isInstance(instance):
            raise OrionisContainerTypeError(
                f"Expected a valid instance for 'instance', but got type '{type(instance).__name__}' instead."
            )

        # Enforce decoupling or subclass relationship as specified
        self.__decouplingCheck(abstract, instance.__class__, enforce_decoupling)

        # Ensure all abstract methods are implemented by the instance
        self.__implementsAbstractMethods(
            abstract=abstract,
            instance=instance
        )

        # Generate and validate the alias key
        alias = self.__makeAliasKey(abstract, alias)

        # Remove any existing binding for this abstract or alias
        self.drop(abstract, alias)

        # Register the instance with singleton lifetime
        self.__bindings[abstract] = Binding(
            contract = abstract,
            instance = instance,
            lifetime = Lifetime.SINGLETON,
            enforce_decoupling = enforce_decoupling,
            alias = alias
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
        alias: str = None,
        enforce_decoupling: bool = False
    ) -> Optional[bool]:
        """
        Registers a service with singleton lifetime.

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

        Notes
        -----
        Registers the concrete implementation to the abstract type with singleton lifetime.
        Removes any previous binding for the same abstract or alias.
        Validates types, decoupling, and method implementation.
        """

        # Validate that abstract is an abstract class
        if not Reflection.isAbstract(abstract):
            raise OrionisContainerTypeError(
                f"Expected an abstract class extending 'abc.ABC' for 'abstract', but got '{abstract.__name__}' which is not an abstract base class."
            )

        # Validate that concrete is a concrete class
        if not Reflection.isConcreteClass(concrete):
            raise OrionisContainerTypeError(
                f"Expected a concrete class for 'concrete', but got abstract class or interface '{concrete.__name__}' instead."
            )

        # Enforce decoupling or subclass relationship
        self.__decouplingCheck(abstract, concrete, enforce_decoupling)

        # Ensure all abstract methods are implemented
        self.__implementsAbstractMethods(
            abstract=abstract,
            concrete=concrete
        )

        # Generate and validate the alias key
        alias = self.__makeAliasKey(abstract, alias)

        # Remove any existing binding for this abstract or alias
        self.drop(abstract, alias)

        # Register the service with singleton lifetime
        self.__bindings[abstract] = Binding(
            contract = abstract,
            concrete = concrete,
            lifetime = Lifetime.SINGLETON,
            enforce_decoupling = enforce_decoupling,
            alias = alias
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
        alias: str = None,
        enforce_decoupling: bool = False
    ) -> Optional[bool]:
        """
        Registers a service with scoped lifetime.

        Binds a concrete implementation to an abstract base type or interface, ensuring a new instance is created for each scope context. Validates types, enforces decoupling, checks abstract method implementation, and manages aliases.

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
            raise OrionisContainerTypeError(
                f"Expected an abstract class extending 'abc.ABC' for 'abstract', but got '{abstract.__name__}' which is not an abstract base class."
            )

        # Validate that concrete is a concrete class
        if not Reflection.isConcreteClass(concrete):
            raise OrionisContainerTypeError(
                f"Expected a concrete class for 'concrete', but got abstract class or interface '{concrete.__name__}' instead."
            )

        # Enforce decoupling or subclass relationship
        self.__decouplingCheck(abstract, concrete, enforce_decoupling)

        # Ensure all abstract methods are implemented
        self.__implementsAbstractMethods(
            abstract=abstract,
            concrete=concrete
        )

        # Generate and validate the alias key
        alias = self.__makeAliasKey(abstract, alias)

        # Remove any existing binding for this abstract or alias
        self.drop(abstract, alias)

        # Register the service with scoped lifetime
        self.__bindings[abstract] = Binding(
            contract = abstract,
            concrete = concrete,
            lifetime = Lifetime.SCOPED,
            enforce_decoupling = enforce_decoupling,
            alias = alias
        )

        # Register the alias for lookup
        self.__aliases[alias] = self.__bindings[abstract]

        # Registration successful
        return True

    def scopedInstance(
        self,
        abstract: Callable[..., Any],
        instance: Any,
        *,
        alias: str = None,
        enforce_decoupling: bool = False
    ) -> Optional[bool]:
        """
        Registers an instance with scoped lifetime for an abstract type or interface.

        Parameters
        ----------
        abstract : Callable[..., Any]
            Abstract class or interface to associate with the instance.
        instance : Any
            Instance to register.
        alias : str, optional
            Alias for registration. If not provided, a default alias is generated.
        enforce_decoupling : bool, optional
            If True, instance's class must not inherit from abstract.

        Returns
        -------
        bool or None
            True if registration succeeds, None if an exception occurs.

        Raises
        ------
        OrionisContainerTypeError
            If abstract is not an abstract class or alias is invalid.
        OrionisContainerException
            If instance is not valid, fails decoupling, or no scope is active.

        Notes
        -----
        Registers the instance with scoped lifetime, available only in the current scope.
        Removes any previous binding for the same abstract or alias.
        """

        # Ensure that the abstract is an abstract class
        if not Reflection.isAbstract(abstract):
            raise OrionisContainerTypeError(
                f"Expected an abstract class extending 'abc.ABC' for 'abstract', but got '{abstract.__name__}' which is not an abstract base class."
            )

        # Ensure that the instance is a valid instance of the abstract
        if not Reflection.isInstance(instance):
            raise OrionisContainerException(
                f"Instance of type '{instance.__class__.__name__}' is not a valid implementation of the abstract class '{abstract.__name__}'."
            )

        # Enforce decoupling or subclass relationship as specified
        self.__decouplingCheck(abstract, instance.__class__, enforce_decoupling)

        # Ensure all abstract methods are implemented by the instance
        self.__implementsAbstractMethods(
            abstract=abstract,
            instance=instance
        )

        # Validate and generate the alias key (either provided or default)
        alias = self.__makeAliasKey(abstract, alias)

        # Remove any existing binding for this abstract or alias
        self.drop(abstract, alias)

        # Register the instance with scoped lifetime in the container bindings
        self.__bindings[abstract] = Binding(
            contract=abstract,
            instance=instance,
            lifetime=Lifetime.SCOPED,
            enforce_decoupling=enforce_decoupling,
            alias=alias
        )

        # Register the alias for lookup
        self.__aliases[alias] = self.__bindings[abstract]

        # Store the instance directly in the current scope, if a scope is active
        scope = ScopedContext.getCurrentScope()
        if scope:
            scope[abstract] = instance
            scope[alias] = scope[abstract]

        # Return True to indicate successful registration
        return True

    def callable(
        self,
        fn: Callable[..., Any],
        *,
        alias: str
    ) -> Optional[bool]:
        """
        Registers a callable (function or factory) under a unique alias with transient lifetime.

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
        Registers the function with transient lifetime. Removes any previous registration under the same alias.
        """

        # Validate and normalize the alias using the internal alias key generator
        alias = self.__makeAliasKey(lambda: None, alias)

        # Ensure the provided fn is actually callable
        if not callable(fn):
            raise OrionisContainerTypeError(
                f"Expected a callable type, but got {type(fn).__name__} instead."
            )

        # Remove any existing registration under this alias
        self.drop(None, alias)

        # Register the function in the bindings dictionary with transient lifetime
        self.__bindings[alias] = Binding(
            function=fn,
            lifetime=Lifetime.TRANSIENT,
            alias=alias
        )

        # Register the alias for lookup in the aliases dictionary
        self.__aliases[alias] = self.__bindings[alias]

        # Return True to indicate successful registration
        return True

    def createScope(
        self
    ) -> ScopeManager:
        """
        Create a new scope context manager for scoped services.

        Returns
        -------
        ScopeManager
            Context manager for scoped service lifecycles.
        """

        # Return a new ScopeManager instance for context management
        return ScopeManager()

    def make(
        self,
        type_: Any,
        *args: tuple,
        **kwargs: dict
    ) -> Any:
        """
        Resolves and instantiates a service or type.

        Attempts to resolve the requested service or type from the container. If registered,
        resolves according to its binding and lifetime. If not registered but is a class,
        tries auto-resolution. Raises an exception if resolution fails.

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

        # Try to resolve from registered bindings first
        if self.bound(type_):
            # Resolve using the container's binding and lifetime rules
            return self.resolve(
                self.getBinding(type_),
                *args,
                **kwargs
            )

        # If not registered, try auto-resolution for classes
        if isinstance(type_, type):
            # Attempt to construct the class and resolve its dependencies recursively
            return self.build(
                type_,
                *args,
                **kwargs
            )

        # If all attempts fail, raise an exception indicating resolution failure
        raise OrionisContainerException(
            f"Cannot resolve service '{getattr(type_, '__name__', str(type_))}': it is not registered in the container and cannot be auto-resolved. "
            "Please ensure the service is registered or provide all required dependencies."
        )

    def resolve(
        self,
        binding: Binding,
        *args,
        **kwargs
    ) -> Any:
        """
        Resolves an instance from a binding according to its lifetime.

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
            The resolved instance.

        Raises
        ------
        OrionisContainerException
            If the binding is not a Binding or the lifetime is unsupported.
        """

        # Validate that binding is a Binding instance
        if not isinstance(binding, Binding):
            raise OrionisContainerException(
                f"Expected a Binding instance, got {type(binding).__name__}"
            )

        # Resolve based on the lifetime type:

        # Transient: always create a new instance
        if binding.lifetime == Lifetime.TRANSIENT:
            return self.__resolveTransient(binding, *args, **kwargs)

        # Singleton: return the cached instance or create one if needed
        elif binding.lifetime == Lifetime.SINGLETON:
            return self.__resolveSingleton(binding, *args, **kwargs)

        # Scoped: return the instance from the current scope or create one
        elif binding.lifetime == Lifetime.SCOPED:
            return self.__resolveScoped(binding, *args, **kwargs)

    def __resolveTransient(
        self,
        binding: Binding,
        *args,
        **kwargs
    ) -> Any:
        """
        Resolves a service registered with transient lifetime.

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
            A new instance of the requested service.

        Raises
        ------
        OrionisContainerException
            If no concrete class or function is defined for the binding.
        """

        # If a concrete class is defined, resolve and instantiate it
        if binding.concrete:
            return self.__autoResolveClass(binding.concrete, *args, **kwargs)

        # If a function is defined, resolve and invoke it
        elif binding.function:
            return self.__autoResolveCallable(binding.function, *args, **kwargs)

        # If neither is defined, raise an exception
        else:
            raise OrionisContainerException(
                f"Cannot resolve transient binding for '{binding.contract or binding.alias}': no concrete class or function defined."
            )

    def __resolveSingleton(
        self,
        binding: Binding,
        *args,
        **kwargs
    ) -> Any:
        """
        Resolves a service registered with singleton lifetime.

        Parameters
        ----------
        binding : Binding
            The binding to resolve.
        *args : tuple
            Positional arguments for the constructor (used only if instance does not exist).
        **kwargs : dict
            Keyword arguments for the constructor (used only if instance does not exist).

        Returns
        -------
        Any
            The singleton instance associated with the binding.

        Raises
        ------
        OrionisContainerException
            If no concrete class, instance, or function is defined for the binding.
        """

        # Return the cached singleton instance if it exists
        if binding.alias in self.__singleton_cache:
            return self.__singleton_cache[binding.alias]

        # If a pre-registered instance is present, cache and return it
        if binding.instance is not None:
            self.__singleton_cache[binding.alias] = binding.instance
            return self.__singleton_cache[binding.alias]

        # If a concrete class is specified, create and cache the instance
        if binding.concrete:
            instance = self.__autoResolveClass(binding.concrete, *args, **kwargs)
            self.__singleton_cache[binding.alias] = instance
            return instance

        # Raise an exception if the binding cannot be resolved
        raise OrionisContainerException(
            f"Cannot resolve singleton binding for '{binding.contract or binding.alias}': no concrete class or instance defined."
        )

    def __resolveScoped(
        self,
        binding: Binding,
        *args,
        **kwargs
    ) -> Any:
        """
        Resolves a service registered with scoped lifetime.

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
            The resolved instance from the current scope.

        Raises
        ------
        OrionisContainerException
            If no scope is active or the service cannot be resolved.
        """

        # Get the current scope context
        scope = ScopedContext.getCurrentScope()

        # Raise if there is no active scope
        if scope is None:
            raise OrionisContainerException(
                f"No active scope for scoped service '{binding.alias}'. Use 'with app.createScope()'."
            )

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
        raise OrionisContainerException(
            f"Cannot resolve scoped binding for '{binding.contract or binding.alias}': no implementation or instance defined."
        )

    def __makeAliasKey(
        self,
        abstract: Callable[..., Any],
        alias: str = None
    ) -> str:
        """
        Generates a unique alias key for service registration.

        Parameters
        ----------
        abstract : Callable[..., Any]
            Abstract base class or interface for alias generation.
        alias : str, optional
            Custom alias string.

        Returns
        -------
        str
            Validated custom alias or default alias in 'module.ClassName' format.

        Raises
        ------
        OrionisContainerTypeError
            If alias is invalid.
        """

        # Define forbidden characters for alias strings
        invalid_chars = set(' \t\n\r\x0b\x0c!@#$%^&*()[]{};:,/<>?\\|`~"\'')

        # If a custom alias is provided, validate it
        if alias:

            # Check for None, empty, or whitespace-only alias
            if alias is None or alias == "" or str(alias).isspace():
                raise OrionisContainerTypeError(
                    "Alias cannot be None, empty, or whitespace only."
                )

            # Ensure alias is a string
            if not isinstance(alias, str):
                raise OrionisContainerTypeError(
                    f"Expected a string type for alias, but got {type(alias).__name__} instead."
                )

            # Check for invalid characters in alias
            if any(char in invalid_chars for char in alias):
                raise OrionisContainerTypeError(
                    f"Alias '{alias}' contains invalid characters."
                )

            # Return validated custom alias
            return alias

        # Generate default alias from abstract class module and name
        return f"{abstract.__module__}.{abstract.__name__}"

    def __autoResolveClass(
        self,
        type_: Callable[..., Any],
        *args,
        **kwargs
    ) -> Any:
        """
        Automatically resolves and instantiates a class, injecting dependencies.

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
            raise OrionisContainerCircularDependencyException(
                f"Circular dependency detected while resolving argument '{type_key}'."
            )

        try:
            # Mark type as being resolved
            self.__resolution_cache.add(type_key)

            # Get constructor dependencies using reflection
            dependencies = ReflectionConcrete(type_).constructorSignature()

            # If no dependencies, instantiate directly
            if dependencies.hasNoDependencies():
                return type_(*args, **kwargs)

            # Resolve dependencies recursively
            final_args, final_kwargs = self.__resolveSignature(dependencies, *args, **kwargs)

            # Instantiate with resolved arguments
            return type_(*final_args, **final_kwargs)

        finally:

            # Clean up resolution cache
            self.__resolution_cache.discard(type_key)

    def __autoResolveCallable(
        self,
        type_: Callable[..., Any],
        *args,
        **kwargs
    ) -> Any:
        """
        Automatically resolves and invokes a callable, injecting dependencies.

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
        final_args, final_kwargs = self.__resolveSignature(dependencies, *args, **kwargs)

        # Invoke the callable with resolved arguments
        return self.__callAndResolve(type_, *final_args, **final_kwargs)

    def __callAndResolve(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Executes a function, handling both synchronous and asynchronous results.

        Parameters
        ----------
        func : Callable
            The function to execute (sync or async).
        *args
            Positional arguments for the function.
        **kwargs
            Keyword arguments for the function.

        Returns
        -------
        Any
            The final result, either the direct return value or the awaited coroutine.
        """

        # Execute the function with provided arguments
        result = func(*args, **kwargs)

        # If the result is not a coroutine, return it directly
        if not asyncio.iscoroutine(result):
            return result

        # Handle asynchronous result
        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()

            # If the loop is running, execute the coroutine in a new thread
            if loop.is_running():
                import concurrent.futures

                # Function to run the coroutine in a new event loop
                def run_coroutine():
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
        *args,
        **kwargs
    ) -> Tuple[List[Any], Dict[str, Any]]:
        """
        Resolves constructor or callable arguments using provided values and container bindings.

        Parameters
        ----------
        arguments : SignatureArguments
            Signature object containing argument metadata.
        *args : tuple
            Positional arguments for the target.
        **kwargs : dict
            Keyword arguments for the target.

        Returns
        -------
        tuple
            A tuple containing:
                - List[Any]: resolved positional arguments.
                - Dict[str, Any]: resolved keyword arguments.
        """

        # Copy kwargs to avoid mutating the original dictionary
        remaining_kwargs = dict(kwargs)

        # Use deque for efficient positional argument handling
        positional = deque(args)

        # Prepare containers for resolved arguments
        final_args = []
        final_kwargs = {}

        # Iterate over arguments in definition order
        for name, dep in arguments.items():

            # Check if argument is keyword-only
            is_keyword_only = dep.is_keyword_only

            # Handle positional or positional-or-keyword arguments
            if not is_keyword_only:

                # Resolve from container by type if bound and not provided as keyword
                if self.bound(dep.type) and name not in remaining_kwargs:
                    final_args.append(self.resolve(self.getBinding(dep.type)))
                    continue

                # Resolve from container by full class path if bound and not provided as keyword
                if self.bound(dep.full_class_path) and name not in remaining_kwargs:
                    final_args.append(self.resolve(self.getBinding(dep.full_class_path)))
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
                final_args.append(self.__resolveArgument(dep))

            else:

                # Use provided keyword argument if available
                if name in remaining_kwargs:
                    final_kwargs[name] = remaining_kwargs[name]
                    del remaining_kwargs[name]
                    continue

                # Resolve keyword-only argument from container by type
                if self.bound(dep.type):
                    final_kwargs[name] = self.resolve(self.getBinding(dep.type))
                    continue

                # Resolve keyword-only argument from container by full class path
                if self.bound(dep.full_class_path):
                    final_kwargs[name] = self.resolve(self.getBinding(dep.full_class_path))
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
        argument: Argument
    ) -> Any:
        """
        Resolves a single argument dependency for auto-resolution.

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
        """

        # Define list of special modules that cannot be auto-resolved
        special_modules = ['typing', 'builtins']

        # Check if argument is already resolved in the current scoped context
        scoped = ScopedContext.getCurrentScope()
        if scoped and (argument.type in scoped or argument.full_class_path in scoped):
            return scoped[argument.type] if argument.type in scoped else scoped[argument.full_class_path]

        # Return default value if argument is resolved and belongs to special modules or has default
        if (argument.resolved and argument.module_name in special_modules) or (argument.resolved and argument.default is not None):
            return argument.default

        # Raise exception for unresolvable built-in or typing types
        if (not argument.resolved and argument.module_name in special_modules):
            raise OrionisContainerException(
                f"Cannot resolve '{argument.name}' of type '{argument.module_name}'. Provide a default value."
            )

        # Attempt resolution using the argument type if bound in container
        if self.bound(argument.type):
            return self.resolve(self.getBinding(argument.type))

        # Attempt resolution using the full class path if bound in container
        if self.bound(argument.full_class_path):
            return self.resolve(self.getBinding(argument.full_class_path))

        # Try auto-resolution if the type is eligible
        if self.__canAutoResolveClass(argument.type):
            return self.__autoResolveClass(argument.type)

        # If all resolution methods fail, raise exception
        raise OrionisContainerException(
            f"Cannot resolve '{argument.name}' of type '{argument.module_name}'. Provide a default value."
        )

    def __canAutoResolveClass(
        self,
        type_: Callable[..., Any]
    ) -> bool:
        """
        Determines whether a type is eligible for automatic resolution by the container.

        Parameters
        ----------
        type_ : Callable[..., Any]
            The type to evaluate for auto-resolution eligibility.

        Returns
        -------
        bool
            True if the type can be automatically resolved, False otherwise.
        """

        # Check if the type is a concrete class (not abstract, not interface)
        if not Reflection.isConcreteClass(type_):
            return False

        # Check if the type is defined in the __main__ module (not eligible for auto-resolution)
        if type_.__module__ == '__main__':
            return False

        # If all checks pass, the type is eligible for auto-resolution
        return True

    def __decouplingCheck(
        self,
        abstract: Callable[..., Any],
        concrete: Callable[..., Any],
        enforce_decoupling: bool
    ) -> None:
        """
        Validates the inheritance relationship between abstract and concrete classes.

        Parameters
        ----------
        abstract : Callable[..., Any]
            Abstract base class or interface.
        concrete : Callable[..., Any]
            Concrete implementation class.
        enforce_decoupling : bool
            If True, concrete must not inherit from abstract. If False, concrete must inherit from abstract.

        Returns
        -------
        None
            No return value.

        Raises
        ------
        OrionisContainerException
            If inheritance relationship does not match the decoupling requirement.
        """

        # If decoupling is enforced, concrete must not inherit from abstract
        if enforce_decoupling:

            # Raise exception if concrete inherits from abstract
            if issubclass(concrete, abstract):
                raise OrionisContainerException(
                    "Concrete class must not inherit from the abstract class."
                )

        # If inheritance is required, concrete must inherit from abstract
        else:

            # Raise exception if concrete does not inherit from abstract
            if not issubclass(concrete, abstract):
                raise OrionisContainerException(
                    "Concrete class must inherit from the abstract class."
                )

    def __implementsAbstractMethods(
        self,
        *,
        abstract: Callable[..., Any] = None,
        concrete: Callable[..., Any] = None,
        instance: Any = None
    ) -> None:
        """
        Validates that all abstract methods in an abstract class are implemented by a concrete class or instance.

        Parameters
        ----------
        abstract : Callable[..., Any]
            Abstract base class with abstract methods.
        concrete : Callable[..., Any], optional
            Concrete class to check for method implementation.
        instance : Any, optional
            Instance to check for method implementation.

        Returns
        -------
        None
            Raises exception if validation fails.

        Raises
        ------
        OrionisContainerException
            If validation fails or required methods are not implemented.
        """

        # Ensure the abstract class is provided
        if abstract is None:
            raise OrionisContainerException("Abstract class must be provided for implementation check.")

        # Get reflection for the abstract class
        rf_abstract = ReflectionAbstract(abstract)

        # Get all abstract methods to be implemented
        abstract_methods = rf_abstract.getMethods()
        if not abstract_methods:
            raise OrionisContainerException(
                f"Abstract class '{abstract.__name__}' has no abstract methods."
            )

        # Select the target class or instance for validation
        target = concrete if concrete is not None else instance
        if target is None:
            raise OrionisContainerException("Either concrete class or instance must be provided for implementation check.")

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
        not_implemented = []
        for method in abstract_methods:
            if method not in implemented_methods:
                not_implemented.append(method)

        # Raise exception if any abstract methods are not implemented
        if not_implemented:
            methods = ", ".join(not_implemented)
            raise OrionisContainerException(
                f"Class '{target_name}' must implement the following abstract methods from '{abstract_name}': {methods}"
            )

    def call(
        self,
        instance: Any,
        method_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Invokes a method on an instance with automatic dependency injection.

        Parameters
        ----------
        instance : Any
            The object instance containing the method to invoke.
        method_name : str
            Name of the method to call on the instance.
        *args : tuple
            Positional arguments to pass to the method.
        **kwargs : dict
            Keyword arguments to pass to the method.

        Returns
        -------
        Any
            The result of the method invocation with dependencies resolved.

        Raises
        ------
        OrionisContainerException
            If the method is not found or is not callable.
        """

        # Retrieve the method from the instance using its name
        method = getattr(instance, method_name)

        # Ensure the method exists on the instance
        if method is None:
            raise OrionisContainerException(
                f"Method '{method_name}' not found in instance of type '{type(instance).__name__}'."
            )

        # Verify that the retrieved attribute is callable
        if not callable(method):
            raise OrionisContainerException(
                f"Attribute '{method_name}' of instance '{type(instance).__name__}' is not callable."
            )

        # Invoke the method with automatic dependency resolution
        return self.__autoResolveCallable(method, *args, **kwargs)