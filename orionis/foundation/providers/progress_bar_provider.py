from __future__ import annotations
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.container.providers.service_provider import ServiceProvider
from orionis.console.contracts.progress_bar import IProgressBar
from orionis.console.dynamic.progress_bar import ProgressBar

class ProgressBarProvider(ServiceProvider, DeferrableProvider):

    def register(self) -> None:
        """
        Register the progress bar service in the application container.

        Registers the `IProgressBar` interface to its concrete implementation,
        `ProgressBar`, using transient lifetime management. The service is
        registered with a specific alias for identification and retrieval.
        Transient lifetime ensures a new instance of `ProgressBar` is created
        each time the `IProgressBar` interface is resolved.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. It registers the service as a
            side effect on the application container.
        """
        # Bind ProgressBar as a transient service for IProgressBar with an alias.
        self.app.transient(
            IProgressBar,
            ProgressBar,
            alias="x-orionis.console.contracts.progress_bar.IProgressBar",
        )

    def provides(self) -> list[type]:
        """
        Specify the services provided by this provider.

        Returns a list of service types that this provider is responsible for.
        Indicates that the provider offers the `IProgressBar` service.

        Parameters
        ----------
        None

        Returns
        -------
        list of type
            A list containing the `IProgressBar` type, indicating that this provider
            supplies the implementation for that interface.
        """
        # Return the list of provided service types.
        return [IProgressBar]
