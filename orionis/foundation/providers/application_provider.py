from __future__ import annotations
from orionis.container.providers.service_provider import ServiceProvider
from orionis.support.facades.application import Application as ApplicationFacade

class ApplicationProvider(ServiceProvider):

    async def boot(self) -> None:
        """
        Initialize the application facade asynchronously.

        Calls the asynchronous initialization method of the ApplicationFacade.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Initialize the application facade
        await ApplicationFacade.init()
