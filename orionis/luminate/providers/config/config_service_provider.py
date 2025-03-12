from orionis.luminate.contracts.services.config.config_service import IConfigService
from orionis.luminate.providers.service_provider import ServiceProvider
from orionis.luminate.services.config.config_service import ConfigService

class ConfigServiceProvider(ServiceProvider):

    async def register(self) -> None:
        """
        Registers services or bindings into the given container.
        """
        await self.app.scoped(IConfigService, ConfigService)
