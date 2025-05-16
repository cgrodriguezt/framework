from orionis.luminate._contracts.services.config.config_service import IConfigService
from orionis.luminate._providers.service_provider import ServiceProvider
from orionis.luminate._services.config.config_service import ConfigService

class ConfigServiceProvider(ServiceProvider):

    def register(self) -> None:
        """
        Registers services or bindings into the given container.
        """
        self.app.scoped(IConfigService, ConfigService)
