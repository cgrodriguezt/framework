from __future__ import annotations
from orionis.http.contracts.route import IRoute
from orionis.http.routes.route import Route
from orionis.container.providers.service_provider import ServiceProvider
from orionis.support.facades.router import Route as RouteFacade

class RouterProvider(ServiceProvider):

    def register(self) -> None:
        """
        Register the IRoute interface as a singleton in the application container.

        This method binds the IRoute contract to the Route implementation and
        assigns an alias for later resolution.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.app.singleton(IRoute, Route, alias="x-orionis-IRoute")

    async def boot(self) -> None:
        """
        Initialize the Route facade asynchronously during the boot process.

        This method ensures that the Route facade is properly initialized before
        handling requests.

        Returns
        -------
        None
            This method does not return a value.
        """
        await RouteFacade.init()
