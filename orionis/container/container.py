from typing import Any, Callable
from orionis.container.entities.binding import Binding
from orionis.container.enums.lifetimes import Lifetime
from orionis.container.exceptions.container_exception import OrionisContainerException
from orionis.container.exceptions.type_error_exception import OrionisContainerTypeError
from orionis.services.introspection.abstract.reflection_abstract import ReflectionAbstract
from orionis.services.introspection.callables.reflection_callable import ReflectionCallable
from orionis.services.introspection.concretes.reflection_concrete import ReflectionConcrete
from orionis.services.introspection.instances.reflection_instance import ReflectionInstance
from orionis.services.introspection.reflection import Reflection
import inspect
import threading

class Container:

    # Singleton instance of the container.
    # This is a class variable that holds the single instance of the Container class.
    _instance = None

    # Lock for thread-safe singleton instantiation.
    # This lock ensures that only one thread can create the instance at a time,
    # preventing
    _lock = threading.Lock()

    # Class variable to track if the container has been initialized.
    # This is used to ensure that the initialization logic runs only once,
    # regardless of how many times the class is instantiated.
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """
        Creates and returns a singleton instance of the class.

        This method implements the singleton pattern, ensuring that only one instance
        of the class exists. If an instance does not exist, it acquires a lock to
        ensure thread safety and creates the instance. Subsequent calls return the
        existing instance.
        Parameters
        ----------
        *args : tuple
            Variable length argument list.
        **kwargs : dict
            Arbitrary keyword arguments.
        Returns
        -------
        Container
            The singleton instance of the class.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Container, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes a new instance of the container.

        This constructor sets up the internal dictionaries for bindings and aliases,
        ensuring that these are only initialized once per class. The initialization
        is guarded by the `_initialized` class attribute to prevent redundant setup.

        Notes
        -----
        - The `__bindings` dictionary is used to store service bindings.
        - The `__aliasses` dictionary is used to store service aliases.
        - Initialization occurs only once per class, regardless of the number of instances.
        """
        if not self.__class__._initialized:
            self.__bindings = {}
            self.__aliasses = {}
            self.__class__._initialized = True

    def __dropService(
        self,
        abstract: Callable[..., Any] = None,
        alias: str = None
    ) -> None:
        """
        Drops a service from the container.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract type or interface to be removed.
        alias : str, optional
            The alias of the service to be removed. If not provided, the service will be removed by its abstract type.

        Raises
        ------
        OrionisContainerException
            If the service does not exist in the container.
        """

        # If abstract is provided
        if abstract:

            # Remove the abstract service from the bindings if it exists
            if abstract in self.__bindings:
                del self.__bindings[abstract]

            # Remove the default alias (module + class name) from aliases if it exists
            abs_alias = ReflectionAbstract(abstract).getModuleWithClassName()
            if abs_alias in self.__aliasses:
                del self.__aliasses[abs_alias]

        # If a custom alias is provided
        if alias:

            # Remove it from the aliases dictionary if it exists
            if alias in self.__aliasses:
                del self.__aliasses[alias]

            # Remove the binding associated with the alias
            if alias in self.__bindings:
                del self.__bindings[alias]

    def __ensureIsCallable(
        self,
        value: Any
    ) -> None:
        """
        Ensures that the provided value is callable.

        Parameters
        ----------
        value : Any
            The value to check.

        Raises
        ------
        OrionisContainerTypeError
            If the value is not callable.
        """

        if not callable(value):
            raise OrionisContainerTypeError(
                f"Expected a callable type, but got {type(value).__name__} instead."
            )

    def __ensureAliasType(
        self,
        value: Any
    ) -> None:
        """
        Ensures that the provided value is a valid alias of type str and does not contain invalid characters.

        Parameters
        ----------
        value : Any
            The value to check.

        Raises
        ------
        OrionisContainerTypeError
            If the value is not of type str or contains invalid characters.

        Notes
        -----
        This method validates that a given value is a string and does not contain characters
        that could cause errors when resolving dependencies (e.g., whitespace, special symbols).
        """

        # Check if the value is a string
        if not isinstance(value, str):
            raise OrionisContainerTypeError(
                f"Expected a string type for alias, but got {type(value).__name__} instead."
            )

        # Define a set of invalid characters for aliases
        invalid_chars = set(' \t\n\r\x0b\x0c!@#$%^&*()[]{};:,/<>?\\|`~"\'')
        if any(char in invalid_chars for char in value):
            raise OrionisContainerTypeError(
                f"Alias '{value}' contains invalid characters. "
                "Aliases must not contain whitespace or special symbols."
            )

    def __ensureAbstractClass(
        self,
        abstract: Callable[..., Any],
        lifetime: str
    ) -> None:
        """
        Ensures that the provided abstract is an abstract class.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The class intended to represent the abstract type.
        lifetime : str
            The service lifetime descriptor, used for error messages.

        Raises
        ------
        OrionisContainerTypeError
            If the abstract class check fails.
        """
        try:
            ReflectionAbstract.ensureIsAbstractClass(abstract)
        except Exception as e:
            raise OrionisContainerTypeError(
                f"Unexpected error registering {lifetime} service: {e}"
            ) from e

    def __ensureConcreteClass(
        self,
        concrete: Callable[..., Any],
        lifetime: str
    ) -> None:
        """
        Ensures that the provided concrete is a concrete (non-abstract) class.

        Parameters
        ----------
        concrete : Callable[..., Any]
            The class intended to represent the concrete implementation.
        lifetime : str
            The service lifetime descriptor, used for error messages.

        Raises
        ------
        OrionisContainerTypeError
            If the concrete class check fails.
        """
        try:
            ReflectionConcrete.ensureIsConcreteClass(concrete)
        except Exception as e:
            raise OrionisContainerTypeError(
                f"Unexpected error registering {lifetime} service: {e}"
            ) from e

    def __ensureIsSubclass(
        self,
        abstract: Callable[..., Any],
        concrete: Callable[..., Any]
    ) -> None:
        """
        Validates that the concrete class is a subclass of the provided abstract class.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract base class or interface.
        concrete : Callable[..., Any]
            The concrete implementation class to check.

        Raises
        ------
        OrionisContainerException
            If the concrete class is NOT a subclass of the abstract class.

        Notes
        -----
        This method ensures that the concrete implementation inherits from the abstract class,
        which is required for proper dependency injection and interface enforcement.
        """
        if not issubclass(concrete, abstract):
            raise OrionisContainerException(
                "The concrete class must inherit from the provided abstract class. "
                "Please ensure that the concrete class is a subclass of the specified abstract class."
            )

    def __ensureIsNotSubclass(
        self,
        abstract: Callable[..., Any],
        concrete: Callable[..., Any]
    ) -> None:
        """
        Validates that the concrete class is NOT a subclass of the provided abstract class.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract base class or interface.
        concrete : Callable[..., Any]
            The concrete implementation class to check.

        Raises
        ------
        OrionisContainerException
            If the concrete class IS a subclass of the abstract class.

        Notes
        -----
        This method ensures that the concrete implementation does NOT inherit from the abstract class.
        """
        if issubclass(concrete, abstract):
            raise OrionisContainerException(
                "The concrete class must NOT inherit from the provided abstract class. "
                "Please ensure that the concrete class is not a subclass of the specified abstract class."
            )

    def __ensureInstance(
        self,
        instance: Any
    ) -> None:
        """
        Ensures that the provided object is a valid instance.

        Parameters
        ----------
        instance : Any
            The object to be validated as an instance.

        Raises
        ------
        OrionisContainerTypeError
            If the provided object is not a valid instance.

        Notes
        -----
        This method uses ReflectionInstance to verify that the given object
        is a proper instance (not a class or abstract type). If the check fails,
        an OrionisContainerTypeError is raised with a descriptive message.
        """
        try:
            ReflectionInstance.ensureIsInstance(instance)
        except Exception as e:
            raise OrionisContainerTypeError(
                f"Error registering instance: {e}"
            ) from e

    def __ensureImplementation(
        self,
        *,
        abstract: Callable[..., Any] = None,
        concrete: Callable[..., Any] = None,
        instance: Any = None
    ) -> None:
        """
        Ensures that a concrete class or instance implements all abstract methods defined in an abstract class.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract class containing abstract methods.
        concrete : Callable[..., Any], optional
            The concrete class that should implement the abstract methods.
        instance : Any, optional
            The instance that should implement the abstract methods.

        Raises
        ------
        OrionisContainerException
            If the concrete class or instance does not implement all abstract methods defined in the abstract class.

        Notes
        -----
        This method checks that all abstract methods in the given abstract class are implemented
        in the provided concrete class or instance. If any methods are missing, an exception is raised with
        details about the missing implementations.
        """
        if abstract is None:
            raise OrionisContainerException("Abstract class must be provided for implementation check.")

        abstract_methods = getattr(abstract, '__abstractmethods__', set())
        if not abstract_methods:
            raise OrionisContainerException(
                f"The abstract class '{abstract.__name__}' does not define any abstract methods. "
                "An abstract class must have at least one abstract method."
            )

        target = concrete if concrete is not None else instance
        if target is None:
            raise OrionisContainerException("Either concrete class or instance must be provided for implementation check.")

        target_class = target if Reflection.isClass(target) else target.__class__
        target_name = target_class.__name__
        abstract_name = abstract.__name__

        not_implemented = []
        for method in abstract_methods:
            if not hasattr(target, str(method).replace(f"_{abstract_name}", f"_{target_name}")):
                not_implemented.append(method)

        if not_implemented:
            formatted_methods = "\n  • " + "\n  • ".join(not_implemented)
            raise OrionisContainerException(
                f"'{target_name}' does not implement the following abstract methods defined in '{abstract_name}':{formatted_methods}\n"
                "Please ensure that all abstract methods are implemented."
            )

    def transient(
        self,
        abstract: Callable[..., Any],
        concrete: Callable[..., Any],
        *,
        alias: str = None,
        enforce_decoupling: bool = False
    ) -> bool:
        """
        Registers a service with a transient lifetime.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract base type or interface to be bound.
        concrete : Callable[..., Any]
            The concrete implementation to associate with the abstract type.
        alias : str, optional
            An alternative name to register the service under. If not provided, the abstract's class name is used.

        Returns
        -------
        bool
            True if the service was registered successfully.

        Raises
        ------
        OrionisContainerTypeError
            If the abstract or concrete class checks fail.
        OrionisContainerException
            If the concrete class inherits from the abstract class.

        Notes
        -----
        Registers the given concrete implementation to the abstract type with a transient lifetime,
        meaning a new instance will be created each time the service is requested. Optionally, an alias
        can be provided for registration.
        """

        # Ensure that abstract is an abstract class
        self.__ensureAbstractClass(abstract, Lifetime.TRANSIENT)

        # Ensure that concrete is a concrete class
        self.__ensureConcreteClass(concrete, Lifetime.TRANSIENT)

        # Ensure that concrete is NOT a subclass of abstract
        if enforce_decoupling:
            self.__ensureIsNotSubclass(abstract, concrete)

        # Validate that concrete is a subclass of abstract
        else:
            self.__ensureIsSubclass(abstract, concrete)

        # Ensure implementation
        self.__ensureImplementation(
            abstract=abstract,
            concrete=concrete
        )

        # Ensure that the alias is a valid string if provided
        if alias:
            self.__ensureAliasType(alias)

        # Extract the module and class name for the alias
        else:
            rf_asbtract = ReflectionAbstract(abstract)
            alias = rf_asbtract.getModuleWithClassName()

        # If the service is already registered, drop it
        self.__dropService(abstract, alias)

        # Register the service with transient lifetime
        self.__bindings[abstract] = Binding(
            contract = abstract,
            concrete = concrete,
            lifetime = Lifetime.TRANSIENT,
            enforce_decoupling = enforce_decoupling,
            alias = alias
        )

        # Register the alias
        self.__aliasses[alias] = self.__bindings[abstract]

        # Return True to indicate successful registration
        return True

    def singleton(
        self,
        abstract: Callable[..., Any],
        concrete: Callable[..., Any],
        *,
        alias: str = None,
        enforce_decoupling: bool = False
    ) -> bool:
        """
        Registers a service with a singleton lifetime.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract base type or interface to be bound.
        concrete : Callable[..., Any]
            The concrete implementation to associate with the abstract type.
        alias : str, optional
            An alternative name to register the service under. If not provided, the abstract's class name is used.

        Returns
        -------
        bool
            True if the service was registered successfully.

        Raises
        ------
        OrionisContainerTypeError
            If the abstract or concrete class checks fail.
        OrionisContainerException
            If the concrete class inherits from the abstract class.

        Notes
        -----
        Registers the given concrete implementation to the abstract type with a singleton lifetime,
        meaning a single instance will be created and shared. Optionally, an alias can be provided for registration.
        """

        # Ensure that abstract is an abstract class
        self.__ensureAbstractClass(abstract, Lifetime.SINGLETON)

        # Ensure that concrete is a concrete class
        self.__ensureConcreteClass(concrete, Lifetime.SINGLETON)

        # Ensure that concrete is NOT a subclass of abstract
        if enforce_decoupling:
            self.__ensureIsNotSubclass(abstract, concrete)

        # Validate that concrete is a subclass of abstract
        else:
            self.__ensureIsSubclass(abstract, concrete)

        # Ensure implementation
        self.__ensureImplementation(
            abstract=abstract,
            concrete=concrete
        )

        # Ensure that the alias is a valid string if provided
        if alias:
            self.__ensureAliasType(alias)
        else:
            rf_asbtract = ReflectionAbstract(abstract)
            alias = rf_asbtract.getModuleWithClassName()

        # If the service is already registered, drop it
        self.__dropService(abstract, alias)

        # Register the service with singleton lifetime
        self.__bindings[abstract] = Binding(
            contract = abstract,
            concrete = concrete,
            lifetime = Lifetime.SINGLETON,
            enforce_decoupling = enforce_decoupling,
            alias = alias
        )

        # Register the alias
        self.__aliasses[alias] = self.__bindings[abstract]

        # Return True to indicate successful registration
        return True

    def scoped(
        self,
        abstract: Callable[..., Any],
        concrete: Callable[..., Any],
        *,
        alias: str = None,
        enforce_decoupling: bool = False
    ) -> bool:
        """
        Registers a service with a scoped lifetime.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract base type or interface to be bound.
        concrete : Callable[..., Any]
            The concrete implementation to associate with the abstract type.
        alias : str, optional
            An alternative name to register the service under. If not provided, the abstract's class name is used.

        Returns
        -------
        bool
            True if the service was registered successfully.

        Raises
        ------
        OrionisContainerTypeError
            If the abstract or concrete class checks fail.
        OrionisContainerException
            If the concrete class inherits from the abstract class.

        Notes
        -----
        Registers the given concrete implementation to the abstract type with a scoped lifetime,
        meaning a new instance will be created per scope. Optionally, an alias can be provided for registration.
        """

        # Ensure that abstract is an abstract class
        self.__ensureAbstractClass(abstract, Lifetime.SCOPED)

        # Ensure that concrete is a concrete class
        self.__ensureConcreteClass(concrete, Lifetime.SCOPED)

        # Ensure that concrete is NOT a subclass of abstract
        if enforce_decoupling:
            self.__ensureIsNotSubclass(abstract, concrete)

        # Validate that concrete is a subclass of abstract
        else:
            self.__ensureIsSubclass(abstract, concrete)

        # Ensure implementation
        self.__ensureImplementation(
            abstract=abstract,
            concrete=concrete
        )

        # Ensure that the alias is a valid string if provided
        if alias:
            self.__ensureAliasType(alias)
        else:
            rf_asbtract = ReflectionAbstract(abstract)
            alias = rf_asbtract.getModuleWithClassName()

        # If the service is already registered, drop it
        self.__dropService(abstract, alias)

        # Register the service with scoped lifetime
        self.__bindings[abstract] = Binding(
            contract = abstract,
            concrete = concrete,
            lifetime = Lifetime.SCOPED,
            enforce_decoupling = enforce_decoupling,
            alias = alias
        )

        # Register the alias
        self.__aliasses[alias] = self.__bindings[abstract]

        # Return True to indicate successful registration
        return True

    def instance(
        self,
        abstract: Callable[..., Any],
        instance: Any,
        *,
        alias: str = None,
        enforce_decoupling: bool = False
    ) -> bool:
        """
        Registers an instance of a class or interface in the container.
        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract class or interface to associate with the instance.
        instance : Any
            The concrete instance to register.
        alias : str, optional
            An optional alias to register the instance under. If not provided,
            the abstract's `__name__` attribute will be used as the alias if available.
        Returns
        -------
        bool
            True if the instance was successfully registered.
        Raises
        ------
        TypeError
            If `abstract` is not an abstract class or if `alias` is not a valid string.
        ValueError
            If `instance` is not a valid instance of `abstract`.
        Notes
        -----
        This method ensures that the abstract is a valid abstract class, the instance
        is valid, and the alias (if provided) is a valid string. The instance is then
        registered in the container under both the abstract and the alias.
        """

        # Ensure that the abstract is an abstract class
        self.__ensureAbstractClass(abstract, f"Instance {Lifetime.SINGLETON}")

        # Ensure that the instance is a valid instance
        self.__ensureInstance(instance)

        # Ensure that instance is NOT a subclass of abstract
        if enforce_decoupling:
            self.__ensureIsNotSubclass(abstract, instance.__class__)

        # Validate that instance is a subclass of abstract
        else:
            self.__ensureIsSubclass(abstract, instance.__class__)

        # Ensure implementation
        self.__ensureImplementation(
            abstract=abstract,
            instance=instance
        )

        # Ensure that the alias is a valid string if provided
        if alias:
            self.__ensureAliasType(alias)
        else:
            rf_asbtract = ReflectionAbstract(abstract)
            alias = rf_asbtract.getModuleWithClassName()

        # If the service is already registered, drop it
        self.__dropService(abstract, alias)

        # Register the instance with the abstract type
        self.__bindings[abstract] = Binding(
            contract = abstract,
            instance = instance,
            lifetime = Lifetime.SINGLETON,
            enforce_decoupling = enforce_decoupling,
            alias = alias
        )

        # Register the alias
        self.__aliasses[alias] = self.__bindings[abstract]

        # Return True to indicate successful registration
        return True

    def function(
        self,
        alias: str,
        function: Callable[..., Any],
        *,
        lifetime: Lifetime = Lifetime.TRANSIENT
    ) -> bool:
        """
        Registers a function or factory under a given alias.

        Parameters
        ----------
        alias : str
            The alias to register the function under.
        function : Callable[..., Any]
            The function or factory to register.
        lifetime : Lifetime, optional
            The lifetime of the function registration (default is TRANSIENT).

        Returns
        -------
        bool
            True if the function was registered successfully.

        Raises
        ------
        OrionisContainerTypeError
            If the alias is invalid or the function is not callable.
        OrionisContainerException
            If the lifetime is not allowed for the function signature.
        """
        # Normalize and validate the lifetime parameter
        if not isinstance(lifetime, Lifetime):
            if isinstance(lifetime, str):
                lifetime_key = lifetime.strip().upper()
                if lifetime_key in Lifetime.__members__:
                    lifetime = Lifetime[lifetime_key]
                else:
                    valid = ', '.join(Lifetime.__members__.keys())
                    raise OrionisContainerTypeError(
                        f"Invalid lifetime '{lifetime}'. Valid options are: {valid}."
                    )
            else:
                raise OrionisContainerTypeError(
                    f"Lifetime must be of type str or Lifetime enum, got {type(lifetime).__name__}."
                )

        # Ensure that the alias is a valid string
        self.__ensureAliasType(alias)

        # Validate that the function is callable
        self.__ensureIsCallable(function)

        # Inspect the function signature
        params = ReflectionCallable(function).getDependencies()

        # If the function requires arguments, only allow TRANSIENT
        if (len(params.resolved) + len(params.unresolved)) > 0 and lifetime != Lifetime.TRANSIENT:
            raise OrionisContainerException(
                "Functions that require arguments can only be registered with a TRANSIENT lifetime."
            )

        # If the service is already registered, drop it
        self.__dropService(None, alias)

        # Register the function with the specified alias and lifetime
        self.__bindings[alias] = Binding(
            function=function,
            lifetime=lifetime,
            alias=alias
        )

        # Register the function as a binding
        self.__aliasses[alias] = self.__bindings[alias]

        return True

    def bound(
        self,
        abstract_or_alias: Any,
    ) -> bool:
        """
        Checks if a service (by abstract type or alias) is registered in the container.

        Parameters
        ----------
        abstract_or_alias : Any
            The abstract class, interface, or alias (str) to check for registration.

        Returns
        -------
        bool
            True if the service is registered (either as an abstract type or alias), False otherwise.

        Notes
        -----
        This method allows you to verify whether a service has been registered in the container,
        either by its abstract type or by its alias. It supports both class-based and string-based lookups.
        """
        return (
            abstract_or_alias in self.__bindings
            or abstract_or_alias in self.__aliasses
        )

    def make(
        self,
        abstract_or_alias: Any,
        *args,
        **kwargs
    ) -> Any:
        """
        Resolves and returns an instance of the requested service.

        Parameters
        ----------
        abstract_or_alias : Any
            The abstract class, interface, or alias (str) to resolve.
        *args : tuple
            Positional arguments to pass to the constructor of the resolved service.
        **kwargs : dict
            Keyword arguments to pass to the constructor of the resolved service.

        Returns
        -------
        Any
            An instance of the requested service.

        Raises
        ------
        OrionisContainerException
            If the requested service is not registered in the container.
        """
        if not self.bound(abstract_or_alias):
            raise OrionisContainerException(
                f"The requested service '{abstract_or_alias}' is not registered in the container."
            )

        binding = self.__bindings.get(abstract_or_alias) or self.__aliasses.get(abstract_or_alias)

        print(binding)