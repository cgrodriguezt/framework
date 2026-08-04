from orionis.container.facades.facade import Facade
from orionis.database.contracts.manager import IConnectionManager
from orionis.orm.query.raw_builder import RawQueryBuilder


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

        users = await DB.table("users").where("active", True).get()
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

    @classmethod
    def table(
        cls,
        name: str,
        *,
        alias: str | None = None,
        connection: str | None = None,
    ) -> RawQueryBuilder:
        """
        Build a fluent, model-less query over a plain table name.

        A real classmethod, not a proxied attribute: it builds the
        builder directly instead of going through the dynamic facade
        dispatcher, since it never needs the pinned service itself (the
        builder resolves its own connection lazily via
        :class:`orionis.orm.resolver.ConnectionResolver` on its first
        terminal call).

        Parameters
        ----------
        name : str
            Logical table name, without the connection prefix.
        alias : str or None, optional
            Alias the table is referred to by inside the query.
        connection : str or None, optional
            Named connection to run the query against, or ``None`` for
            the default connection.

        Returns
        -------
        RawQueryBuilder
            Fluent, model-less query builder over the table.
        """
        return RawQueryBuilder(name, alias=alias, connection=connection)
