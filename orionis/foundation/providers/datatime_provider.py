from orionis.container.providers.service_provider import ServiceProvider
from orionis.support.time.contracts.datetime import IDateTime
from orionis.support.time.datetime import DateTime

class DataTimeProvider(ServiceProvider):

    def register(self) -> None:
        """
        Registers the DateTime service as a singleton in the application container.

        The service is registered with the IDateTime interface and an alias.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Register DateTime as a singleton for IDateTime with a specific alias
        self.app.singleton(
            IDateTime,
            DateTime,
            alias="x-orionis.support.time.contracts.datetime.IDateTime",
        )