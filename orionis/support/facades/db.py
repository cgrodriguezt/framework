from orionis.container.facades.facade import Facade
from orionis.database.contracts.manager import IConnectionManager


class DB(Facade):
    """
    Facade for the database connection manager.

    Proxies all calls to the bound :class:`IConnectionManager` singleton.

    Usage (facade pinned at boot)::

        connection = DB.connection()          # default connection
        connection = DB.connection("pgsql")   # named connection

        rows = await DB.connection().select(
            "SELECT * FROM users WHERE id = :id", {"id": 1},
        )

        async with DB.connection().transaction():
            ...
    """

    @classmethod
    def getFacadeAccessor(cls) -> type:
        """
        Return the container accessor for the connection manager.

        Returns
        -------
        type
            :class:`IConnectionManager`.
        """
        return IConnectionManager
