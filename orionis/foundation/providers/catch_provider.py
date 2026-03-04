from __future__ import annotations
from orionis.container.providers.service_provider import ServiceProvider
from orionis.failure.catch import Catch
from orionis.failure.contracts.catch import ICatch

class CathcProvider(ServiceProvider):

    def register(self) -> None:
        """
        Register the Catch service as a singleton in the application container.

        Parameters
        ----------
        self : CathcProvider
            The instance of the CathcProvider class.

        Returns
        -------
        None
            This method does not return a value. It registers the Catch service
            as a singleton in the application container.

        Notes
        -----
        Binds the `ICatch` interface to the `Catch` implementation as a singleton,
        using a specific alias. Ensures only one instance of `Catch` is created
        and shared throughout the application's lifecycle.
        """
        self.app.singleton(
            abstract=ICatch,
            concrete=Catch,
            alias="x-orionis.failure.contracts.catch.ICatch",
        )
