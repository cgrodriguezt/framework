from orionis.luminate.contracts.services.log.log_service import ILogguerService
from orionis.luminate.providers.service_provider import ServiceProvider
from orionis.luminate.services.log.log_service import LogguerService

class LogServiceProvider(ServiceProvider):

    def register(self) -> None:
        """
        Registers services or bindings into the given container.
        """
        self.app.singleton(ILogguerService, LogguerService)

    def boot(self) -> None:
        """
        Boot the service provider.

        This method is intended to be overridden by subclasses to perform
        any necessary bootstrapping or initialization tasks.
        """
        self.app.make(ILogguerService)