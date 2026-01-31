from orionis.container.providers.service_provider import ServiceProvider
from orionis.failure.contracts.catch import ICatch
from orionis.failure.catch import Catch

class CathcProvider(ServiceProvider):

    def register(self) -> None:
        """
        Register the Catch service as a singleton in the application container.

        Bind the `ICatch` interface to the `Catch` implementation as a singleton,
        using a specific alias. This ensures that only one instance of `Catch`
        is created and shared throughout the application's lifecycle.

        Returns
        -------
        None
            No return value. Performs registration as a side effect.
        """
        self.app.singleton(
            abstract=ICatch,
            concrete=Catch,
            alias="x-orionis.failure.contracts.catch.ICatch"
        )
