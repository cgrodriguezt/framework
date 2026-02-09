from __future__ import annotations
from orionis.console.request.contracts.cli_request import ICLIRequest
from orionis.console.request.cli_request import CLIRequest
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.container.providers.service_provider import ServiceProvider

class CLRequestProvider(ServiceProvider, DeferrableProvider):

    def register(self) -> None:
        """
        Register CLI request services in the application container.

        Registers the `ICLIRequest` interface to the `CLIRequest` implementation as a
        transient service. Each resolution of `ICLIRequest` yields a new `CLIRequest`
        instance. The binding uses a specific alias for container reference.

        Parameters
        ----------
        self : CLRequestProvider
            Instance of the provider.

        Returns
        -------
        None
            This method performs registration as a side effect and returns None.
        """
        # Bind ICLIRequest to CLIRequest as a transient service with a specific alias.
        self.app.transient(
            ICLIRequest,
            CLIRequest,
            alias="x-orionis.console.contracts.cli_request.ICLIRequest",
        )

    def provides(self) -> list[type]:
        """
        Specify the services provided by the CLRequestProvider.

        Indicate that this provider supplies the `ICLIRequest` service to the
        application container.

        Parameters
        ----------
        self : CLRequestProvider
            Instance of the provider.

        Returns
        -------
        list of type
            List containing the `ICLIRequest` type.
        """
        # Return the list of provided service types.
        return [ICLIRequest]
