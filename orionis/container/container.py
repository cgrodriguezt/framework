from typing import Any, Callable
from orionis.container.enums.lifetimes import Lifetime
from orionis.container.exceptions.container_exception import OrionisContainerException
from orionis.container.exceptions.type_error_exception import OrionisContainerTypeError
from orionis.services.introspection.abstract.reflection_abstract import ReflectionAbstract
from orionis.services.introspection.concretes.reflection_concrete import ReflectionConcrete
from orionis.services.introspection.instances.reflection_instance import ReflectionInstance
from orionis.services.introspection.reflection import Reflection

class Container:

    def __init__(self):
        self.__transient = {}
        self.__singleton = {}
        self.__scoped = {}
        self.__instance = {}

    def __ensureAliasType(self, value: Any) -> None:
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

    def __ensureAbstractClass(self, abstract: Callable[..., Any], lifetime: str) -> None:
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

    def __ensureConcreteClass(self, concrete: Callable[..., Any], lifetime: str) -> None:
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

    def __ensureIsSubclass(self, abstract: Callable[..., Any], concrete: Callable[..., Any]) -> None:
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

    def __ensureIsNotSubclass(self, abstract: Callable[..., Any], concrete: Callable[..., Any]) -> None:
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

    def __ensureInstance(self, instance: Any) -> None:
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

    def __ensureImplementation(self, *, abstract: Callable[..., Any] = None, concrete: Callable[..., Any] = None, instance: Any = None) -> None:
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

    def transient(self, abstract: Callable[..., Any], concrete: Callable[..., Any], alias: str = None, enforce_decoupling: bool = False) -> bool:
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

        if enforce_decoupling:
            # Ensure that concrete is NOT a subclass of abstract
            self.__ensureIsNotSubclass(abstract, concrete)
        else:
            # Validate that concrete is a subclass of abstract
            self.__ensureIsSubclass(abstract, concrete)

        # Ensure implementation
        self.__ensureImplementation(
            abstract=abstract,
            concrete=concrete
        )

        # Ensure that the alias is a valid string if provided
        if alias:
            self.__ensureAliasType(alias)

        # Register the service with transient lifetime
        self.__transient[abstract] = concrete

        # If an alias is provided, register it as well
        if alias:
            self.__transient[alias] = concrete
        elif hasattr(abstract, '__name__'):
            alias = abstract.__name__
            self.__transient[alias] = concrete

        # Return True to indicate successful registration
        return True

    def singleton(self, abstract: Callable[..., Any], concrete: Callable[..., Any], alias: str = None, enforce_decoupling: bool = False) -> bool:
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

        if enforce_decoupling:
            # Ensure that concrete is NOT a subclass of abstract
            self.__ensureIsNotSubclass(abstract, concrete)
        else:
            # Validate that concrete is a subclass of abstract
            self.__ensureIsSubclass(abstract, concrete)

        # Ensure implementation
        self.__ensureImplementation(
            abstract=abstract,
            concrete=concrete
        )

        # Ensure that the alias is a valid string if provided
        if alias:
            self.__ensureAliasType(alias)

        # Register the service with singleton lifetime
        self.__singleton[abstract] = concrete

        # If an alias is provided, register it as well
        if alias:
            self.__singleton[alias] = concrete
        elif hasattr(abstract, '__name__'):
            alias = abstract.__name__
            self.__singleton[alias] = concrete

        # Return True to indicate successful registration
        return True

    def scoped(self, abstract: Callable[..., Any], concrete: Callable[..., Any], alias: str = None, enforce_decoupling: bool = False) -> bool:
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

        if enforce_decoupling:
            # Ensure that concrete is NOT a subclass of abstract
            self.__ensureIsNotSubclass(abstract, concrete)
        else:
            # Validate that concrete is a subclass of abstract
            self.__ensureIsSubclass(abstract, concrete)

        # Ensure implementation
        self.__ensureImplementation(
            abstract=abstract,
            concrete=concrete
        )

        # Ensure that the alias is a valid string if provided
        if alias:
            self.__ensureAliasType(alias)

        # Register the service with scoped lifetime
        self.__scoped[abstract] = concrete

        # If an alias is provided, register it as well
        if alias:
            self.__scoped[alias] = concrete
        elif hasattr(abstract, '__name__'):
            alias = abstract.__name__
            self.__scoped[alias] = concrete

        # Return True to indicate successful registration
        return True

    def instance(self, abstract: Callable[..., Any], instance: Any, alias: str = None, enforce_decoupling: bool = False) -> bool:
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

        if enforce_decoupling:
            # Ensure that instance is NOT a subclass of abstract
            self.__ensureIsNotSubclass(abstract, instance.__class__)
        else:
            # Validate that instance is a subclass of abstract
            self.__ensureIsSubclass(abstract, instance.__class__)

        # Ensure implementation
        self.__ensureImplementation(
            abstract=abstract,
            instance=instance
        )

        # Ensure that the alias is a valid string if provided
        if alias:
            self.__ensureAliasType(alias)

        # Register the instance with the abstract type
        self.__instance[abstract] = instance

        # If an alias is provided, register it as well
        if alias:
            self.__instance[alias] = instance
        elif hasattr(abstract, '__name__'):
            alias = abstract.__name__
            self.__instance[alias] = instance

        # Return True to indicate successful registration
        return True

    def bind(self, concrete_instance_or_function, lifetime: str = Lifetime.TRANSIENT, alias: str = None) -> None:
        pass