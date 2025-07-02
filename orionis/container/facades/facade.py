from typing import Any
from orionis.container.container import Container

class FacadeMeta(type):

    def __getattr__(cls, name: str) -> Any:
        """
        When an undefined attribute is accessed, this method resolves the service and delegates the call.
        It's like having a genie in a bottle, but for services.

        Args:
            name: The name of the attribute to access

        Returns:
            The requested attribute from the underlying service
        """
        service = cls.resolve()
        if not hasattr(service, name):
            raise AttributeError(f"'{cls.__name__}' facade's service has no attribute '{name}'")
        return getattr(service, name)


class Facade(metaclass=FacadeMeta):

    # Container instance to resolve services
    _container = Container()

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Get the name of the service to be resolved from the container.
        This method must be overridden by subclasses to return the name of the service
        to be resolved. If not overridden, it raises NotImplementedError.
        Returns
        -------
        str
            The service name to be resolved from the container.
        Raises
        ------
        NotImplementedError
            If the method is not overridden by a subclass.
        """
        raise NotImplementedError(f"Class {cls.__name__} must define the getFacadeAccessor method")

    @classmethod
    def resolve(cls, *args, **kwargs) -> Any:
        """
        This method retrieves a service instance from the container using the facade accessor.
        If the service is not bound in the container, a RuntimeError is raised.
        Parameters
        ----------
        *args
            Positional arguments to pass to the service constructor.
        **kwargs
            Keyword arguments to pass to the service constructor.
        Returns
        -------
        Any
            The resolved service instance.
        Raises
        ------
        RuntimeError
            If the service is not bound in the container.
        Notes
        -----
        """

        # Get the service name from the facade accessor
        service_name = cls.getFacadeAccessor()

        # Check if the service is bound in the container
        if not cls._container.bound(service_name):
            raise RuntimeError(
                f"The service '{service_name}' is not bound in the container. "
                "Did you forget to register it?"
            )

        # Resolve the service instance from the container
        service_instance = cls._container.make(service_name, *args, **kwargs)
        return service_instance