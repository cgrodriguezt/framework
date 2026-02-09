from __future__ import annotations
from orionis.container.providers.service_provider import ServiceProvider
from orionis.services.log.contracts.log_service import ILogger
from orionis.services.log.log_service import Logger
from orionis.support.facades.logger import Log as LoggerFacade

class LoggerProvider(ServiceProvider):

    def register(self) -> None:
        """
        Register the Logger service implementation in the application container.

        Bind the `Logger` class to the `ILogger` contract within the application's
        dependency injection container. Retrieve the logging configuration from the
        application, create a `Logger` instance using this configuration, and
        register it with an alias for internal framework identification.

        Returns
        -------
        None
            No return value. Performs service registration as a side effect on the
            application container.
        """
        # Register Logger as singleton with ILogger contract and framework alias
        self.app.singleton(
            ILogger,
            Logger,
            alias="x-orionis.services.log.contracts.log_service.ILogger",
        )

    async def boot(self) -> None:
        """
        Initialize the logging system after all services are registered.

        This method retrieves the logging configuration from the application,
        creates a Logger instance with this configuration, and initializes the
        Logger service. Ensures the logging system is ready after all providers
        have been registered.

        Returns
        -------
        None
            This method does not return a value. It performs initialization as a
            side effect.
        """
        # Initialize the logging system using the facade.
        await LoggerFacade.init()