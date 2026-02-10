from __future__ import annotations
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.container.providers.service_provider import ServiceProvider
from orionis.console.dynamic.contracts.progress_bar import IProgressBar
from orionis.console.dynamic.progress_bar import ProgressBar
from orionis.support.facades.progress_bar import ProgressBar as ProgressBarFacade

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

    async def boot(self) -> None:
        """
        Initialize the progress bar facade asynchronously.

        This method sets up the ProgressBarFacade by calling its init method.
        It is intended to be called during the application's bootstrapping
        phase to ensure the progress bar system is ready for use.

        Returns
        -------
        None
            This method does not return a value. It performs initialization as
            a side effect.
        """
        await ProgressBarFacade.init()
