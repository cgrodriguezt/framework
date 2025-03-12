from orionis.luminate.contracts.services.commands.reactor_commands_service import IReactorCommandsService
from orionis.luminate.providers.service_provider import ServiceProvider
from orionis.luminate.services.commands.reactor_commands_service import ReactorCommandsService

class ReactorCommandsServiceProvider(ServiceProvider):

    async def register(self) -> None:
        """
        Registers services or bindings into the given container.
        """
        await self.app.singleton(IReactorCommandsService, ReactorCommandsService)

    async def boot(self) -> None:
        """
        Boot the service provider.

        This method is intended to be overridden by subclasses to perform
        any necessary bootstrapping or initialization tasks.
        """
        await self.app.make(IReactorCommandsService)