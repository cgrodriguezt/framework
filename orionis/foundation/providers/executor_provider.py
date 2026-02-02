from __future__ import annotations
from orionis.console.contracts.executor import IExecutor
from orionis.console.output.executor import Executor
from orionis.container.providers.service_provider import ServiceProvider
from orionis.container.providers.deferrable_provider import DeferrableProvider

class ConsoleExecuteProvider(ServiceProvider, DeferrableProvider):

    def register(self) -> None:
        """
        Register the console executor service in the application container.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method performs a side effect by binding the executor service.
        """
        # Bind IExecutor to Executor as a transient service for isolated execution.
        self.app.transient(
            IExecutor,
            Executor,
            alias="x-orionis.console.contracts.executor.IExecutor"
        )

    def provides(self) -> list[type]:
        """
        Specify the services provided by this service provider.

        Parameters
        ----------
        None

        Returns
        -------
        list of type
            List containing the types of services provided, here only IExecutor.
        """
        return [IExecutor]
