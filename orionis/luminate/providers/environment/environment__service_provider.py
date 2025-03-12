from orionis.luminate.contracts.services.environment.environment_service import IEnvironmentService
from orionis.luminate.providers.service_provider import ServiceProvider
from orionis.luminate.services.environment.environment_service import EnvironmentService
from orionis.luminate.services.files.path_resolver_service import PathResolverService

class EnvironmentServiceProvider(ServiceProvider):

    def register(self) -> None:
        """
        Registers services or bindings into the given container.
        """
        self.app.singleton(IEnvironmentService, EnvironmentService)

    def boot(self) -> None:
        """
        Boot the service provider.

        This method is intended to be overridden by subclasses to perform
        any necessary bootstrapping or initialization tasks.
        """
        self.app.make(IEnvironmentService)