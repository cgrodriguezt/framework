from __future__ import annotations
from orionis.http.contracts.route import IRoute
from orionis.http.routes.route import Route
from orionis.container.providers.service_provider import ServiceProvider

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
        self.app.singleton(
            abstract=IRoute,
            concrete=Route,
            alias="x-orionis.http.contracts.route.IRoute"
        )
