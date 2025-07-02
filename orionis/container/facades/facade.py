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

    _container = Container()

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        This method must be overridden by subclasses to return the name of the service to be resolved.
        If not, it throws a tantrum (NotImplementedError).

        Returns:
            The service name to be resolved from the container
        """
        raise NotImplementedError(f"Class {cls.__name__} must define the getFacadeAccessor method")

    @classmethod
    def resolve(cls) -> Any:
        """
        Resolves the service from the Container with caching for improved performance.
        It's like calling the butler to fetch something from the pantry.

        Returns:
            The resolved service instance
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
        service_instance = cls._container.make(service_name)
        return service_instance