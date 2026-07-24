from __future__ import annotations
from orionis.container.providers.service_provider import ServiceProvider
from orionis.database.connection_manager import ConnectionManager
from orionis.database.contracts.manager import IConnectionManager
from orionis.orm.resolver import ConnectionResolver
from orionis.support.facades.db import DB

class DatabaseProvider(ServiceProvider):
    """
    Service provider for the Orionis database and ORM systems.

    Binds :class:`IConnectionManager` to :class:`ConnectionManager` as a
    singleton, installs the manager on the ORM connection resolver so
    models can query without container lookups, and pins the :class:`DB`
    facade for direct attribute access.
    """

    def register(self) -> None:
        """
        Bind IConnectionManager to ConnectionManager as a singleton.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.app.singleton(IConnectionManager, ConnectionManager)

    async def boot(self) -> None:
        """
        Wire the ORM resolver and pin the DB facade after registration.

        Returns
        -------
        None
            This method does not return a value.
        """
        manager = await self.app.make(IConnectionManager)
        # Install the manager so models resolve connections statically.
        ConnectionResolver.setManager(manager)
        await DB.pin()
