from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

    from orionis.database.contracts.connection import IConnection


class IConnectionManager(ABC):
    """
    Contract for the database connection manager.

    The manager resolves the database configuration, registers named
    connection configurations, builds :class:`IConnection` objects on
    demand, caches them for reuse, and controls their lifecycle.
    """

    @abstractmethod
    def connection(self, name: str | None = None) -> IConnection:
        """
        Resolve the connection registered under the given name.

        The connection is built on first access and cached for reuse.

        Parameters
        ----------
        name : str or None, optional
            Connection name as declared in the database configuration,
            or ``None`` for the default connection.

        Returns
        -------
        IConnection
            Connection bound to its configuration.

        Raises
        ------
        ConnectionNotFoundException
            If the connection is not declared in the configuration.
        """

    @abstractmethod
    def addConnection(self, name: str, config: dict[str, Any]) -> None:
        """
        Register or replace a named connection configuration at runtime.

        A live connection built from a previous configuration keeps
        serving until :meth:`disconnect` is called for that name.

        Parameters
        ----------
        name : str
            Connection name to register.
        config : dict
            Driver configuration for the connection.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        ValueError
            If the name is empty or the configuration is not a mapping.
        """

    @abstractmethod
    def hasConnection(self, name: str) -> bool:
        """
        Report whether a connection configuration exists.

        Parameters
        ----------
        name : str
            Connection name to look up.

        Returns
        -------
        bool
            ``True`` when the configuration is registered.
        """

    @abstractmethod
    def getDefaultName(self) -> str:
        """
        Return the name of the default connection.

        Returns
        -------
        str
            Default connection name.
        """

    @abstractmethod
    def setDefaultName(self, name: str) -> None:
        """
        Change the default connection name.

        Parameters
        ----------
        name : str
            Name of a registered connection.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        ConnectionNotFoundException
            If the name is not registered.
        """

    @abstractmethod
    async def disconnect(self, name: str | None = None) -> None:
        """
        Dispose one or all cached connections.

        Parameters
        ----------
        name : str or None, optional
            Connection to dispose, or ``None`` to dispose every cached
            connection.

        Returns
        -------
        None
            This method does not return a value.
        """

    @abstractmethod
    def sqlAlchemyJobStore(
        self,
        name: str | None = None,
        *,
        tablename: str = "apscheduler_jobs",
    ) -> SQLAlchemyJobStore:
        """
        Build an APScheduler ``SQLAlchemyJobStore`` for a connection.

        APScheduler's ``SQLAlchemyJobStore`` always operates through a
        blocking SQLAlchemy engine, so the returned store is backed by a
        synchronous DBAPI driver rather than the async engine used by
        :meth:`connection`.

        Parameters
        ----------
        name : str or None, optional
            Connection name as declared in the database configuration,
            or ``None`` for the default connection.
        tablename : str, optional
            Name of the table used to persist scheduled jobs.

        Returns
        -------
        SQLAlchemyJobStore
            Job store bound to a synchronous engine for the connection.

        Raises
        ------
        ConnectionNotFoundException
            If the connection is not declared in the configuration.
        MissingDatabaseDependencyException
            If the synchronous driver package is not installed.
        """
