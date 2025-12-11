from __future__ import annotations
from orionis.container.exceptions import (
    OrionisContainerAttributeError,
    OrionisContainerException,
)
from orionis.foundation.application import IApplication, Application
from typing import TypeVar

T = TypeVar("T")

class FacadeMeta(type):

    def __getattr__(cls, name: str) -> T:
        """
        Resolve the service and delegate attribute access.

        When an undefined attribute is accessed on the facade class, this method
        resolves the underlying service and returns the requested attribute from it.
        Raises an exception if the attribute does not exist.

        Parameters
        ----------
        name : str
            Name of the attribute to access.

        Returns
        -------
        T
            The requested attribute from the resolved service.

        Raises
        ------
        OrionisContainerAttributeError
            If the resolved service does not have the requested attribute.
        """
        # Resolve the underlying service instance from the container
        service = cls.resolve()

        # Check if the requested attribute exists on the service
        if not hasattr(service, name):
            error_msg = (
                f"'{cls.__name__}' facade's service has no attribute '{name}'"
            )
            raise OrionisContainerAttributeError(error_msg)

        # Return the requested attribute from the resolved service
        return getattr(service, name)

class Facade(metaclass=FacadeMeta):

    # Application instance to resolve services
    _app: IApplication = Application()

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Return the name of the service to resolve from the container.

        This method must be overridden by subclasses to specify the service name.
        If not overridden, it raises NotImplementedError.

        Returns
        -------
        str
            The name of the service to resolve.

        Raises
        ------
        NotImplementedError
            If the method is not overridden by a subclass.
        """
        # Raise an error if the subclass does not implement this method
        error_msg = (
            f"Class {cls.__name__} must define the getFacadeAccessor method"
        )
        raise NotImplementedError(error_msg)

    @classmethod
    def resolve(cls, *args: tuple, **kwargs: dict) -> object:
        """
        Retrieve a service instance from the container using the facade accessor.

        Ensures the application context is booted and the service is bound in the
        container before resolving. Raises an exception if the service cannot be
        resolved.

        Parameters
        ----------
        *args : tuple
            Positional arguments to pass to the service constructor.
        **kwargs : dict
            Keyword arguments to pass to the service constructor.

        Returns
        -------
        object
            The resolved service instance.

        Raises
        ------
        OrionisContainerException
            If the application is not booted or the service is not bound.
        """
        # Check if the application context is booted before resolving services
        if not cls._app.isBooted:
            error_msg = (
                f"Cannot resolve service '{cls.getFacadeAccessor()}' through the "
                f"{cls.__name__} facade. Facades require an active Orionis application "
                "context. Please ensure the application is properly booted before using"
                " facades, or access the service directly through the container."
            )
            raise OrionisContainerException(error_msg)

        # Get the service name from the facade accessor
        service_name = cls.getFacadeAccessor()

        # Check if the service is bound in the container
        if not cls._app.bound(service_name):
            error_msg = (
                f"Service '{service_name}' not bound in the container. Please ensure "
                f"'{service_name}' is registered in the container before using the "
                f"{cls.__name__} facade."
            )
            raise OrionisContainerException(error_msg)

        # Resolve and return the service instance from the container
        return cls._app.make(service_name, *args, **kwargs)
