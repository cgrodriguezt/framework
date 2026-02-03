from __future__ import annotations
from orionis.container.providers.service_provider import ServiceProvider
from orionis.services.log.contracts.log_service import ILogger
from orionis.services.log.log_service import Logger

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
