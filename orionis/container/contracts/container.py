from abc import ABC, abstractmethod
from typing import Any, Callable
from orionis.container.enums.lifetimes import Lifetime

class IContainer(ABC):
    """
    IContainer is an interface that defines the structure for a dependency injection container.
    It provides methods for registering and resolving services with different lifetimes.
    """

    @abstractmethod
    def singleton(
        self,
        abstract: Callable[..., Any],
        concrete: Callable[..., Any],
        *,
        alias: str = None,
        enforce_decoupling: bool = False
    ) -> bool:
        """
        Register a service as a singleton.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract base type or interface to be bound.
        concrete : Callable[..., Any]
            The concrete implementation to associate with the abstract type.
        alias : str, optional
            An alternative name to register the service under.
        enforce_decoupling : bool, optional
            Whether to enforce that concrete is not a subclass of abstract.

        Returns
        -------
        bool
            True if the service was registered successfully.
        """
        pass

    @abstractmethod
    def transient(
        self,
        abstract: Callable[..., Any],
        concrete: Callable[..., Any],
        *,
        alias: str = None,
        enforce_decoupling: bool = False
    ) -> bool:
        """
        Register a service as transient.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract base type or interface to be bound.
        concrete : Callable[..., Any]
            The concrete implementation to associate with the abstract type.
        alias : str, optional
            An alternative name to register the service under.
        enforce_decoupling : bool, optional
            Whether to enforce that concrete is not a subclass of abstract.

        Returns
        -------
        bool
            True if the service was registered successfully.
        """
        pass

    @abstractmethod
    def scoped(
        self,
        abstract: Callable[..., Any],
        concrete: Callable[..., Any],
        *,
        alias: str = None,
        enforce_decoupling: bool = False
    ) -> bool:
        """
        Register a service as scoped.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract base type or interface to be bound.
        concrete : Callable[..., Any]
            The concrete implementation to associate with the abstract type.
        alias : str, optional
            An alternative name to register the service under.
        enforce_decoupling : bool, optional
            Whether to enforce that concrete is not a subclass of abstract.

        Returns
        -------
        bool
            True if the service was registered successfully.
        """
        pass

    @abstractmethod
    def instance(
        self,
        abstract: Callable[..., Any],
        instance: Any,
        *,
        alias: str = None,
        enforce_decoupling: bool = False
    ) -> bool:
        """
        Register an instance of a service.

        Parameters
        ----------
        abstract : Callable[..., Any]
            The abstract class or interface to associate with the instance.
        instance : Any
            The concrete instance to register.
        alias : str, optional
            An optional alias to register the instance under.
        enforce_decoupling : bool, optional
            Whether to enforce that instance's class is not a subclass of abstract.

        Returns
        -------
        bool
            True if the instance was successfully registered.
        """
        pass

    @abstractmethod
    def function(
        self,
        alias: str,
        fn: Callable[..., Any],
        *,
        lifetime: Lifetime = Lifetime.TRANSIENT
    ) -> bool:
        """
        Register a function as a service.

        Parameters
        ----------
        alias : str
            The alias to register the function under.
        fn : Callable[..., Any]
            The function or factory to register.
        lifetime : Lifetime, optional
            The lifetime of the function registration (default is TRANSIENT).

        Returns
        -------
        bool
            True if the function was registered successfully.
        """
        pass

    @abstractmethod
    def make(
        self,
        abstract_or_alias: Any,
        *args: tuple,
        **kwargs: dict
    ) -> Any:
        """
        Resolve a service from the container.

        Parameters
        ----------
        abstract_or_alias : Any
            The abstract class, interface, or alias (str) to resolve.
        *args : tuple
            Positional arguments to pass to the constructor.
        **kwargs : dict
            Keyword arguments to pass to the constructor.

        Returns
        -------
        Any
            An instance of the requested service.
        """
        pass

    @abstractmethod
    def bound(
        self,
        abstract_or_alias: Any
    ) -> bool:
        """
        Check if a service is registered in the container.

        Parameters
        ----------
        abstract_or_alias : Any
            The abstract class, interface, or alias (str) to check.

        Returns
        -------
        bool
            True if the service is registered, False otherwise.
        """
        pass