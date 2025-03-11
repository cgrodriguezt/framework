from orionis.luminate.contracts.services.files.path_resolver_service import IPathResolverService
from orionis.luminate.providers.service_provider import ServiceProvider
from orionis.luminate.services.files.path_resolver_service import PathResolverService

class PathResolverProvider(ServiceProvider):

    beferoBootstrapping = True

    def register(self) -> None:
        """
        Registers services or bindings into the given container.
        """
        self._container_id = self.app.singleton(IPathResolverService, PathResolverService)

    def boot(self) -> None:
        """
        Boot the service provider.

        This method is intended to be overridden by subclasses to perform
        any necessary bootstrapping or initialization tasks.
        """
        self.app.make(self._container_id)