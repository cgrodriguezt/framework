from orionis.container.contracts.container import IContainer
from orionis.container.entities.binding import Binding
from orionis.container.enums.lifetimes import Lifetime


class Resolver:
    """
    Resolver class for handling dependency resolution in the container.
    """

    def __init__(
        self,
        container:IContainer,
        lifetime:Lifetime
    ):
        self.container = container
        self.lifetime = lifetime

    def transient(
        self,
        binding:Binding,
        *args,
        **kwargs
    ):
        """
        Register a transient service.
        """
        return self.container.transient(service, implementation, **kwargs)
